import wx

from wxHelpers import *

from Invoice import Invoice
from InvoiceLogic import InvoiceLogic
import sqlobject

import Resource

class InvoiceViewLogic(InvoiceLogic):
    SetInvoiceId = None
    SetPaymentMethod = None
    SetApprovalCode = None
    SetTendered = None
    SetBalance = None
    SetDate = None
    SetHideCash = None
    SetShowCash = None

    invoice = None

    def DisplayLast(self):
        try:
            query = self.db.Invoice.select()
            last = query[-1]
            self.invoice = last
            self.Display()
        except:
            print "There are no invoices"
            self.SetInvoiceId("No Invoices")


    def Display(self):
        #self.invoice = self.db.Invoice.get(invoiceId)
        self.SetInvoiceId(str(self.invoice.id))
        self.SetDate(self.invoice.time)
        self.ClearItems()
        for sold in self.invoice.items:
            self.InsertRow([
                    sold.item.id,
                    sold.item.bcode,
                    sold.item.desc,
                    sold.qty,
                    sold.item.unit,
                    sold.item.stockStart + sold.item.stockIn - sold.item.stockOut,
                    sold.item.selling,
                    sold.item.taxCategory.rate,
                    sold.totalTax,
                    sold.discount,
                    sold.total])
        self.SetTax(self.CurrencyFormat(self.invoice.totalTax))
        self.SetTotal(self.CurrencyFormat(self.invoice.total))
        if self.invoice.paymentMethod.id == 1:
            self.SetShowCash()
            self.SetTendered(self.CurrencyFormat(self.invoice.tendered))
            self.SetBalance(self.CurrencyFormat(self.invoice.balance))
        else:
            self.SetHideCash()
            self.SetPaymentMethod(self.invoice.paymentMethod.name)
            self.SetApprovalCode(self.invoice.approvalCode)


    def OnBack(self, event):
        if self.invoice != None:
            try:
                self.invoice = self.db.Invoice.get(self.invoice.id - 1)
                self.Display()
            except sqlobject.main.SQLObjectNotFound:
                print "No more behind"


    def OnForward(self, event):
        if self.invoice != None:
            try:
                self.invoice = self.db.Invoice.get(self.invoice.id + 1)
                self.Display()
            except sqlobject.main.SQLObjectNotFound:
                print "No more ahead"


    def OnPrint(self, event):
        self.Print(self.invoice)


    def GoToInvoice(self, invoiceId):
        try:
            invoiceId = int(invoiceId)
            self.invoice = self.db.Invoice.get(invoiceId)
            self.Display()
        except (ValueError,sqlobject.main.SQLObjectNotFound), e:
            self.SetInvoiceId(str(self.invoice.id))
            self.InvoiceIdError()
            return




