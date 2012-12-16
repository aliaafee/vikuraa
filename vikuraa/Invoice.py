import wx

import Resource
from Window import VWindow
from Grid import *

from DateTimePickerCtrl import DateTimePickerCtrl
from NumberDisplay import NumberDisplay
from PaymentDialog import PaymentDialog

class Invoice(VWindow):
    def __init__(self, parent, title, logic):
        VWindow.__init__(self, parent, title, logic)
        self.icon = wx.Bitmap(Resource.GetFileName('invoice-new-sml.png'))


    def GlueCallBack(self):
        logic = self.Logic

        self.OnSearch = logic.OnSearch
        self.UpdateItemId = logic.UpdateItemId
        self.UpdateBarcode = logic.UpdateBarcode
        self.UpdateQty = logic.UpdateQty


    def GlueLogic(self):
        logic = self.Logic

        logic.GetAddress = self.tcAddress.GetValue
        logic.SetAddress = self.tcAddress.SetValue
        logic.SetTotal = self.SetTotal
        logic.SetTax = self.SetTax
        logic.DisableUI = self.Disable
        logic.EnableUI = self.Enable
        logic.GetPayment = self.ShowPaymentDialog
        logic.GetEnteredCode = self.tcCode.GetValue
        logic.SetEnteredCode = self.tcCode.SetValue
        logic.GetEnteredQty = self.tcQty.GetValue
        logic.SetEnteredQty = self.tcQty.SetValue

        self.GlueListLogic()


    def GlueListLogic(self):
        logic = self.Logic

        logic.GetAllItems = self.list.GetAll
        logic.GetListValue = self.list.GetCellValue
        logic.SetListValue = self.list.SetCellValue
        logic.GetColSum = self.list.GetColumnSum
        logic.GetRowWith = self.list.SearchCol
        logic.InsertRow = self.list.AppendRow
        logic.SetRow = self.list.SetRow
        logic.HasItems = self.list.HasItems
        logic.ClearItems = self.list.DeleteAllRows
        logic.DeleteRow = self.list.DeleteRow


    def InitList(self, view=False):
        listctrl = VGrid(self, columns=
                {
                    self.Logic.COL_ID : VGridIntCol('ItemId', self.UpdateItemId, ReadOnly=view),
                    self.Logic.COL_BCODE : VGridStringColumn('Barcode', self.UpdateBarcode, ReadOnly=view),
                    self.Logic.COL_DESC: VGridStringColumn('Desc', ReadOnly=True),
                    self.Logic.COL_QTY: VGridNumberCol('Qty', self.UpdateQty, ReadOnly=view),
                    self.Logic.COL_UNIT: VGridStringColumn('Unit', ReadOnly=True),
                    self.Logic.COL_AVAILABLE: VGridNumberCol('Available', ReadOnly=True, Hidden=view),
                    self.Logic.COL_RATE: VGridCurrencyCol('Rate', ReadOnly=True, symbol="Rf"),
                    self.Logic.COL_GST: VGridCurrencyCol('GST', ReadOnly=True, symbol="Rf"),
                    self.Logic.COL_TOTAL: VGridCurrencyCol('Total', ReadOnly=True, symbol="Rf"),
                    self.Logic.COL_GSTP: VGridPercentCol('GST%', ReadOnly=True, Hidden=True),
                    self.Logic.COL_DISC: VGridCurrencyCol('Disc', ReadOnly=True, Hidden=True, symbol="Rf")
                })
        listctrl.SetResizeCol(self.Logic.COL_DESC)
        return listctrl


    def InitControls(self):
        self.list = self.InitList()

        stAddress = wx.StaticText(self, label = 'Address')
        self.tcAddress = wx.TextCtrl(self, size=wx.Size(-1, 10), style=wx.TE_MULTILINE)

        self.fontMed = wx.Font(
            16,
            family=wx.MODERN,
            style=wx.NORMAL,
            weight=wx.FONTWEIGHT_BOLD)

        self.tcCode = wx.SearchCtrl(self, size=(100,-1),style=wx.TE_PROCESS_ENTER)
        self.tcCode.SetDescriptiveText("Bar Code/ Item Code")
        self.tcCode.SetFont(self.fontMed)
        #self.tcCode.Bind(wx.EVT_KEY_UP, self.OnEnter)
        self.tcCode.Bind(wx.EVT_TEXT_ENTER, self.OnSearch)

        stQty = wx.StaticText(self,label = 'Qty|Code')
        self.tcQty = wx.TextCtrl(self, size=(60,-1), style=wx.TE_RIGHT | wx.ALIGN_RIGHT)
        self.tcQty.SetValue("1")
        self.tcQty.SetFont(self.fontMed)
        self.tcQty.Bind(wx.EVT_KEY_UP, self.OnQty)

        self.numdisplay = NumberDisplay(self,['Total','Incl. 6% GST'], size=wx.Size(-1,-1))

        gridl, gridr, top = self.Layout2()

        gridl.Add(stAddress, 1, wx.ALL, 3)
        gridl.Add(self.tcAddress, 1, wx.ALL| wx.EXPAND, 3)
        #gridl.AddSpacer(0)
        #gridl.AddSpacer(0)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.tcQty,0,wx.ALL | wx.EXPAND,0)
        hbox.Add(self.tcCode,1,wx.ALL | wx.EXPAND, 0)
        
        gridl.Add(stQty,0,wx.ALL | wx.ALIGN_CENTER_VERTICAL,3)
        gridl.Add(hbox, 0, wx.ALL | wx.EXPAND, 3)
        
        gridl.AddGrowableRow(0)
        
        gridr.AddSpacer(0)
        gridr.Add(self.numdisplay, 1, wx.ALL | wx.EXPAND, 3)

        top.Add(self.list, 1, wx.ALL|wx.EXPAND, 3)


    def OnQty(self, event):
        kcode = event.GetKeyCode()
        if kcode == wx.WXK_RETURN or kcode == 370:
            self.tcCode.SetFocus()


    def SetTotal(self, value):
        self.numdisplay.SetValue(0, value)


    def SetTax(self, value):
        self.numdisplay.SetValue(1, value)


    def ShowPaymentDialog(self, paymentMethods, invoiceTotal, invoiceTaxTotal):
        dlg = PaymentDialog(self, paymentMethods, invoiceTotal, invoiceTaxTotal)

        result = dlg.ShowModal()

        if result == wx.ID_OK:
            return (True, dlg.GetPaymentMethod(), dlg.GetTendered(),
                            dlg.GetBalance(), dlg.GetApprovalCode(),
                            dlg.GetPrintInvoice())

        return False, 0.0, 0.0, 0.0, '', False


    def DefaultFocus(self):
        self.tcCode.SetFocus()


    def IsSaved(self):
        if self.list.GetRowCount() == 0:
            return True
        return False
