import locale

import wx

import wx.lib.mixins.listctrl  as  listmix

import Format


LIST_COL_TYPE_TEXT = 1
LIST_COL_TYPE_INTEGER = 2
LIST_COL_TYPE_NUMBER = 3
LIST_COL_TYPE_CURRENCY = 4
LIST_COL_TYPE_PERCENT = 5

POPUPID_DEL = wx.NewId()

class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin,listmix.ListCtrlAutoWidthMixin):
    """
    This needs to be replaced with Grid.VGrid in Invoice and Invoice View
    """
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

        self.columnIDs = []
        self.columnTypes = {}
        self.columnCallbacks = {}
        self.columnEditable = {}
        self.rowEditable = {}
        self.itemFloat = []
        self.itemInt = []

        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

        self.Bind(wx.EVT_MENU, self.OnDeleteItem, id=POPUPID_DEL)

        self.Locked = False


    def SetLocked(self, state):
        self.Locked = state


    def OnContextMenu(self, event):
        if self.Locked:
            return

        if self.GetItemCount() < 1:
            event.Skip()
            return

        menu = wx.Menu()
        menu.Append(POPUPID_DEL, "Delete")

        self.PopupMenu(menu)
        menu.Destroy()


    def OnDeleteItem(self, event):
        if self.Locked:
            return

        self.DeleteItem(self.GetFocusedItem())


    def InsertColumn(self, colid, label, coltype=LIST_COL_TYPE_TEXT, callback=None, editable=False, hidden=False):
        if coltype == LIST_COL_TYPE_TEXT:
            wx.ListCtrl.InsertColumn(self, colid, label)
        else:
            wx.ListCtrl.InsertColumn(self, colid, label, wx.LIST_FORMAT_RIGHT)

        if hidden:
            self.SetColumnWidth(colid, 0)
        else:
            self.SetColumnWidth(colid, 80)

        self.columnTypes[colid] = coltype
        self.columnCallbacks[colid] = callback
        self.columnEditable[colid] = editable
        self.columnIDs.append(colid)


    def HideColumn(self, columnid):
        self.SetColumnWidth(columnid, 0)


    def OpenEditor(self,col,row):
        if self.Locked:
            return

        if self.columnEditable[col]:
            if self.columnTypes[col] == LIST_COL_TYPE_INTEGER:
                wx.ListCtrl.SetStringItem(self, row, col, str(self.GetItemInteger(row, col)))
                listmix.TextEditMixin.OpenEditor(self, col,row)
                return
            if self.columnTypes[col] != LIST_COL_TYPE_TEXT:
                wx.ListCtrl.SetStringItem(self,row, col, str(self.GetItemFloat(row, col)))
                listmix.TextEditMixin.OpenEditor(self, col,row)
                return
        else:
            return


    def SetStringItem(self, row, col, text, CallbackOn = True):
        if self.columnTypes[col] == LIST_COL_TYPE_INTEGER:
            try:
                value = int(text)
            except ValueError:
                value = self.itemInt[row][col]
            self.SetIntegerItem(row, col, value, CallbackOn)
            return

        if self.columnTypes[col] != LIST_COL_TYPE_TEXT:
            try:
                value = float(text)
            except ValueError:
                value = self.itemFloat[row][col]
            self.SetFloatItem(row, col, value, CallbackOn)
            return

        if CallbackOn:
            if self.columnCallbacks[col] != None:
                if not self.columnCallbacks[col](row,col,text):
                    #rturn without setting col if callback is false
                    return
        wx.ListCtrl.SetStringItem(self,row, col, text)


    def SetIntegerItem(self, row, col, value, CallbackOn = True):
        try:
            value = int(value)
        except ValueError:
            value = 0

        if CallbackOn:
            if self.columnCallbacks[col] != None:
                if not self.columnCallbacks[col](row,col,value):
                    #rturn without setting col if callback is false
                    return
        self.itemInt[row][col] = value
        wx.ListCtrl.SetStringItem(self,row, col, str(value))


    def SetFloatItem(self, row, col, value, CallbackOn = True):
        try:
            value = float(value)
        except ValueError:
            value = 0.0

        if CallbackOn:
            if self.columnCallbacks[col] != None:
                if not self.columnCallbacks[col](row,col,value):
                    #rturn without setting col if callback is false
                    return

        self.itemFloat[row][col] = value

        if self.columnTypes[col] == LIST_COL_TYPE_TEXT:
            valueFormated = str(value)
        if self.columnTypes[col] == LIST_COL_TYPE_NUMBER:
            valueFormated = '%g' % value
        if self.columnTypes[col] == LIST_COL_TYPE_CURRENCY:
            valueFormated = Format.Currency( value) #'Rf {0}'.format(round(value, 2))
        if self.columnTypes[col] == LIST_COL_TYPE_PERCENT:
            valueFormated = ('%g' % value) + '%'

        wx.ListCtrl.SetStringItem(self,row, col, valueFormated)


    def HasEntry(self, col, value):
        '''
        Check if a given value is in a given column
        returns that row
        '''
        listCount = self.GetItemCount()
        for row in range(listCount) :
            if value == self.GetItemText(row, col):
                return row

        return None


    def GetItemText(self, row, col):
        item = self.GetItem(row, col)
        return item.GetText()


    def GetItemInteger(self, row, col):
        #item = self.GetItem(row, col)
        return self.itemInt[row][col]
        #return item.GetData()


    def GetItemFloat(self, row, col):
        return self.itemFloat[row][col]


    def AddRow(self, row=None):
        rowCount = self.GetItemCount()

        columnCount = self.GetColumnCount()
        self.itemFloat.append([0 for i in range(columnCount)])
        self.itemInt.append([0 for i in range(columnCount)])

        if row == None:
            row = []
            for col in self.columnIDs:
                row.append(' ')

        self.InsertStringItem(rowCount, str(row[self.columnIDs[0]]))

        self.SetRow(rowCount, row)

        return rowCount


    def SetRow(self,rowIndex, row):
        for col in self.columnIDs:
            if self.columnTypes[col] == LIST_COL_TYPE_INTEGER:
                self.SetIntegerItem(rowIndex, col, row[col], False)
            if self.columnTypes[col] == LIST_COL_TYPE_TEXT:
                self.SetStringItem(rowIndex, col, str(row[col]), False)
            if self.columnTypes[col] >= LIST_COL_TYPE_NUMBER:
                self.SetFloatItem(rowIndex, col, row[col], False)
        return True


    def GetColumnSum(self, col):
        rowCount = self.GetItemCount()
        if self.columnTypes[col] == LIST_COL_TYPE_INTEGER:
            total = 0
        else:
            total = 0.0

        if rowCount == 0:
            return total

        for row in range(rowCount):
            if self.columnTypes[col] == LIST_COL_TYPE_INTEGER:
                total += self.GetItemInteger(row, col)
            else:
                total += self.GetItemFloat(row, col)
        return total


    def GetAll(self, cols):
        rowCount = self.GetItemCount()
        result = []
        for row in range(rowCount):
            result.append({})
            for col in cols:

                if self.columnTypes[col] == LIST_COL_TYPE_TEXT:
                    result[row][col] = self.GetItemText(row, col)

                if self.columnTypes[col] == LIST_COL_TYPE_INTEGER:
                    result[row][col] = self.GetItemInteger(row, col)

                if self.columnTypes[col] >= LIST_COL_TYPE_NUMBER:
                    result[row][col] = self.GetItemFloat(row, col)
        return result


    def HasItems(self):
        if self.GetItemCount() > 0:
            return True
        return False

    def DeleteItem(self, row):
        del(self.itemFloat[row])
        del(self.itemInt[row])
        wx.ListCtrl.DeleteItem(self, row)


    def DeleteAllItems(self):
        self.itemFloat = []
        self.itemInt = []
        wx.ListCtrl.DeleteAllItems(self)

    '''
    def GetCol(self, col):
        return []


    def GetRow(self, row):
        return []

    def ClearAll(self):
        self.Freeze()
        rowCount = self.GetItemCount()
        for row in range(rowCount):
            self.DeleteItem(0)
        self.Thaw()
    '''


