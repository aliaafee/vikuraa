import wx

import sqlobject

from Invoice import Invoice
from InvoiceLogic import InvoiceLogic
from DateTimePickerCtrl import DateTimePickerCtrl

import Resource
import Format

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
        self.SetTax(Format.Currency(self.invoice.totalTax))
        self.SetTotal(Format.Currency(self.invoice.total))
        if self.invoice.paymentMethod.id == 1:
            self.SetShowCash()
            self.SetTendered(Format.Currency(self.invoice.tendered))
            self.SetBalance(Format.Currency(self.invoice.balance))
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
    def __init__(self, parent, title, logic):
        Invoice.__init__(self, parent, title, logic)

        self.Logic.DisplayLast()


    def GlueCallBack(self):
        logic = self.Logic

        self.OnBack = logic.OnBack
        self.OnForward = logic.OnForward
        self.OnPrint = logic.OnPrint
        self.OnGotoInvoice = logic.GoToInvoice
        self.UpdateItemId = None
        self.UpdateBarcode = None
        self.UpdateQty = None


    def GlueLogic(self):
        logic = self.Logic

        logic.SetTotal = self.tcTotal.SetValue
        logic.SetTax = self.tcTax.SetValue
        logic.SetInvoiceId = self.tcInvoiceId.SetValue
        logic.SetDate = self.tcDate.SetValue
        logic.SetPaymentMethod = self.tcPaymentMethod.SetValue
        logic.SetApprovalCode = self.tcApprovalCode.SetValue
        logic.SetTendered = self.tcTendered.SetValue
        logic.SetBalance = self.tcBalance.SetValue
        logic.SetHideCash = self.HideCash
        logic.SetShowCash = self.ShowCash
        logic.InvoiceIdError = self.InvoiceIdError

        self.GlueListLogic()


    def DefaultFocus(self):
        pass


    def IsSaved(self):
        return True


    def InitToolbar(self):
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

        self.toolbar = toolbar


    def InitControls(self):
        gridl, gridr, top = self.Layout2()

        self.list = self.InitList(True)

        top.Add(self.list, 1, wx.ALL|wx.EXPAND, 3)

        stDate = wx.StaticText(self,label = 'Date')
        self.tcDate = DateTimePickerCtrl(self)

        stAddress = wx.StaticText(self,label = 'Address')
        self.tcAddress = wx.TextCtrl(self)

        gridl.Add(stDate, 0, wx.ALL, 3)
        gridl.Add(self.tcDate, 0, wx.ALL|wx.EXPAND, 3)
        gridl.Add(stAddress, 0, wx.ALL, 3)
        gridl.Add(self.tcAddress, 0, wx.ALL|wx.EXPAND, 3)


        self.tcTotal,self.tcTax,self.tcPaymentMethod,self.tcApprovalCode,self.tcTendered,self.tcBalance = self.LabeledTextCtrls(
            gridr,
            ['Total', 'Incl 6% GST', 'Payment Method','Approval Code', 'Tendered', 'Balance'],
            wx.TE_RIGHT | wx.ALIGN_RIGHT)


    def OnInvoiceId(self, event):
        kcode = event.GetKeyCode()
        if kcode == wx.WXK_RETURN or kcode == 370:
            invoiceId = self.tcInvoiceId.GetValue()
            #print invoiceId
            self.OnGotoInvoice(invoiceId)
            event.GetEventObject().SetFocus()


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