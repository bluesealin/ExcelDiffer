#!/usr/bin/env python
# -*- coding:utf-8 -*-


def diff(dataBefore, dataAfter):
    """
    核心diff算法
    :param dataBefore: 二维数组数据
    :param dataAfter: 二维数组数据
    :return: 变化描述
    rowInfo 行增删
    colInfo 列增删
    celInfo 单元格修改
    """

    # 浅拷贝，使算法中的增删不影响原数据
    dataBefore = dataBefore[:]
    dataAfter = dataAfter[:]

    # 坐标对应关系，用于在最后计算出单元格修改后，找到原本的坐标
    mappingBefore = [[(i, j) for j in range(len(dataBefore[0]))]
                     for i in range(len(dataBefore))]
    mappingAfter = [[(i, j) for j in range(len(dataAfter[0]))]
                    for i in range(len(dataAfter))]

    # 步骤1：将最原始的数据直接进行diff，找出相同行
    # 考虑到列增删的影响，此处实际是相似度高的行判别为相同行
    # 相似度用最长公共子序列长度表征
    rowInfo = subdiff(dataBefore, dataAfter)

    # 步骤2：步骤1中以外的行，可以被视为是删除/增加的行，去除
    delCountBefore = 0
    delCountAfter = 0
    for info in rowInfo:
        diffType = info[0:1]
        if diffType == 'd':
            indexB = int(info[1:]) - delCountBefore
            del dataBefore[indexB]
            del mappingBefore[indexB]
            delCountBefore += 1
        elif diffType == 'a':
            indexA = int(info[1:]) - delCountAfter
            del dataAfter[int(indexA)]
            del mappingAfter[indexA]
            delCountAfter += 1

    # 步骤3：数据行列倒置，用于处理列的情况
    dataBefore = row2col(dataBefore)
    dataAfter = row2col(dataAfter)
    mappingBefore = row2col(mappingBefore)
    mappingAfter = row2col(mappingAfter)

    # 步骤4：倒置后的数据diff
    colInfo = subdiff(dataBefore, dataAfter)

    # 步骤5：再次根据结果删除，此时相当于删除了原数据中不同的列
    delCountBefore = 0
    delCountAfter = 0
    for info in colInfo:
        diffType = info[0:1]
        if diffType == 'd':
            indexB = int(info[1:]) - delCountBefore
            del dataBefore[indexB]
            del mappingBefore[indexB]
            delCountBefore += 1
        elif diffType == 'a':
            indexA = int(info[1:]) - delCountAfter
            del dataAfter[indexA]
            del mappingAfter[indexA]
            delCountAfter += 1

    # 步骤6 再次行列倒置
    dataBefore = row2col(dataBefore)
    dataAfter = row2col(dataAfter)
    mappingBefore = row2col(mappingBefore)
    mappingAfter = row2col(mappingAfter)

    # 步骤7 剩余数据找单元格修改
    cellInfo = []
    for row in range(len(dataBefore)):
        for col in range(len(dataBefore[0])):
            if dataBefore[row][col] != dataAfter[row][col]:
                info = []
                info.append(mappingBefore[row][col])
                info.append(mappingAfter[row][col])
                cellInfo.append(info)

    return rowInfo, colInfo, cellInfo


def subdiff(dataBefore, dataAfter):
    """
    diff子算法
    :param dataBefore: 修改前数据
    :param dataAfter: 修改后数据
    :return: 形如["s0:0", "d1", "a1"]的列表数据
    s前缀代表相同序列号，分号前后对应修改前后数据
    d前缀代表修改前数据删除的数据
    a前缀代表休后后数据增加的数据
    """
    indexBefore, indexAfter = longgestCommonSubsequence(dataBefore, dataAfter)
    info = []
    i = 0
    j = 0
    bLen = len(dataBefore)
    aLen = len(dataAfter)
    bIndex = 0
    aIndex = 0
    bIndexLen = len(indexBefore)
    aIndexLen = len(indexAfter)
    while i < bLen or j < aLen:
        if aIndex == aIndexLen and i < bLen:
            info.append("d%d" % i)
            i += 1
        elif bIndex == bIndexLen and j < aLen:
            info.append("a%d" % j)
            j += 1
        elif indexBefore[bIndex] == i and indexAfter[aIndex] == j:
            info.append("s%d:%s" % (i, j))
            i += 1
            j += 1
            bIndex += 1
            aIndex += 1
        elif indexBefore[bIndex] == i and indexAfter[aIndex] > j:
            info.append("a%d" % j)
            j += 1
        elif indexBefore[bIndex] > i and indexAfter[aIndex] == j:
            info.append("d%d" % i)
            i += 1
        else:
            while indexBefore[bIndex] > i:
                info.append("d%d" % i)
                i += 1
            while indexAfter[aIndex] > j:
                info.append("a%d" % j)
                j += 1

    return info


