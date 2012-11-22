import wx

from wxHelpers import *
from DateTimePickerCtrl import DateTimePickerCtrl
from DbComboBox import DbComboBox
from Grid import *

import Resource
import Format

class Purchase(wx.Panel):
    Logic = None

    def __init__(self, parent, logic):
        wx.Panel.__init__(self, parent)

        self.Logic = logic

        self._GlueEventCallbacks()

        self._InitCtrls()

        self._GlueLogic()

        self.Logic.Start()
        self.cbSuppliers.SetSelection(0)
        self.cbTaxCategory.SetSelection(0)


    def _GlueEventCallbacks(self):
        logic = self.Logic

        self.OnBack = logic.OnBack
        #self.OnPurchaseBillId = None
        self.OnForward = logic.OnForward
        self.UpdateItemId = logic.UpdateItemId
        self.UpdateItemBarcode = logic.UpdateItemBarcode
        #self.OnAddRow = None
        self.OnPrint = None
        self.OnSave = logic.Save
        self.GoToPurchaseBill = logic.GoToPurchaseBill

        return

    def _GlueLogic(self):
        logic = self.Logic

        logic.GetPurchaseBillId = self.tcPurchaseBillId.GetValue
        logic.SetPurchaseBillId = self.tcPurchaseBillId.SetValue
        logic.GetDate = self.tcDate.GetValue
        logic.SetDate = self.tcDate.SetValue
        logic.SetSupplierList = self.cbSuppliers.SetDataSource
        logic.SetTaxCategoryList = self.cbTaxCategory.SetDataSource
        logic.SetSupplier = self.cbSuppliers.SetValue
        logic.SetTaxCategory = self.cbTaxCategory.SetValue
        logic.GetSupplier = self.cbSuppliers.GetValue
        logic.GetTaxCategory = self.cbTaxCategory.GetValue
        logic.SetListValue = self.list.SetCellValue
        logic.GetListValue = self.list.GetCellValue
        logic.AppendRow = self.list.AppendRow
        logic.SetRow = self.list.SetRow
        logic.Lock = self.list.SetReadOnly
        logic.HasItems = self.list.HasItems
        logic.GetRowCount = self.list.GetRowCount
        logic.ClearAll = self.list.DeleteAllRows
        logic.PurchaseBillIdError = self.PurchaseBillIdError


    def _InitToolBar(self):
        toolbar = wx.ToolBar(self)#, style=wx.TB_NODIVIDER)

        tbBack = toolbar.AddLabelTool(
                wx.ID_ANY, 'Back', wx.Bitmap(Resource.GetFileName('arrow-left.png')))
        self.Bind(wx.EVT_TOOL, self.OnBack, tbBack)

        self.tcPurchaseBillId = wx.TextCtrl(toolbar,size=wx.Size(80,-1))
        self.tcPurchaseBillId.Bind(wx.EVT_KEY_UP, self.OnPurchaseBillId)

        toolbar.AddControl(self.tcPurchaseBillId)

        tbForward = toolbar.AddLabelTool(
                wx.ID_ANY, 'Forward', wx.Bitmap(Resource.GetFileName('arrow-right.png')))
        self.Bind(wx.EVT_TOOL, self.OnForward, tbForward)

        toolbar.AddSeparator()

        toolbar.Realize()

        self.tbNavigation = toolbar

        toolbar = wx.ToolBar(self)#, style=wx.TB_NODIVIDER)

        tbSave = toolbar.AddLabelTool(wx.ID_ANY, 'Save', wx.Bitmap(Resource.GetFileName('save.png')))
        self.Bind(wx.EVT_TOOL, self.OnSave, tbSave)
        tbAddRow = toolbar.AddLabelTool(wx.ID_ANY, 'Add Row', wx.Bitmap(Resource.GetFileName('add-row.png')))
        self.Bind(wx.EVT_TOOL, self.OnAddRow, tbAddRow)

        tbPrint = toolbar.AddLabelTool(
                wx.ID_ANY, 'Print', wx.Bitmap(Resource.GetFileName('print.png')))
        self.Bind(wx.EVT_TOOL, self.OnPrint, tbPrint)

        toolbar.Realize()

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.tbNavigation,0,wx.ALL,0)
        sizer.Add(toolbar,1, wx.ALL|wx.EXPAND, 0)

        return sizer

    def _InitList(self):
        listctrl = VGrid(self, columns=
                {
                    self.Logic.COL_ID : VGridIntCol('PurchId', ReadOnly=True, Hidden=True),
                    self.Logic.COL_ITEM_ID : VGridIntCol('ItemId', self.UpdateItemId),
                    self.Logic.COL_ITEM_BCODE : VGridIntCol('Barcode', self.UpdateItemBarcode),
                    self.Logic.COL_ITEM_DESC : VGridStringColumn('Desc'),
                    self.Logic.COL_QTY : VGridNumberCol('Qty'),
                    self.Logic.COL_ITEM_UNIT: VGridStringColumn('Unit'),
                    self.Logic.COL_COST : VGridCurrencyCol('Cost', None, symbol=Format.CurrencySymbol),
                    self.Logic.COL_ITEM_SELLING : VGridCurrencyCol('Selling', None, symbol="Rf"),
                    self.Logic.COL_EXPIRY : VGridDateCol('Expiry', Hidden=True)
                })
        listctrl.SetColSize(self.Logic.COL_COST, 110)
        listctrl.SetColSize(self.Logic.COL_ITEM_SELLING, 110)
        listctrl.SetResizeCol(self.Logic.COL_ITEM_DESC)
        return listctrl


    def _InitCtrls(self):
        topsizer = wx.BoxSizer(wx.VERTICAL)

        tb = self._InitToolBar()
        topsizer.Add(tb,0, wx.ALL| wx.EXPAND,0)

        stDate = wx.StaticText(self, label="Date")
        self.tcDate = DateTimePickerCtrl(self, showtime=False)

        stSuppliers = wx.StaticText(self, label="Supplier")
        self.cbSuppliers = DbComboBox(self)

        stTaxCategory = wx.StaticText(self, label="Tax Category")
        self.cbTaxCategory = DbComboBox(self)

        #stTaxCategory2 = wx.StaticText(self, label="Tax Category")
        #self.cbTaxCategory2 = wx.ComboBox(self, 501,
        #        style= wx.CB_DROPDOWN, size = wx.Size(200,-1))

        gridl = wx.FlexGridSizer(3,2)
        gridl.AddGrowableCol(1)

        gridl.Add(stDate, 0, wx.ALL, 5)
        gridl.Add(self.tcDate, 0, wx.ALL| wx.EXPAND, 5)
        gridl.Add(stSuppliers, 0, wx.ALL, 5)
        gridl.Add(self.cbSuppliers, 0, wx.ALL| wx.EXPAND, 5)
        gridl.Add(stTaxCategory, 0, wx.ALL| wx.EXPAND, 5)
        gridl.Add(self.cbTaxCategory, 0, wx.ALL| wx.EXPAND, 5)

        gridr = wx.FlexGridSizer(3,2)
        gridr.AddGrowableCol(1)
        #gridr.Add(stTaxCategory2, 0, wx.ALL| wx.EXPAND, 5)
        #gridr.Add(self.cbTaxCategory2, 0, wx.ALL| wx.EXPAND, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(gridl, 1, wx.ALL| wx.EXPAND)
        hbox.Add(gridr, 1, wx.ALL| wx.EXPAND)

        topsizer.Add(hbox,0, wx.ALL| wx.EXPAND,0)

        self.list = self._InitList()
        topsizer.Add(self.list, 1, wx.ALL| wx.EXPAND, 5)

        self.SetSizer(topsizer)

    def OnPurchaseBillId(self, event):
        kcode = event.GetKeyCode()
        if kcode == wx.WXK_RETURN or kcode == 370:
            billid = self.tcPurchaseBillId.GetValue()
            self.GoToPurchaseBill(billid)


    def OnAddRow(self, event):
        self.list.AppendRow()

    def IsSaved(self):
        return True

    def PurchaseBillIdError(self):
        print "cannot find the entered bill"











