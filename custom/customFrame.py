#!/usr/bin/env python
# -*- coding:utf-8 -*-

import wx
import wx.lib.filebrowsebutton as filebrowse
import xlrd

from customPanel import SameSheetPanel, SheetPanel


class MainFrame(wx.Frame):
    """
    程序主窗口
    """
    def __init__(self):
        screenSize = wx.DisplaySize()
        frmWidth = screenSize[0] / 2
        frmHeight = screenSize[1] / 2
        frmPos = (screenSize[0] / 8, screenSize[1] / 8)
        wx.Frame.__init__(self, None, title="ExcelDiffer", pos=frmPos,
                          size=(frmWidth + 100, frmHeight + 200))

        self.excelFilePaths = ['', '']
        self.firstFileButton = filebrowse.FileBrowseButton(self, -1,
                pos=(20, 20), labelText="第一个Excel文件",
                buttonText="选择", fileMask="*.xlsx", size=(600, -1))
        self.secondFileButton = filebrowse.FileBrowseButton(self, -1,
                pos=(20, 60), labelText="第二个Excel文件",
                buttonText="选择", fileMask="*.xlsx", size=(600, -1))
        self.diffButton = wx.Button(self, -1, "开始比对", (20, 100))
        self.Bind(wx.EVT_BUTTON, self.Diff, self.diffButton)
        self.Show()

    def Diff(self, event):
        """
        点击"开始对比"按钮后触发的函数，计算diff数据并在窗口中展示
        :param event:
        :return:
        """
        self.excelFilePaths[0] = self.firstFileButton.GetValue()
        self.excelFilePaths[1] = self.secondFileButton.GetValue()
        if '' in self.excelFilePaths:
            dlg = wx.MessageDialog(self, "请选择两个Excel文件", "温馨提示", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        firstExcel = xlrd.open_workbook(self.excelFilePaths[0])
        secondExcel = xlrd.open_workbook(self.excelFilePaths[1])
        self.typeNB = wx.Notebook(self, -1, pos=(20, 120), size=(700, 450))
        sameSheets, diffSheets = self.calcSheet(firstExcel, secondExcel)
        self.typeNB.commonSheets = sameSheets
        self.typeNB.diffSheets = diffSheets
        samePanel = SameSheetPanel(self.typeNB, firstExcel,
                                   secondExcel, sameSheets)
        onlyInFirstPanel = SheetPanel(self.typeNB, self.excelFilePaths[0],
                                      firstExcel, diffSheets[0])
        onlyInSecondPanel = SheetPanel(self.typeNB, self.excelFilePaths[1],
                                       secondExcel, diffSheets[1])
        self.typeNB.AddPage(samePanel, "相同sheet")
        self.typeNB.AddPage(onlyInFirstPanel, "第一个文件独有sheet")
        self.typeNB.AddPage(onlyInSecondPanel, "第二个文件独有sheet")

    def calcSheet(self, firstExcel, secondExcel):
        """
        计算两个Excel文件中sheet表情况，得出相同名称的sheet表和单独的sheet表
        :param firstExcel:
        :param secondExcel:
        :return:
        """
        firstSheets = firstExcel.sheet_names()
        secondSheets = secondExcel.sheet_names()
        commonSheets = []
        onlyInFirst = []
        onlyInSecond = []
        for sheet in firstSheets:
            if sheet in secondSheets:
                commonSheets.append(sheet)
            else:
                onlyInFirst.append(sheet)
        for sheet in secondSheets:
            if sheet not in commonSheets:
                onlyInSecond.append(sheet)
        return commonSheets, [onlyInFirst, onlyInSecond]