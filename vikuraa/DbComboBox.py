import wx
from Database import Session

class DbComboBox(wx.ComboBox):
    def __init__(self, parent, table=None):
        '''
        Table is an SQLObject class with
        at leasr id and name field
        '''
        wx.ComboBox.__init__(self, parent, style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.table = table
        self.Populate()


    def SetDataSource(self, table):
        "Set the table after the ctrl was created"
        self.table = table
        self.Refresh()


    def Populate(self):
        session = Session()
        if self.table == None:
            return
        query = session.query(self.table)
        for item in query:
            self.Append(item.name, item.id)
        self.SetSelection(0)
        session.close()


    def GetValue(self):
        if self.table == None:
            return
        if self.GetCount() == 0:
            return None
        item = self.GetSelection()
        return self.GetClientData(item)


    def SetValue(self, value):
        if self.table == None:
            return
        if self.GetCount() == 0:
            return
        for index in range(self.GetCount()):
            if self.GetClientData(index) == value:
                self.SetSelection(index)
                return
        self.SetSelection(0)


    def Refresh(self):
        if self.table == None:
            return
        if self.GetCount() == 0:
            self.Populate()
            return
        value = self.GetValue()
        self.Clear()
        self.Populate()
        self.SetValue(value)



if __name__ == "__main__":
    import Database
    import os.path
    uri = 'sqlite:///' + os.path.abspath('test.db') #+ '?debug=t'
    Database.StartEngine(uri)

    app = wx.App()
    frame = wx.Frame(None)
    pnl = DbComboBox(frame)
    pnl.SetDataSource(Database.User)
    pnl.SetValue(2)
    pnl.Refresh()
    print pnl.GetValue()
    sz = wx.BoxSizer(wx.VERTICAL)
    sz.Add(pnl,0,wx.ALL|wx.EXPAND,10)
    frame.SetSizer(sz)
    frame.Show()

    app.MainLoop()


