import wx

from wxHelpers import *
from NumberDisplay import NumberDisplay

import Format

class PaymentDialog(wx.Dialog):
    def __init__(self, parent, paymentMethods, invoiceTotal,
                        invoiceTaxTotal):
        wx.Dialog.__init__(
                self,
                parent = parent,
                name = "PaymentDialog",
                title = "Payment",
                size = wx.Size(350, 360))

        self.PaymentMethods = paymentMethods
        self.InvoiceTotal = invoiceTotal
        self.InvoiceTaxTotal = invoiceTaxTotal

        self._InitCtrls()

        self.Total = invoiceTotal
        self.stTotal.SetLabel(Format.Currency(invoiceTotal))
        self.Tax = invoiceTotal
        self.stTax.SetLabel(Format.Currency(invoiceTaxTotal))
        self.tcTender.SetValue('')

        self.Balance = 0

        self.Calculate()


    def Calculate(self):
        try:
            tender = float(self.tcTender.GetValue())
            balance = tender - self.Total
            if balance > 0.0:
                self.Balance = balance
            else:
                self.Balance = 0
        except ValueError:
            self.Balance = 0

        self.tcBalance.SetLabel(Format.Currency(self.Balance))

        self.Layout()


    def _InitCtrls(self):
        display1 = NumberDisplay(self, ['Total Due', 'Incl. 6% GST'])
        display1.SetSize(wx.Size(100,100))
        self.stTotal = display1.GetStaticText(0)
        self.stTax = display1.GetStaticText(1)

        self.cbPaymentMethod = wx.ComboBox(self, 501,
                            style= wx.CB_DROPDOWN | wx.CB_READONLY, size = wx.Size(200,-1))
        c = LabelCtrl(self, 'Payment Method', self.cbPaymentMethod, size = wx.Size(200,-1), labelexpand = True)

        for method in self.PaymentMethods:
            self.cbPaymentMethod.Append(method.name, method.id)

        self.tcApprovalCode, d = LabeledCtrl(self, "Approval Code", size = wx.Size(200,-1), labelexpand = True)
        self.tcApprovalCode.SetFont(display1.fontBig)
        self.tcApprovalCode.SetWindowStyleFlag(wx.TE_RIGHT | wx.ALIGN_RIGHT)
        self.tcApprovalCode.Bind(wx.EVT_KEY_UP, self.OnEnter)

        self.tcTender, e = LabeledCtrl(self, "Tender", size = wx.Size(200,-1), labelexpand = True)
        self.tcTender.Bind ( wx.EVT_TEXT, self.OnTender )
        self.tcTender.Bind(wx.EVT_KEY_UP, self.OnEnter)
        self.tcTender.SetFont(display1.fontBig)
        self.tcTender.SetWindowStyleFlag(wx.TE_RIGHT | wx.ALIGN_RIGHT)

        self.ndBalance = NumberDisplay(self, ['Balance'])
        self.tcBalance = self.ndBalance.GetStaticText(0)

        btnsizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btnSave = wx.Button(self, label="Save", size=wx.Size(80, -1))
        self.btnSave.Bind(wx.EVT_BUTTON, self.OnDone)

        btnsizer.Add(self.btnSave, 1, wx.ALL|wx.EXPAND, 5)

        self.btnSavePrint = wx.Button(self, label="Save and Print", size=wx.Size(80, -1))
        self.btnSavePrint.Bind(wx.EVT_BUTTON, self.OnDonePrint)

        btnsizer.Add(self.btnSavePrint, 1, wx.ALL|wx.EXPAND, 5)

        self.btnCancel = wx.Button(self, label="Cancel", size=wx.Size(80, -1))
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.chPrint = wx.CheckBox(self, -1, "Print Invoice")
        self.chPrint.Hide()

        btnsizer.Add(self.btnCancel, 1, wx.ALL|wx.EXPAND, 5)

        topsizer = BoxSizerVerticalAdd([display1, c, d, e, self.ndBalance, self.chPrint, btnsizer])

        self.cbPaymentMethod.SetSelection(0)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelectMethod, self.cbPaymentMethod)

        self.OnSelectMethod(None)

        self.SetSizer(topsizer)
        self.Center()


    def OnEnter(self, event):
        kcode = event.GetKeyCode()
        if kcode == wx.WXK_RETURN or kcode == 370:
            ctrl = event.GetEventObject()
            if ctrl.GetValue() != '':
                if ctrl == self.tcTender:
                    try:
                        tender = float(self.tcTender.GetValue())
                    except ValueError:
                        tender = 0
                    if tender >= self.Total:
                        self.OnDone(event)
                else:
                    self.OnDone(event)


    def OnSelectMethod(self, event):
        item = self.cbPaymentMethod.GetSelection()

        if int(self.cbPaymentMethod.GetClientData(item)) == 1:
            self.tcApprovalCode.Hide()
            self.tcApprovalCode.label.Hide()
            self.tcTender.Show()
            self.tcTender.label.Show()
            self.ndBalance.Show()
            self.tcTender.SetFocus()
        else:
            self.tcApprovalCode.Show()
            self.tcApprovalCode.label.Show()
            self.tcTender.Hide()
            self.tcTender.label.Hide()
            self.ndBalance.Hide()
            self.tcApprovalCode.SetFocus()
        self.Layout()


    def OnTender(self, event):
        self.Calculate()

    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnDone(self, event):
        self.EndModal(wx.ID_OK)

    def OnDonePrint(self, event):
        self.chPrint.SetValue(1)
        self.EndModal(wx.ID_OK)

    def GetPaymentMethod(self):
        item = self.cbPaymentMethod.GetSelection()
        return int(self.cbPaymentMethod.GetClientData(item))

    def GetTendered(self):
        try:
            tender = float(self.tcTender.GetValue())
            if tender < self.Total:
                tender = self.Total
        except ValueError:
            tender = self.Total
        self.Balance = tender - self.Total
        return tender

    def GetBalance(self):
        try:
            tender = float(self.tcTender.GetValue())
            if tender < self.Total:
                tender = self.Total
        except ValueError:
            tender = self.Total
        self.Balance = tender - self.Total
        return self.Balance

    def GetApprovalCode(self):
        return self.tcApprovalCode.GetValue()

    def GetPrintInvoice(self):
        if self.chPrint.IsChecked():
            return True
        return False


class PM():
    def __init__(self):
        self.id = 0
        self.name = ''

def curformat(txt):
    return str(txt)

if __name__ == "__main__":
    pm = []
    for i in range(10):
        p = PM()
        p.id = i
        p.name = 'ALi ' + str(i)
        pm.append(p)

    app = wx.App()
    top = PaymentDialog(None, pm, 100, 100, curformat)
    top.Show()
    app.MainLoop()
