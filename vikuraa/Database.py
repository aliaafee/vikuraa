import sqlobject as sql
import sqlobject.sqlbuilder as sqlb

sql.col.default_datetime_implementation = sql.MXDATETIME_IMPLEMENTATION




class User(sql.SQLObject):
    name = sql.StringCol()
    password = sql.StringCol()
    privilages = sql.StringCol(default='')
    invoices = sql.MultipleJoin('Invoice')
    purchaseBills = sql.MultipleJoin('PurchaseBill')


class Session(sql.SQLObject):
    user = sql.StringCol()
    time = sql.DateTimeCol()
    host = sql.StringCol()
    port = sql.IntCol()


class SessionLog(sql.SQLObject):
    user = sql.StringCol()
    session = sql.IntCol()
    time = sql.DateTimeCol()
    host = sql.StringCol()
    port = sql.IntCol()
    action = sql.StringCol()


class TaxCategory(sql.SQLObject):
    name = sql.StringCol()
    rate = sql.FloatCol()


class Item(sql.SQLObject):
    bcode = sql.IntCol()
    desc  = sql.StringCol()
    unit = sql.StringCol()
    selling = sql.FloatCol()
    #available = sql.FloatCol()
    stockStart = sql.FloatCol()
    stockIn = sql.FloatCol()
    stockOut = sql.FloatCol()
    taxCategory = sql.ForeignKey('TaxCategory', notNull=True)
    purchases = sql.MultipleJoin('Purchase')


class Supplier(sql.SQLObject):
    name = sql.StringCol()
    address = sql.StringCol(default='')
    country = sql.StringCol(default='')
    purchasebills = sql.MultipleJoin('PurchaseBill')


class PurchaseBill(sql.SQLObject):
    time = sql.DateTimeCol()
    supplier = sql.ForeignKey('Supplier')
    user = sql.ForeignKey('User', notNull=True)
    purchases = sql.MultipleJoin('Purchase')


class Purchase(sql.SQLObject):
    item = sql.ForeignKey('Item', notNull=True) #, cascade=True)
    purchaseBill = sql.ForeignKey('PurchaseBill', notNull=True)
    qty = sql.FloatCol()
    cost = sql.FloatCol()
    expiry = sql.DateTimeCol()


class PaymentMethod(sql.SQLObject):
    name = sql.StringCol()
    account = sql.ForeignKey('Account')
    invoices = sql.MultipleJoin('Invoice')


class Invoice(sql.SQLObject):
    user = sql.ForeignKey('User', notNull=True)
    time = sql.DateTimeCol()
    address = sql.StringCol()
    total = sql.FloatCol()
    totalTax = sql.FloatCol()
    tendered = sql.FloatCol()
    balance = sql.FloatCol()
    account = sql.ForeignKey('Account', notNull=True)
    paymentMethod = sql.ForeignKey('PaymentMethod', notNull=True)
    approvalCode = sql.StringCol()
    items = sql.MultipleJoin('Sold')
    printed = sql.BoolCol()


class Sold(sql.SQLObject):
    invoice = sql.ForeignKey('Invoice', notNull=True)
    item = sql.ForeignKey('Item', notNull=True)
    qty = sql.FloatCol()
    rate = sql.FloatCol()
    discount = sql.FloatCol()
    total = sql.FloatCol()
    totalTax = sql.FloatCol()


class Account(sql.SQLObject):
    name = sql.StringCol()
    amount = sql.FloatCol()
    invoices = sql.MultipleJoin('Invoice')
    expenditure = sql.MultipleJoin('Expenditure')


class Expenditure(sql.SQLObject):
    name = sql.StringCol()
    amount = sql.FloatCol()
    time = sql.DateTimeCol()
    account = sql.ForeignKey('Account', notNull=True)


class Db(object):
    def __init__(self, dburi):

        self.connection = sql.connectionForURI(dburi)
        sql.sqlhub.processConnection = self.connection


        try:

            PaymentMethod.createTable()
            Invoice.createTable()
            PurchaseBill.createTable()
            Supplier.createTable()
            Expenditure.createTable()
            Account.createTable()
            Sold.createTable()
            Purchase.createTable()
            Item.createTable()
            TaxCategory.createTable()
            User.createTable()
            Session.createTable()
            SessionLog.createTable()

            #Debug data
            '''
            item1 = Item(bcode=1001, desc="Sock", unit="PCS", selling=100, stockStart=20, stockIn=0, stockOut=0, taxCategory=1)

            defaultAccount = Account(name='Cash Card', amount=0.0)
            defaultPaymentMethod = PaymentMethod(name="Cash", account=1)

            testUser = User(name='a',password='a', privilages='LOGIN')
            testUser = User(name='ali',password='ali.log', privilages='LOGIN')
            testUser = User(name='shooga',password='shooga.log', privilages='LOGIN')
            '''
            CashAccount = Account(name='Cash Account', amount=0.0)
            CashMethod = PaymentMethod(name="Cash", account=CashAccount.id)

            CreditAccount = Account(name='Credit Card Account', amount=0.0)
            CreditMethod = PaymentMethod(name="Credit Card", account=CreditAccount.id)

            defaultSupplier = Supplier(name='Default')
            dafaultTax = TaxCategory(name='GST', rate=6.0)

            RootUser = User(name='admin',password='admin', privilages='LOGIN')
        except sql.dberrors.OperationalError:
            print "table exists"


        self.User = User
        self.Session = Session
        self.SessionLog = SessionLog
        self.Supplier = Supplier
        self.Expenditure = Expenditure
        self.Account = Account
        self.Sold = Sold
        self.Invoice = Invoice
        self.Purchase = Purchase
        self.Item = Item
        self.TaxCategory = TaxCategory
        self.PurchaseBill = PurchaseBill
        self.PaymentMethod = PaymentMethod


    def close(self):
        pass


    def startTransaction(self):
        self.old_conn = sql.sqlhub.getConnection()
        self.connection = self.old_conn.transaction()
        sql.sqlhub.threadConnection = self.connection


    def endTransaction(self):
        self.connection = self.old_conn
        sql.sqlhub.threadConnection = self.connection


    def commitTransaction(self):
        self.connection.commit()


    def rollbackTransaction(self):
        self.connection.rollback()

