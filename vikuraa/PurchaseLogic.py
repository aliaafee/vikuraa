from datetime import datetime
import Format

from Database import Session, Supplier, TaxCategory, PurchaseBill, Item, Purchase


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


    def __init__(self, userSession, peripherals):
        self.userSession = userSession
        self.peripherals = peripherals

        self.session = Session()


    def __del__(self):
        self.session.close()


    def Start(self):
        self.SetSupplierList(Supplier)
        self.SetTaxCategoryList(TaxCategory)
        try:
            query = self.session.query(PurchaseBill)
            last = query[-1]
            self.PurchaseBill = last
            self.Display()
        except:
            self.PurchaseBill = None
            self.New()


    def OnBack(self, event):
        if self.PurchaseBill == None:
            try:
                query = self.session.query(PurchaseBill)
                last = query[-1]
                self.PurchaseBill = last
                self.Display()
            except:
                pass
        else:
            try:
                self.PurchaseBill = self.session.query(PurchaseBill).\
                                    filter(PurchaseBill.id == (self.PurchaseBill.id - 1)).one()
                self.Display()
            except:
                print "No more behind"


    def OnForward(self, event):
        if self.PurchaseBill != None:
            try:
                self.PurchaseBill = self.session.query(PurchaseBill).\
                                    filter(PurchaseBill.id == (self.PurchaseBill.id + 1)).one()
                self.Display()
            except:
                self.PurchaseBill = None
                self.New()


    def GoToPurchaseBill(self, billid):
        try:
            self.PurchaseBill = self.session.query(PurchaseBill).\
                                    filter(PurchaseBill.id == (billid)).one()
            self.Display()
        except:
            if self.PurchaseBill != None:
                self.SetPurchaseBillId(str(self.PurchaseBill.id))
            else:
                self.New()
            self.PurchaseBillIdError()


    def New(self):
        self.ClearAll()
        self.SetPurchaseBillId('New')
        self.SetDate(datetime.now())
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
        item = Item(
                bcode = self.GetListValue(row, self.COL_ITEM_BCODE),
                desc = self.GetListValue(row, self.COL_ITEM_DESC),
                unit = self.GetListValue(row, self.COL_ITEM_UNIT),
                selling = self.GetListValue(row, self.COL_ITEM_SELLING),
                stockStart = 0,
                stockIn = 0,
                stockOut = 0,
                taxCategory_id = self.GetTaxCategory())

        self.session.add(item)
        self.session.flush()
        
        if item.bcode == '':
            item.bcode = 'S'+(str(item.id)).upper().zfill(4)
        
        return item


    def OverWrite(self):
        print "OverWriting"
        try:
            self.PurchaseBill.time = self.GetDate()
            self.PurchaseBill.supplier_id = self.GetSupplier()
            self.PurchaseBill.user_id = self.userSession.user.id

            for row in range(self.GetRowCount()):
                purchaseid = self.GetListValue(row, self.COL_ID)
                if purchaseid == 0:
                    self.SaveNewPurchase(row, self.PurchaseBill)
                else:
                    self.OverWritePurchase(purchaseid, row, self.PurchaseBill)

        except ValueError, err:
            self.session.rollback()
            print('ERROR: %s\n' % str(err))

            print "error bill not saved"
        else:
            self.session.commit()
            self.Display()


    def OverWritePurchase(self, purchasid, row, bill):
        try:
            purchase = self.session.query(Purchase).filer(Purchase.id == purchaseid).one()
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
                        item = self.session.query(Item).filter(Item.id == itemid).one()
                    except:
                        itemid = 0
                        item = self.AddNewItem(row)


            purchase.item_id = item.id
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
            self.session.delete(purchase)
            self.session.flush()
            if item.stockStart == 0 and item.stockIn == 0 and item.stockOut == 0:
                self.session.delete(item)
                self.session.flush()


    def SaveNewPurchase(self, row, bill):
        qty = self.GetListValue(row, self.COL_QTY)
        if qty != 0:
            itemid = self.GetListValue(row, self.COL_ITEM_ID)
            if itemid == 0:
                item = self.AddNewItem(row)
            else:
                try:
                    item = self.session.query(Item).filter(Item.id == itemid).one()
                except:
                    itemid = 0
                    item = self.AddNewItem(row)

            purchase = Purchase(
                item_id=item.id,
                purchaseBill_id = bill.id,
                qty = qty,
                cost = self.GetListValue(row, self.COL_COST),
                expiry = self.GetListValue(row, self.COL_EXPIRY))

            self.session.add(purchase)

            item.stockIn = item.stockIn + purchase.qty


    def SaveNew(self):
        if not self.HasItems():
            print "nothing to save"
            return

        try:
            bill = PurchaseBill(
                    time = self.GetDate(),
                    supplier_id = self.GetSupplier(),
                    user_id = self.userSession.user.id)

            self.session.add(bill)
            self.session.flush()

            for row in range(self.GetRowCount()):
                self.SaveNewPurchase(row, bill)

        except Exception, err:
            self.session.rollback()
            print('ERROR: %s\n' % str(err))

            print "error bill not saved"
        else:
            self.session.commit()
            self.PurchaseBill = bill
            self.Display()


    def ClearRow(self, row):
        self.SetRow( row,
            [ self.GetListValue(row, self.COL_ID),
            0,
            '',
            '',
            0,
            '',
            0,
            0,
            datetime.now() ])


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


    def UpdateItemId(self,row,col,code, prev_code):
        try:
            item = self.session.query(Item).filter(Item.id == code).one()
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


    def UpdateItemBarcode(self,row,col,code, prev_code):
        itemid = self.GetListValue(row, self.COL_ITEM_ID)
        if itemid == 0:
            #Search if no item selected
            try:
                item = self.session.query(Item).filter(Item.bcode == code).one()
            except:
                self.SetListValue(row, self.COL_ITEM_BCODE, code)
                self.SetForNewItem(row)
            else:
                self.SetListValue(row, self.COL_ITEM_ID, item.id)
                self.SetListValue(row, self.COL_ITEM_BCODE, item.bcode)
                self.SetListValue(row, self.COL_ITEM_DESC, item.desc)
                self.SetListValue(row, self.COL_ITEM_UNIT, item.unit)
                self.SetListValue(row, self.COL_ITEM_SELLING, item.selling)
                self.SetForExistingItem(row)
        else:
            #If item select check whether any item is using the entered barcode
            try:
                other = self.session.query(Item).filter(Item.bcode == code).filter(Item.id != itemid).one()
            except:
                pass
            else:
                print "Another item with same bcode exists"
                self.SetListValue(row, self.COL_ITEM_BCODE, prev_code)


