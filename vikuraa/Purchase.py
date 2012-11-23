import wx

import Resource
from Window import VWindow
from Grid import *

from DateTimePickerCtrl import DateTimePickerCtrl
from DbComboBox import DbComboBox

class Purchase(VWindow):
    def __init__(self, parent, title, logic):
        VWindow.__init__(self, parent, title, logic)
        self.icon = wx.Bitmap(Resource.GetFileName('purchase-bill-sml.png'))


    def GlueCallBack(self):
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


    def GlueLogic(self):
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


    def InitToolbar(self):
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

        tbSave = toolbar.AddLabelTool(wx.ID_ANY, 'Save', wx.Bitmap(Resource.GetFileName('save.png')))
        self.Bind(wx.EVT_TOOL, self.OnSave, tbSave)
        tbAddRow = toolbar.AddLabelTool(wx.ID_ANY, 'Add Row', wx.Bitmap(Resource.GetFileName('add-row.png')))
        self.Bind(wx.EVT_TOOL, self.OnAddRow, tbAddRow)

        tbPrint = toolbar.AddLabelTool(
                wx.ID_ANY, 'Print', wx.Bitmap(Resource.GetFileName('print.png')))
        self.Bind(wx.EVT_TOOL, self.OnPrint, tbPrint)

        toolbar.Realize()

        self.toolbar = toolbar


    def InitList(self):
        listctrl = VGrid(self, columns=
                {
                    self.Logic.COL_ID : VGridIntCol('PurchId', ReadOnly=True, Hidden=True),
                    self.Logic.COL_ITEM_ID : VGridIntCol('ItemId', self.UpdateItemId),
                    self.Logic.COL_ITEM_BCODE : VGridStringColumn('Barcode', self.UpdateItemBarcode),
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


    def InitControls(self):
        stDate = wx.StaticText(self, label="Date")
        self.tcDate = DateTimePickerCtrl(self, showtime=False)

        stSuppliers = wx.StaticText(self, label="Supplier")
        self.cbSuppliers = DbComboBox(self)

        stTaxCategory = wx.StaticText(self, label="Tax Category")
        self.cbTaxCategory = DbComboBox(self)

        self.list = self.InitList()

        gridl, gridr, top = self.Layout2()

        gridl.Add(stDate, 0, wx.ALL, 3)
        gridl.Add(self.tcDate, 0, wx.ALL| wx.EXPAND, 3)
        gridl.Add(stSuppliers, 0, wx.ALL, 3)
        gridl.Add(self.cbSuppliers, 0, wx.ALL| wx.EXPAND, 3)
        gridl.Add(stTaxCategory, 0, wx.ALL, 3)
        gridl.Add(self.cbTaxCategory, 0, wx.ALL| wx.EXPAND, 3)
        top.Add(self.list, 1, wx.ALL|wx.EXPAND, 3)
        

    def OnPurchaseBillId(self, event):
        kcode = event.GetKeyCode()
        if kcode == wx.WXK_RETURN or kcode == 370:
            billid = self.tcPurchaseBillId.GetValue()
            self.GoToPurchaseBill(billid)


    def OnAddRow(self, event):
        self.list.AppendRow()

        
    def PurchaseBillIdError(self):
        print "cannot find the entered bill"
        

    def DefaultFocus(self):
        pass
        

    def IsSaved(self):
        return True
