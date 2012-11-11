import wx

import EditableListCtrl as ListCtrl
from PaymentDialog import PaymentDialog
from NumberDisplay import NumberDisplay
from wxHelpers import *
from DateTimePickerCtrl import DateTimePickerCtrl
import Resource


class Invoice(wx.Panel):
    Logic = None

    OnSearch = None
    UpdateItemId = None
    UpdateBarcode = None
    UpdateRow = None
    CurrencyFormat = None

    def __init__(self, parent, logic):
        wx.Panel.__init__(self, parent)

        self.Logic = logic

        self._GlueEventCallbacks()

        sizer = self._InitCtrls()

        self.SetSizer(sizer)

        self._GlueLogic()

        self.Bind(wx.EVT_CLOSE, self.OnClose)


    def _GlueEventCallbacks(self):
        logic = self.Logic
        if logic != None:
            self.CurrencyFormat = logic.CurrencyFormat
            self.OnSearch = logic.OnSearch
            self.UpdateItemId = logic.UpdateItemId
            self.UpdateBarcode = logic.UpdateBarcode
            self.UpdateRow = logic.UpdateRow


    def _GlueLogic(self):
        logic = self.Logic

        logic.GetAddress = self.tcAddress.GetValue
        logic.SetAddress = self.tcAddress.SetValue
        try:
            logic.GetEnteredCode = self.tcCode.GetValue
            logic.SetEnteredCode = self.tcCode.SetValue
            logic.GetEnteredQty = self.tcQty.GetValue
            logic.SetEnteredQty = self.tcQty.SetValue
        except:
            pass
        logic.GetAllItems = self.list.GetAll
        logic.GetItemFloat = self.list.GetItemFloat
        logic.GetItemString = self.list.GetItemText
        logic.SetItemFloat = self.list.SetFloatItem
        logic.SetItemString = self.list.SetStringItem
        logic.GetColSum = self.list.GetColumnSum
        logic.GetRowWith = self.list.HasEntry
        logic.InsertRow = self.list.AddRow
        logic.SetRow = self.list.SetRow
        logic.SetTotal = self.SetTotal
        logic.SetTax = self.SetTax
        logic.DisableUI = self.Disable
        logic.EnableUI = self.Enable
        logic.HasItems = self.list.HasItems
        logic.ClearItems = self.list.DeleteAllItems
        logic.GetPayment = self.ShowPaymentDialog
        logic.DeleteRow = self.list.DeleteItem


    def SetTotal(self, text):
        try:
            self.tcTotal.SetLabel(text)
            if self.UpdateDisplay != None:
                self.UpdateDisplay()
        except:
            self.tcTotal.SetValue(text)


    def SetTax(self, text):
        try:
            self.tcTax.SetLabel(text)
            if self.UpdateDisplay != None:
                self.UpdateDisplay()
        except:
            self.tcTax.SetValue(text)


    def _InitList(self):
        listctrl = ListCtrl.EditableListCtrl(self,
                style = wx.LC_REPORT, currencyformat=self.CurrencyFormat)

        editable=True

        listctrl.InsertColumn(self.Logic.COL_ID, 'ItemId', ListCtrl.LIST_COL_TYPE_INTEGER, self.UpdateItemId, False)
        listctrl.InsertColumn(self.Logic.COL_BCODE, 'Barcode', ListCtrl.LIST_COL_TYPE_INTEGER, self.UpdateBarcode, editable)
        listctrl.InsertColumn(self.Logic.COL_DESC, 'Desc     ')
        listctrl.InsertColumn(self.Logic.COL_QTY, '      Qty', ListCtrl.LIST_COL_TYPE_NUMBER, self.UpdateRow, editable)
        listctrl.InsertColumn(self.Logic.COL_UNIT, 'Unit')
        listctrl.InsertColumn(self.Logic.COL_AVAILABLE, 'Available', ListCtrl.LIST_COL_TYPE_NUMBER)
        listctrl.InsertColumn(self.Logic.COL_RATE, '     Rate', ListCtrl.LIST_COL_TYPE_CURRENCY)
        listctrl.InsertColumn(self.Logic.COL_GST, '      GST', ListCtrl.LIST_COL_TYPE_CURRENCY)

        listctrl.InsertColumn(self.Logic.COL_TOTAL, '           Total', ListCtrl.LIST_COL_TYPE_CURRENCY)



        listctrl.InsertColumn(self.Logic.COL_GSTP, 'GST%', ListCtrl.LIST_COL_TYPE_PERCENT, hidden=True)
        listctrl.InsertColumn(self.Logic.COL_DISC, 'Disc', ListCtrl.LIST_COL_TYPE_CURRENCY, self.UpdateRow, editable, hidden=True)

        listctrl.setResizeColumn(self.Logic.COL_QTY)
        listctrl.SetColumnWidth(self.Logic.COL_QTY, -2)
        listctrl.SetColumnWidth(self.Logic.COL_TOTAL, 100)

        return listctrl


    def _InitCtrls(self, readonly=False):
        topsizer = wx.GridBagSizer()

        lblDate = wx.StaticText(self,label = 'Date')
        #self.tcDate = wx.TextCtrl(self)
        self.tcDate = DateTimePickerCtrl(self)
        self.tcDate.label = lblDate
        if not readonly:
            self.tcDate.Hide()
            lblDate.Hide()
        topsizer.Add(lblDate, (0,0), (1,1), wx.ALL | wx.EXPAND, 5)
        topsizer.Add(self.tcDate, (0,1), (1,1), wx.ALL, 5)

        lblAddress = wx.StaticText(self,label = 'Address')
        self.tcAddress = wx.TextCtrl(self)
        topsizer.Add(lblAddress, (1,0), (1,1), wx.ALL | wx.EXPAND, 5)
        topsizer.Add(self.tcAddress, (1,1), (1,1), wx.ALL | wx.EXPAND, 5)

        if not readonly:
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
            #topsizer.Add(self.tcCode, (2,0), (1,2), wx.ALL | wx.EXPAND, 5)
            stQty = wx.StaticText(self,label = 'Qty')
            self.tcQty = wx.TextCtrl(self, size=(60,-1), style=wx.TE_RIGHT | wx.ALIGN_RIGHT)
            self.tcQty.SetValue("1")
            self.tcQty.SetFont(self.fontMed)
            self.tcQty.Bind(wx.EVT_KEY_UP, self.OnQty)
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            hbox.Add(stQty,0,wx.ALL | wx.ALIGN_CENTER_VERTICAL,0)
            hbox.Add(self.tcQty,0,wx.ALL,0)
            hbox.Add(self.tcCode,1,wx.ALL | wx.EXPAND,0)
            topsizer.Add(hbox, (2,0), (1,2), wx.ALL | wx.EXPAND, 5)


            numdisplay = NumberDisplay(self,['Total','Incl. 6% GST'], size=wx.Size(-1,-1))
            topsizer.Add(numdisplay, (0,2), (3,2), wx.ALL | wx.EXPAND, 5)
            self.tcTotal = numdisplay.GetStaticText(0)
            self.tcTax = numdisplay.GetStaticText(1)
            self.UpdateDisplay = numdisplay.Layout

        self.list = self._InitList()

        if readonly:
            self.list.SetLocked(True)
        topsizer.Add(self.list, (3,0), (1,4), wx.ALL | wx.EXPAND, 5)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        topsizer.AddGrowableCol(1)
        topsizer.AddGrowableCol(3)
        topsizer.AddGrowableRow(3)

        return topsizer

    def OnDate(self, event):
        now = wx.DateTime()
        now.Set
        #tcDate.SetValue()
        print tcDate.GetValue()

    def OnEnter(self, event):
        kcode = event.GetKeyCode()
        print kcode
        if kcode == wx.WXK_RETURN or kcode == 370:
            print "hell"
            self.OnSearch(event)

    def OnQty(self, event):
        kcode = event.GetKeyCode()
        if kcode == wx.WXK_RETURN or kcode == 370:
            self.tcCode.SetFocus()

    def Enable(self):
        self.GetParent().Enable(True)
        self.tcAddress.Enable(True)
        self.tcCode.Enable(True)
        self.list.Enable(True)
        self.tcTotal.Enable(True)
        self.tcTax.Enable(True)


    def Disable(self):
        self.GetParent().Enable(False)
        self.tcAddress.Enable(False)
        self.tcCode.Enable(False)
        self.list.Enable(False)
        self.tcTotal.Enable(False)
        self.tcTax.Enable(False)


    def ShowPaymentDialog(self, paymentMethods, invoiceTotal, invoiceTaxTotal):
        dlg = PaymentDialog(self, paymentMethods, invoiceTotal,
                                invoiceTaxTotal, self.CurrencyFormat)

        result = dlg.ShowModal()

        if result == wx.ID_OK:
            return (True, dlg.GetPaymentMethod(), dlg.GetTendered(),
                            dlg.GetBalance(), dlg.GetApprovalCode(),
                            dlg.GetPrintInvoice())

        return False, 0.0, 0.0, 0.0, '', False


    def IsSaved(self):
        print self.list.GetItemCount()
        if self.list.GetItemCount() == 0:
            return True
        return False


    def OnClose(self, event):
        print "Closing it"