class InvoiceView(Invoice):
    def __init__(self, parent, logic):
        wx.Panel.__init__(self, parent)

        self.Logic = logic

        self._GlueEventCallbacks()

        sizer = self._InitCtrls(readonly=True)
        sizer = self._InitViewCtrls(sizer)

        self.SetSizer(sizer)

        self._GlueLogic()

        self.Logic.DisplayLast()


    def _GlueEventCallbacks(self):
        logic = self.Logic

        self.OnBack = logic.OnBack
        self.OnForward = logic.OnForward
        self.OnPrint = logic.OnPrint
        self.OnGotoInvoice = logic.GoToInvoice
        self.CurrencyFormat = logic.CurrencyFormat


    def _GlueLogic(self):
        Invoice._GlueLogic(self)
        logic = self.Logic

        logic.SetInvoiceId = self.tcInvoiceId.SetValue
        logic.SetDate = self.tcDate.SetValue
        logic.SetPaymentMethod = self.tcPaymentMethod.SetValue
        logic.SetApprovalCode = self.tcApprovalCode.SetValue
        logic.SetTendered = self.tcTendered.SetValue
        logic.SetBalance = self.tcBalance.SetValue
        logic.SetHideCash = self.HideCash
        logic.SetShowCash = self.ShowCash
        logic.InvoiceIdError = self.InvoiceIdError


    def _InitToolBar(self):
        toolbar = wx.ToolBar(self)#, style=wx.TB_NODIVIDER)

        tbBack = toolbar.AddLabelTool(
                wx.ID_ANY, 'Back', wx.Bitmap(Resource.GetFileName('arrow-left.png')))
        self.Bind(wx.EVT_TOOL, self.OnBack, tbBack)

        self.tcInvoiceId = wx.TextCtrl(toolbar,size=wx.Size(80,-1))
        self.tcInvoiceId.Bind(wx.EVT_KEY_UP, self.OnInvoiceId)

        toolbar.AddControl(self.tcInvoiceId)

        tbForward = toolbar.AddLabelTool(
                wx.ID_ANY, 'Forward', wx.Bitmap(Resource.GetFileName('arrow-right.png')))
        self.Bind(wx.EVT_TOOL, self.OnForward, tbForward)

        tbPrint = toolbar.AddLabelTool(
                wx.ID_ANY, 'Print', wx.Bitmap(Resource.GetFileName('print.png')))
        self.Bind(wx.EVT_TOOL, self.OnPrint, tbPrint)

        toolbar.Realize()

        return toolbar


    def _InitViewCtrls(self, mainsizer):
        topsizer = wx.BoxSizer(wx.VERTICAL)

        self.list.HideColumn(self.Logic.COL_AVAILABLE)

        tb = self._InitToolBar()
        topsizer.Add(tb,0, wx.ALL| wx.EXPAND,0)

        #self.tcDate, sizer = LabeledCtrl(self, 'Date', wx.ALIGN_LEFT, wx.Size(-1,-1), False)
        #rsizer.Add(sizer, 0, wx.ALL| wx.EXPAND, 2)

        #self.tcInvoiceId, sizer = LabeledCtrl(self, 'Invoice Id')
        #rsizer.Add(sizer, 0, wx.ALL| wx.EXPAND, 2)

        #self.tcInvoiceId.Bind(wx.EVT_KEY_UP, self.OnInvoiceId)

        lsizer = wx.BoxSizer(wx.VERTICAL)

        self.tcTotal, sizer = LabeledCtrl(self, 'Total',
                                        wx.ALIGN_LEFT, wx.Size(-1,-1), False)
        lsizer.Add(sizer, 0, wx.EXPAND | wx.ALL, 0)

        self.tcTax, sizer = LabeledCtrl(self, 'Incl 6% GST',
                                        wx.ALIGN_LEFT, wx.Size(-1,-1), False)
        lsizer.Add(sizer, 0, wx.EXPAND | wx.ALL, 0)

        self.tcPaymentMethod, sizer = LabeledCtrl(self, 'Payment Method',
                                        wx.ALIGN_LEFT, wx.Size(-1,-1), False)
        lsizer.Add(sizer, 0, wx.EXPAND | wx.ALL, 0)

        self.tcApprovalCode, sizer = LabeledCtrl(self, 'Approval Code',
                                        wx.ALIGN_LEFT, wx.Size(-1,-1), False)
        lsizer.Add(sizer, 0, wx.EXPAND | wx.ALL, 0)

        self.tcTendered, sizer = LabeledCtrl(self, 'Tendered',
                                        wx.ALIGN_LEFT, wx.Size(-1,-1), False)
        self.tcTendered.SetWindowStyleFlag(wx.TE_RIGHT | wx.ALIGN_RIGHT)
        lsizer.Add(sizer, 0, wx.EXPAND | wx.ALL, 0)

        self.tcBalance, sizer = LabeledCtrl(self, 'Balance',
                                        wx.ALIGN_LEFT, wx.Size(-1,-1), False)
        self.tcBalance.SetWindowStyleFlag(wx.TE_RIGHT | wx.ALIGN_RIGHT)
        lsizer.Add(sizer, 0, wx.EXPAND | wx.ALL, 0)
        self.UpdateDisplay = None

        mainsizer.Add(lsizer, (0,2), (3,2), wx.ALL | wx.EXPAND, 5)

        topsizer.Add(mainsizer,1,wx.ALL|wx.EXPAND,0)

        return topsizer


    def OnInvoiceId(self, event):
        kcode = event.GetKeyCode()
        if kcode == wx.WXK_RETURN or kcode == 370:
            invoiceId = self.tcInvoiceId.GetValue()
            #print invoiceId
            self.OnGotoInvoice(invoiceId)
            event.GetEventObject().SetFocus()


    def InvoiceIdError(self):
        print "Looks like you typed a wronge invoice id"


    def HideCash(self):
        self.tcBalance.Hide()
        self.tcTendered.Hide()
        self.tcApprovalCode.Show()
        self.tcPaymentMethod.Show()
        self.tcBalance.label.Hide()
        self.tcTendered.label.Hide()
        self.tcApprovalCode.label.Show()
        self.tcPaymentMethod.label.Show()
        self.Layout()

    def ShowCash(self):
        self.tcBalance.Show()
        self.tcTendered.Show()
        self.tcApprovalCode.Hide()
        self.tcPaymentMethod.Hide()
        self.tcBalance.label.Show()
        self.tcTendered.label.Show()
        self.tcApprovalCode.label.Hide()
        self.tcPaymentMethod.label.Hide()
        self.Layout()


    def IsSaved(self):
        return True


if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    logic = InvoiceViewLogic(None, None, None)
    pnl = InvoiceView(frame, logic)
    sz = wx.BoxSizer()
    sz.Add(pnl,1,wx.ALL|wx.EXPAND,0)
    frame.SetSizer(sz)
    frame.Show()
    app.MainLoop()
