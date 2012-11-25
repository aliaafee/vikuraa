from sqlalchemy.dialects.sqlite.base import dialect
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Integer, String, ForeignKey, DateTime, Float, Text, Boolean
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref


Session = sessionmaker()


class Base(object):
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=Base)


class User(Base):
    id = Column(String(50), primary_key=True)
    name = Column(String(100))
    password = Column(String(50))
    privilages = Column(String(200))


class UserSession(Base):
    user_id = Column(String(50), ForeignKey('user.id'))
    time = Column(DateTime)
    host = Column(String(50))
    port = Column(Integer)


class UserSessionLog(Base):
    user_id = Column(String(50), ForeignKey('user.id'))
    time = Column(DateTime)
    host = Column(String(50))
    port = Column(Integer)
    action = Column(String(10))


class TaxCategory(Base):
    name = Column(String(100))
    rate = Column(Float)


class Item(Base):
    bcode = Column(String(200))
    desc  = Column(String(200))
    unit = Column(String(50))
    selling = Column(Float)
    stockStart = Column(Float, default=0.0)
    stockIn = Column(Float, default=0.0)
    stockOut = Column(Float, default=0.0)
    taxCategory_id = Column(Integer, ForeignKey('taxcategory.id'))
    taxCategory = relationship("TaxCategory")


class PaymentMethod(Base):
    name = Column(String(200))
    account_id = Column(Integer, ForeignKey('account.id'))
    account = relationship("Account")


class Invoice(Base):
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User")
    time = Column(DateTime)
    address = Column(Text)
    total = Column(Float, default=0.0)
    totalTax = Column(Float, default=0.0)
    tendered = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)
    
    account_id = Column(Integer, ForeignKey('account.id'))
    account = relationship("Account")
    
    paymentMethod_id = Column(Integer, ForeignKey('paymentmethod.id'))
    paymentMethod = relationship("PaymentMethod")
    
    approvalCode = Column(String(200))
    printed = Column(Boolean())
    
    items = relationship("Sold")


class Sold(Base):
    invoice_id = Column(Integer, ForeignKey('invoice.id'))
    item_id = Column(Integer, ForeignKey('item.id'))
    item = relationship('Item')
    qty = Column(Float, default=0.0)
    rate = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    totalTax = Column(Float, default=0.0)


class Account(Base):
    name = Column(String(200))
    amount = Column(Float, default=0.0)


class Supplier(Base):
    name = Column(String(200))
    address = Column(Text)
    country = Column(String(200))


class PurchaseBill(Base):
    time = Column(DateTime)
    supplier_id = Column(Integer, ForeignKey('supplier.id'))
    supplier = relationship("Supplier")
    user_id = Column(Integer, ForeignKey('user.id'))
    purchases = relationship("Purchase")


class Purchase(Base):
    item_id = Column(Integer, ForeignKey('item.id'))
    item = relationship('Item')
    purchaseBill_id = Column(Integer, ForeignKey('purchasebill.id'))
    qty = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)
    expiry = Column(DateTime)
    
    

def StartEngine(uri):
    engine = create_engine(uri, echo=False)

    Base.metadata.create_all(engine)

    Session.configure(bind=engine)

    session = Session()
    adminuser = session.query(User).filter_by(id='admin').first()
    
    if adminuser == None:
        CashAccount = Account(name='Cash Account', amount=0.0)
        CreditAccount = Account(name='Credit Card Account', amount=0.0)
        
        session.add_all([CashAccount, CreditAccount])
        session.flush()
        
        CashMethod = PaymentMethod(name="Cash", account_id=CashAccount.id)
        CreditMethod = PaymentMethod(name="Credit Card", account_id=CreditAccount.id)

        defaultTax = TaxCategory(name='GST', rate=6.0)
        defaultSupplier = Supplier(name='Default')

        AdminUser = User(id='admin', name='Administrator',password='admin', privilages='LOGIN')

        session.add_all([CashMethod, CreditMethod, defaultTax, AdminUser, defaultSupplier])

        session.commit()

