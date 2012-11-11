import wx


class DbComboBox(wx.ComboBox):
    def __init__(self, parent, table=None):
        '''
        table is an SQLObject class with
        fields id and name
        '''
        wx.ComboBox.__init__(self, parent, style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.table = table
        self.Populate()

    def SetDataSource(self, table):
        self.table = table
        self.Refresh()

    def Populate(self):
        if self.table == None:
            return
        query = self.table.select()
        for item in query:
            self.Append(item.name, item.id)
        self.SetSelection(0)

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
    uri = 'sqlite:' + os.path.abspath('shop.db') #+ '?debug=t'
    db = Database.Db(uri)

    app = wx.App()
    frame = wx.Frame(None)
    pnl = DbComboBox(frame)
    pnl.SetDataSource(db.User)
    pnl.SetValue(2)
    pnl.Refresh()
    print pnl.GetValue()
    sz = wx.BoxSizer(wx.VERTICAL)
    sz.Add(pnl,0,wx.ALL|wx.EXPAND,10)
    frame.SetSizer(sz)
    frame.Show()



    app.MainLoop()