def longgestCommonSubsequence(a, b):
    """
    LCS算法，最长公共子序列
    :param a: 数据a
    :param b: 数据b
    :return: 返回两个数组，分别代表两个数据中公共子序列的小标值
    """
    aLen = len(a)
    bLen = len(b)
    dp = [[0 for i in range(bLen + 1)] for j in range(aLen + 1)]
    path = [[0 for i in range(bLen + 1)] for j in range(aLen + 1)]
    for i in range(aLen):
        for j in range(bLen):
            if equal(a[i], b[j]):
                dp[i + 1][j + 1] = dp[i][j] + 1
                path[i + 1][j + 1] = 1
            elif dp[i + 1][j] > dp[i][j + 1]:
                dp[i + 1][j + 1] = dp[i + 1][j]
                path[i + 1][j + 1] = -1
            else:
                dp[i + 1][j + 1] = dp[i][j + 1]
                path[i + 1][j + 1] = -2
    return calcSubsequenceIndex(path, a, b, aLen, bLen)


def equal(dataB, dataA):
    """
    计算两个数据是否相等
    :param dataB: 原数据
    :param dataA: 修改后数据
    :return: 数据a与b是否相等
    """
    if isinstance(dataB, list):
        # list类型判断是否有公共的子项
        # 用于在data是二维数据的情况
        setB = set(dataB)
        setA = set(dataA)
        setS = setB & setA
        return len(setS) > 0
    else:
        # 否则直接判断二者是否相等
        return dataB == dataA


def calcSubsequenceIndex(path, a, b, aIndex, bIndex):
    """
    递归方式计算公共子序列的下标值
    :param path: 路径信息dp二维数组
    :param a: 序列a
    :param b: 序列b
    :param aIndex: 当前所求序列a的下标值
    :param bIndex: 当前所求序列b的下标值
    :return: 对应两个公共子序列的下标值数组
    """
    if aIndex == 0 or bIndex == 0:
        return [], []
    if path[aIndex][bIndex] == 1:
        s1, s2 = calcSubsequenceIndex(path, a, b, aIndex - 1, bIndex - 1)
        s1.append(aIndex - 1)
        s2.append(bIndex - 1)
        return s1, s2
    elif path[aIndex][bIndex] == -1:
        return calcSubsequenceIndex(path, a, b, aIndex, bIndex - 1)
    else:
        return calcSubsequenceIndex(path, a, b, aIndex - 1, bIndex)


def row2col(data):
    """
    行列转置函数
    :param data: 原数据
    :return: 转置后数据
    """
    return map(list, zip(*data))


if __name__ == '__main__':
    import xlrd
    firstExcel = xlrd.open_workbook('test/testExcel1.xlsx')
    secondExcel = xlrd.open_workbook('test/testExcel2.xlsx')
    sheetInFirst = firstExcel.sheet_by_index(0)
    sheetInSecond = secondExcel.sheet_by_index(0)
    firstData = []
    for row in range(sheetInFirst.nrows):
        partData = []
        for col in range(sheetInFirst.ncols):
            partData.append(sheetInFirst.cell_value(row, col))
        firstData.append(partData)
    secondData = []
    for row in range(sheetInSecond.nrows):
        partData = []
        for col in range(sheetInSecond.ncols):
            partData.append(sheetInSecond.cell_value(row, col))
        secondData.append(partData)
    diff(firstData, secondData)
