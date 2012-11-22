from mx import DateTime
import Format


class InvoiceLogic(object):
    COL_ID = 0
    COL_BCODE = 1
    COL_DESC = 2
    COL_QTY = 3
    COL_UNIT = 4
    COL_AVAILABLE = 5
    COL_RATE = 6
    COL_GSTP = 7
    COL_GST = 8
    COL_DISC = 9
    COL_TOTAL = 10

    GetAddress = None #arg -, ret string
    SetAddress = None
    GetEnteredCode = None #arg -, ret string
    SetEnteredCode = None #arg str
    GetEnteredQty = None
    SetEnteredQty = None
    GetAllItems = None #arg -, ret 2dlist[][?what]
    GetListValue = None #arg row,col ret float
    SetListValue = None #arg row,col,float
    SetItemInteger = None
    GetColSum = None #arg col, ret float
    GetRowWith = None #arg col, search, ret row(int)
    ClearItems = None
    InsertRow = None #arg [?wh], ret bool
    SetTotal = None #arg str
    SetTax = None #arg str
    HasItems = None
    GetPayment = None #arg paymentMethod[][id, name], invoicetotal, taxtotal, ret paymentMethod, tendered, balance, approvalCode
    DeleteRow = None
    SetRow = None #arg row,[?wh], ret bool
    #GetListValue = None #arg row,col ret str
    #SetItemString = None #arg row,col,str
    #GetRow = None #arg row, ret list[?what]
    #GetCol = None #arg col, ret list[?what?]
    #SetRow = None #arg row,[?wh], ret bool
    #DisableUI = None
    #EnableUI = None

    InvoiceTotal = 0.0
    InvoiceTaxTotal = 0.0

    def __init__(self, db, session, peripherals):
        self.db = db
        self.session = session
        self.peripherals = peripherals


    def Start(self):
        pass


    def AddItem(self, code, byitemid=False):
        if byitemid:
            try:
                item = self.db.Item.get(code)
            except:
                print "item not  found"
                return
        else:
            query = self.db.Item.select(self.db.Item.q.bcode == code)
            if query.count() != 1:
                return
            else:
                item = query.getOne()

        row = self.GetRowWith(self.COL_ID, item.id)

        try:
            enteredQty = float(self.GetEnteredQty())
        except ValueError:
            enteredQty = 1.0

        if enteredQty == 0:
            return

        self.SetEnteredQty("1")

        if row != None:
            qty = self.GetListValue(row, self.COL_QTY)
            qty += enteredQty
            self.SetListValue(row, self.COL_QTY, qty)
            self.SetListValue(row, self.COL_AVAILABLE, item.stockStart + item.stockIn - item.stockOut)
            self.UpdateRow(row)
        else:
            row = self.InsertRow([
                item.id,
                item.bcode,
                item.desc,
                enteredQty,
                item.unit,
                item.stockStart + item.stockIn - item.stockOut,
                item.selling,
                item.taxCategory.rate,
                0.0,
                0.0,
                0.0])
            self.UpdateRow(row)


    def OnSearch(self, event):
        code = self.GetEnteredCode()
        self.SetEnteredCode('')
        if code == '':
            self.SetEnteredQty("1")
            self.SaveInvoice()
            return
        elif code[0] == 'i' and code[1:].isdigit:
            print code[0]
            print code[1:]
            try:
                code = int(code[1:])
            except ValueError:
                return
            self.AddItem(code, True)
            event.Skip()
            return
        elif code.isdigit():
            self.AddItem(int(code))
            event.Skip()
            return



    def UpdateItemId(self, row, col, value, prev_value):
        self.SetListValue(row, col, prev_value)


    def UpdateBarcode(self, row, col, value, prev_value):
        twinrow = self.GetRowWith(self.COL_BCODE, value, row)
        if twinrow != None:
            if twinrow != row:
                qty = self.GetListValue(twinrow, self.COL_QTY) + self.GetListValue(row, self.COL_QTY)
                self.SetListValue(twinrow, self.COL_QTY, qty)
                self.UpdateRow(twinrow)
                self.DeleteRow(row)
                return True

        try:
            code = int(value)
        except:
            print "bad code"
            self.SetListValue(row, col, prev_value)
            return False

        try:
            query = self.db.Item.select(self.db.Item.q.bcode == code)
        except:
            print "not found"
            self.SetListValue(row, col, prev_value)
            return False

        if query.count() != 1:
            print "not found 2"
            self.SetListValue(row, col, prev_value)
            return False

        print "everything fine"

        item = query.getOne()

        self.SetRow(row,[
                    item.id,
                    item.bcode,
                    item.desc,
                    1.0,
                    item.unit,
                    item.stockStart + item.stockIn - item.stockOut,
                    item.selling,
                    item.taxCategory.rate,
                    0.0,
                    0.0,
                    0.0])

        self.UpdateRow(row)

        return True


    def UpdateQty(self, row, col, value, prev_value):
        if value == 0:
            self.DeleteRow(row)
            self.UpdateTotals()
            return False
        else:
            self.UpdateRow(row)
            return True


    def UpdateRow(self, row):
        qty = self.GetListValue(row, self.COL_QTY)
        disc = self.GetListValue(row, self.COL_DISC)
        rate = self.GetListValue(row, self.COL_RATE)
        gstP = self.GetListValue(row, self.COL_GSTP)

        total = qty * rate - disc
        tax = total - ((100 * total)/(100 + gstP))

        self.SetListValue(row, self.COL_GST, tax)
        self.SetListValue(row, self.COL_TOTAL, total)

        self.UpdateTotals()

        return True


    def UpdateTotals(self):
        self.InvoiceTotal = self.GetColSum(self.COL_TOTAL)
        self.InvoiceTaxTotal = self.GetColSum(self.COL_GST)

        self.SetTotal(Format.Currency(self.InvoiceTotal))
        self.SetTax(Format.Currency(self.InvoiceTaxTotal))


    def Print(self, invoice, isreprint=True):
        try:
            p = self.peripherals.ReciptPrinter()
        except IOError, e:
            print "Looks like the printer is not working. Print canceled"
            print e
            return

        p.Line_c('SOME MART')
        p.Line_c('Somewide Hingun')
        p.Line_c('Z. Somedhoo')
        p.Line_c('Somedives')
        p.Line_c('TIN: 000000000000')
        p.Line_b()
        p.Line_c('TAX INVOICE')
        p.Line_b()
        p.Table([
            ['', p.ALIGN_L, [str(invoice.time)]],
            ['', p.ALIGN_R, ['ID:{0}'.format(invoice.id)]]])
        p.Line_b()
        if invoice.address != '':
            p.Line_l('Billed to {0}'.format(invoice.address), trimtopagewidth=False)
            p.Line_b()
        if invoice.printed:
            p.Line_c("###### REPRINT ######")
            p.Line_b()

        descs = []
        qtys = []
        rates = []
        totals = []
        subtotal = 0
        #discounts = []
        for sold in invoice.items:
            descs.append(sold.item.desc)
            qtys.append(('%g' % sold.qty))
            rate = sold.rate - sold.totalTax
            rates.append(Format.Currency(rate, symbol=''))
            total = rate * sold.qty
            totals.append(Format.Currency(total, symbol=''))
            subtotal += total
            #discounts.append(Format.Currency(sold.discount, symbol=''))

        p.Table([
            ['Desc' , p.ALIGN_L, descs],
            ['Qty' , p.ALIGN_R, qtys],
            ['Rate' , p.ALIGN_R, rates],
            #['Disc' , p.ALIGN_R, discounts],
            ['Amnt' , p.ALIGN_R, totals]])

        p.Line_b()
        p.Line_r('   Sub Total Rf' + (Format.Currency(subtotal, symbol='').rjust(10)))
        p.Line_r('      6% GST Rf' + (Format.Currency(invoice.totalTax, symbol='').rjust(10)))
        p.SetBig_on()
        p.SetColor_red()
        p.Line_r('   Total Due Rf' + (Format.Currency(invoice.total, symbol='').rjust(10)))
        p.SetBig_off()
        p.SetColor_black()

        if invoice.paymentMethod.id == 1:
            p.Line_r('      Tender Rf' + (Format.Currency(invoice.tendered, symbol='').rjust(10)))
            p.Line_r('     Balance Rf' + (Format.Currency(invoice.balance, symbol='').rjust(10)))
        else:
            p.Line_r('   Payment by {0}'.format(invoice.paymentMethod.name))
            if invoice.approvalCode != '':
                p.Line_r('   Approval Code {0}'.format(invoice.approvalCode))
        p.Line_b()
        p.Line_c("served by {0}".format(invoice.user.name))
        p.Line_c('Thank You')

        p.End()

        invoice.printed = True


    def SaveInvoice(self):
        if not self.HasItems():
            return

        query = self.db.PaymentMethod.select()

        paymentMethods = query[0:]

        payment = self.GetPayment(paymentMethods,self.InvoiceTotal, self.InvoiceTaxTotal)

        paymentOk, paymentMethodId, tendered, balance, approvalCode, printInvoice = payment

        if not paymentOk:
            return

        self.db.startTransaction()
        try:
            paymentMethod = self.db.PaymentMethod.get(paymentMethodId)
            account = paymentMethod.account

            invoice = self.db.Invoice(
                user = self.session.user.id,
                time = DateTime.now(),
                address = self.GetAddress(),
                total = self.InvoiceTotal,
                totalTax = self.InvoiceTaxTotal,
                tendered = tendered,
                balance = balance,
                account = account.id,
                paymentMethod = paymentMethod.id,
                approvalCode = approvalCode,
                printed = False)

            account.amount = account.amount + self.InvoiceTotal

            entries = self.GetAllItems([
                        self.COL_ID,
                        self.COL_BCODE,
                        self.COL_DESC,
                        self.COL_QTY,
                        self.COL_UNIT,
                        self.COL_AVAILABLE,
                        self.COL_RATE,
                        self.COL_GSTP,
                        self.COL_GST,
                        self.COL_DISC,
                        self.COL_TOTAL])
            print entries

            for entrie in entries:
                if entrie[self.COL_ID] == 0:
                    #sell openitem
                    print "selling open item"
                else:
                    item = self.db.Item.get(entrie[self.COL_ID])
                    item.stockOut = item.stockOut + entrie[self.COL_QTY]

                    sold = self.db.Sold(
                            invoice = invoice.id,
                            item = item.id,
                            qty = entrie[self.COL_QTY],
                            rate = entrie[self.COL_RATE],
                            total = entrie[self.COL_TOTAL],
                            discount = entrie[self.COL_DISC],
                            totalTax = entrie[self.COL_GST])

            if printInvoice:
                self.Print(invoice)

            self.ClearItems()
            self.SetAddress('')
            self.UpdateTotals()
        except Exception, err:
            self.db.rollbackTransaction()
            print('ERROR: %s\n' % str(err))

            print "error invoice not saved"
        else:
            self.db.commitTransaction()
        self.db.endTransaction()






