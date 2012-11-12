from mx import DateTime
import Formats
import sqlobject.sqlbuilder as sqlb
import sqlobject
#import TextTable as tb

class PurchaseLogic(object):
    COL_ID = 0
    COL_ITEM_ID = 1
    COL_ITEM_BCODE = 2
    COL_ITEM_DESC = 3
    COL_QTY = 4
    COL_ITEM_UNIT = 5
    COL_COST = 6
    COL_ITEM_SELLING = 7
    COL_EXPIRY = 8
    #COL_ITEM_TAX_CAT = 9

    SetSupplierList = None
    SetTaxCategoryList = None
    GetSupplier = None
    GetTaxCategory = None
    SetSupplier = None
    SetTaxCategory =  None
    SetListValue = None
    GetListValue = None
    SetRow = None
    Lock = None
    GetPurchaseBillId = None
    HasItems = None
    ShowNavBar = None
    HideNavBar = None
    PurchaseBillIdError = None

    CurrencyFormat = Formats.CurrencyFormat

    def __init__(self, db, session, peripherals):
        self.db = db
        self.session = session
        self.peripherals = peripherals


    def Start(self):
        self.SetSupplierList(self.db.Supplier)
        self.SetTaxCategoryList(self.db.TaxCategory)
        try:
            query = self.db.PurchaseBill.select()
            last = query[-1]
            self.PurchaseBill = last
            self.Display()
        except:
            self.PurchaseBill = None
            self.New()


    def OnBack(self, event):
        if self.PurchaseBill == None:
            try:
                query = self.db.PurchaseBill.select()
                last = query[-1]
                self.PurchaseBill = last
                self.Display()
            except:
                pass
        else:
            try:
                self.PurchaseBill = self.db.PurchaseBill.get(self.PurchaseBill.id - 1)
                self.Display()
            except sqlobject.main.SQLObjectNotFound:
                print "No more behind"


    def OnForward(self, event):
        if self.PurchaseBill != None:
            try:
                self.PurchaseBill = self.db.PurchaseBill.get(self.PurchaseBill.id + 1)
                self.Display()
            except sqlobject.main.SQLObjectNotFound:
                self.PurchaseBill = None
                self.New()


    def GoToPurchaseBill(self, billid):
        try:
            self.PurchaseBill = self.db.PurchaseBill.get(billid)
            self.Display()
        except sqlobject.main.SQLObjectNotFound:
            if self.PurchaseBill != None:
                self.SetPurchaseBillId(str(self.PurchaseBill.id))
            else:
                self.New()
            self.PurchaseBillIdError()


    def New(self):
        self.ClearAll()
        self.SetPurchaseBillId('New')
        self.SetDate(DateTime.now())
        self.SetSupplier(0)
        self.SetTaxCategory(0)


    def Display(self):
        self.ClearAll()
        if self.PurchaseBill == None:
            return

        self.SetPurchaseBillId(str(self.PurchaseBill.id))
        self.SetDate(self.PurchaseBill.time)
        self.SetSupplier(self.PurchaseBill.supplier.id)

        for purchase in self.PurchaseBill.purchases:
            row = self.AppendRow()
            self.SetRow(row, [
                    purchase.id,
                    purchase.item.id,
                    purchase.item.bcode,
                    purchase.item.desc,
                    purchase.qty,
                    purchase.item.unit,
                    purchase.cost,
                    purchase.item.selling,
                    purchase.expiry])
            self.SetForExistingItem(row)
            self.SetTaxCategory(purchase.item.taxCategory.id)


    def Save(self, event):
        try:
            billId = int(self.GetPurchaseBillId())
        except ValueError:
            billId = 0

        if self.PurchaseBill == None:
            self.SaveNew()
        else:
            self.OverWrite()


    def AddNewItem(self, row):
        item = self.db.Item(
                bcode = self.GetListValue(row, self.COL_ITEM_BCODE),
                desc = self.GetListValue(row, self.COL_ITEM_DESC),
                unit = self.GetListValue(row, self.COL_ITEM_UNIT),
                selling = self.GetListValue(row, self.COL_ITEM_SELLING),
                stockStart = 0,
                stockIn = 0,
                stockOut = 0,
                taxCategory = self.GetTaxCategory())
        if item.bcode == 0:
            item.bcode = item.id
        return item


    def OverWrite(self):
        print "OverWriting"
        self.db.startTransaction()
        try:
            self.PurchaseBill.time = self.GetDate()
            self.PurchaseBill.supplier = self.GetSupplier()
            self.PurchaseBill.user = self.session.user.id

            for row in range(self.GetRowCount()):
                purchaseid = self.GetListValue(row, self.COL_ID)
                if purchaseid == 0:
                    self.SaveNewPurchase(row, self.PurchaseBill)
                else:
                    self.OverWritePurchase(purchaseid, row, self.PurchaseBill)

        except ValueError, err:
            self.db.rollbackTransaction()
            print('ERROR: %s\n' % str(err))

            print "error bill not saved"
        else:
            self.db.commitTransaction()
            self.Display()
        self.db.endTransaction()


    def OverWritePurchase(self, purchasid, row, bill):
        try:
            purchase = self.db.Purchase.get(purchasid)
        except:
            self.SaveNewPurchase(row, bill)
            return

        #undo previous stuff
        item = purchase.item
        item.stockIn = item.stockIn - purchase.qty
        qty = self.GetListValue(row, self.COL_QTY)

        if qty != 0:
            itemid = self.GetListValue(row, self.COL_ITEM_ID)
            if item.id != itemid:
                if itemid == 0:
                    item = self.AddNewItem(row)
                else:
                    try:
                        item = self.db.Item.get(itemid)
                    except:
                        itemid = 0
                        item = self.AddNewItem(row)


            purchase.item = item.id
            purchase.qty = qty
            purchase.cost = self.GetListValue(row, self.COL_COST)
            purchase.expiry = self.GetListValue(row, self.COL_EXPIRY)

            item.stockIn = item.stockIn + purchase.qty

            item.bcode = self.GetListValue(row, self.COL_ITEM_BCODE)
            item.desc = self.GetListValue(row, self.COL_ITEM_DESC)
            item.unit = self.GetListValue(row, self.COL_ITEM_UNIT)
            item.selling = self.GetListValue(row, self.COL_ITEM_SELLING)
        else:
            '''
            If the qty is zero the delete this purchase record
            '''
            update = sqlb.Delete('purchase',
                        where=(self.db.Purchase.q.id == purchase.id))
            query = self.db.connection.sqlrepr(update)
            self.db.connection.query(query)
            if item.stockStart == 0 and item.stockIn == 0 and item.stockOut == 0:
                update = sqlb.Delete('item',
                        where=(self.db.Item.q.id == item.id))
                query = self.db.connection.sqlrepr(update)
                self.db.connection.query(query)



    def SaveNewPurchase(self, row, bill):
        qty = self.GetListValue(row, self.COL_QTY)
        if qty != 0:
            itemid = self.GetListValue(row, self.COL_ITEM_ID)
            if itemid == 0:
                item = self.AddNewItem(row)
            else:
                try:
                    item = self.db.Item.get(itemid)
                except:
                    itemid = 0
                    item = self.AddNewItem(row)

            purchase = self.db.Purchase(
                item=item.id,
                purchaseBill = bill.id,
                qty = qty,
                cost = self.GetListValue(row, self.COL_COST),
                expiry = self.GetListValue(row, self.COL_EXPIRY))

            item.stockIn = item.stockIn + purchase.qty


    def SaveNew(self):
        if not self.HasItems():
            print "nothing to save"
            return

        self.db.startTransaction()
        try:
            bill = self.db.PurchaseBill(
                    time = self.GetDate(),
                    supplier = self.GetSupplier(),
                    user = self.session.user.id)

            for row in range(self.GetRowCount()):
                self.SaveNewPurchase(row, bill)



        except Exception, err:
            self.db.rollbackTransaction()
            print('ERROR: %s\n' % str(err))

            print "error bill not saved"
        else:
            self.db.commitTransaction()
            self.PurchaseBill = bill
            self.Display()
        self.db.endTransaction()


    def ClearRow(self, row):
        self.SetRow( row,
            [ self.GetListValue(row, self.COL_ID),
            0,
            0,
            '',
            0,
            '',
            0,
            0,
            DateTime.now() ])


    def SetForNewItem(self, row):
        self.Lock(row, self.COL_ITEM_ID, False)
        self.Lock(row, self.COL_ITEM_BCODE, False)
        self.Lock(row, self.COL_ITEM_DESC, False)
        self.Lock(row, self.COL_QTY, False)
        self.Lock(row, self.COL_ITEM_UNIT, False)
        self.Lock(row, self.COL_COST, False)
        self.Lock(row, self.COL_ITEM_SELLING, False)
        self.Lock(row, self.COL_EXPIRY, False)


    def SetForExistingItem(self, row):
        self.Lock(row, self.COL_ITEM_ID, False)
        self.Lock(row, self.COL_ITEM_BCODE, False)
        self.Lock(row, self.COL_ITEM_DESC, False)
        self.Lock(row, self.COL_QTY, False)
        self.Lock(row, self.COL_ITEM_UNIT, False)
        self.Lock(row, self.COL_COST, False)
        self.Lock(row, self.COL_ITEM_SELLING, False)
        self.Lock(row, self.COL_EXPIRY, False)


    def UpdateItemId(self,row,col,code):
        try:
            item = self.db.Item.get(code)
        except:
            self.ClearRow(row)
            self.SetListValue(row, self.COL_ITEM_ID, code)
            self.SetForNewItem(row)
        else:
            self.SetListValue(row, self.COL_ITEM_ID, item.id)
            self.SetListValue(row, self.COL_ITEM_BCODE, item.bcode)
            self.SetListValue(row, self.COL_ITEM_DESC, item.desc)
            self.SetListValue(row, self.COL_ITEM_UNIT, item.unit)
            self.SetListValue(row, self.COL_ITEM_SELLING, item.selling)
            self.SetForExistingItem(row)


    def UpdateItemBarcode(self,row,col,code):
        itemid = self.GetListValue(row, self.COL_ITEM_ID)
        if itemid == 0:
            #Search if no item selected
            query = self.db.Item.select(self.db.Item.q.bcode == code)
            if query.count() != 1:
                self.SetListValue(row, self.COL_ITEM_BCODE, code)
                self.SetForNewItem(row)
            else:
                item = query.getOne()
                self.SetListValue(row, self.COL_ITEM_ID, item.id)
                self.SetListValue(row, self.COL_ITEM_BCODE, item.bcode)
                self.SetListValue(row, self.COL_ITEM_DESC, item.desc)
                self.SetListValue(row, self.COL_ITEM_UNIT, item.unit)
                self.SetListValue(row, self.COL_ITEM_SELLING, item.selling)
                self.SetForExistingItem(row)
        else:
            #If item select check whether any item is using the entered barcode
            query = self.db.Item.select(self.db.Item.q.bcode == code)
            if query.count() > 0:
                item = query[0]
                if item.id != itemid:
                    print "Another item with same bcode exists"
                    item = self.db.Item.get(itemid)
                    self.SetListValue(row, self.COL_ITEM_BCODE, item.bcode)