import wx
import wx.aui

from Invoice import Invoice
from InvoiceLogic import InvoiceLogic

from InvoiceView import InvoiceView, InvoiceViewLogic

from Purchase import Purchase
from PurchaseLogic import PurchaseLogic

from LoginPrompt import LoginPrompt

import Resource


class MainFrame(wx.Frame):
    _InvoiceCount = 0

    def __init__(self, parent, session, peripherals):
        wx.Frame.__init__(
            self,
            name = 'MainFrame',
            title = 'Vikuraa',
            parent = parent,
            style = wx.DEFAULT_FRAME_STYLE,
            size = wx.Size(800, 600)
            #size = wx.DisplaySize()
            )

        self._InitMenu()
        self._InitCtrls()

        self.session = session
        self.peripherals = peripherals


    def _InitMenu(self):
        self.menuBar = wx.MenuBar()

        self.SetMenuBar(self.menuBar)

        self.filemenu = wx.Menu()

        menulogout = 400
        self.filemenu.Append(menulogout, "Logout", "Log out of the current session")
        wx.EVT_MENU(self, menulogout,  self.OnLogOut)


        self.filemenu.Append(wx.ID_EXIT, "Exit", "Exit the program")
        wx.EVT_MENU(self, wx.ID_EXIT,  self.OnExit)

        self.menuBar.Append(self.filemenu, "&File")

        self.status = self.CreateStatusBar()


    def _InitToolBar(self):
        toolbar = wx.ToolBar(self, style=wx.TB_NODIVIDER)

        tbNewInvoice = toolbar.AddLabelTool(
                wx.ID_ANY, 'New Invoice', wx.Bitmap(Resource.GetFileName('invoice-new.png')))
        self.Bind(wx.EVT_TOOL, self.OnNewInvoice, tbNewInvoice)

        tbViewInvoice = toolbar.AddLabelTool(
                wx.ID_ANY, 'View Invoice', wx.Bitmap(Resource.GetFileName('invoice-view.png')))
        self.Bind(wx.EVT_TOOL, self.OnViewInvoice, tbViewInvoice)

        toolbar.AddSeparator()

        tbPurchase = toolbar.AddLabelTool(
                wx.ID_ANY, 'Purchase Bill', wx.Bitmap(Resource.GetFileName('purchase-bill.png')))
        self.Bind(wx.EVT_TOOL, self.OnPurchase, tbPurchase)


        toolbar.Realize()

        userbar = wx.ToolBar(self, style=wx.TB_NODIVIDER)

        tbLogOut = userbar.AddLabelTool(
                wx.ID_ANY, 'Quit', wx.Bitmap(Resource.GetFileName('exit.png')))
        self.Bind(wx.EVT_TOOL, self.OnLogOut, tbLogOut)

        userbar.Realize()

        self.stUserName = wx.StaticText(self, label="")

        maintoolbar = wx.BoxSizer(wx.HORIZONTAL)
        maintoolbar.Add(toolbar, 1, wx.ALIGN_LEFT, 5)
        maintoolbar.Add(self.stUserName, 0,
                            wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL,5)
        maintoolbar.Add(userbar, 0, wx.ALIGN_RIGHT, 5)

        return maintoolbar


    def _InitCtrls(self):
        topsizer = wx.BoxSizer(wx.VERTICAL)

        toolbar = self._InitToolBar()
        topsizer.Add(toolbar, 0, wx.ALL | wx.EXPAND)

        self.plMain = wx.aui.AuiNotebook(self)
        topsizer.Add(self.plMain, 1, wx.ALL | wx.EXPAND)
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnClosePage)

        self.SetSizer(topsizer)

        self.Bind(wx.EVT_CLOSE, self.OnClose)


    def Show(self):
        wx.Frame.Show(self)
        self.DoLogin()


    def DoLogin(self):
        if not self.session.IsLoggedIn():
            while True:
                dlg = LoginPrompt(self)
                result = dlg.ShowModal()
                if result == wx.ID_OK:
                    user, password = dlg.getLogin()

                    if self.session.Login(user, password):
                        self.stUserName.SetLabel(self.session.user.name)
                        self.Layout()
                        break
                    else:
                        print "Invalid Username/Password"
                        wx.MessageBox('Invalid Username/Password', 'Login Error',
                                            wx.OK | wx.ICON_ERROR)
                else:
                    self.Close()
                    break
        else:
            self.stUserName.SetLabel(self.session.user.name)
            self.Layout()


    def OnLogOut(self, event):
        if not self.IsSaved():
            dlg = wx.MessageDialog(None,
                'There is some unsaved data. Are you sure you want to logout without saving?',
                'Unsaved data',
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            result = dlg.ShowModal()
            if result == wx.ID_NO:
                return
        for i in range(self.plMain.GetPageCount()):
            self.plMain.DeletePage(0)
        self.session.Logout()
        self.stUserName.SetLabel('')
        self.Layout()
        self.DoLogin()


    def OnExit(self, event):
        self.Close()


    def IsSaved(self):
        pageCount = self.plMain.GetPageCount()
        if pageCount == 0:
            return True

        for i in range(pageCount):
            window = self.plMain.GetPage(i)
            if not window.IsSaved():
                return False

        return True
    

    def OnClosePage(self, event):
        window = self.plMain.GetPage(event.GetSelection())
        if not window.IsSaved():
            dlg = wx.MessageDialog(None, 'There is some unsaved data. Are you sure you want to exit without saving?', 'Unsaved data',
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            result = dlg.ShowModal()
            if result == wx.ID_NO:
                event.Veto()
                return

        event.Skip


    def OnClose(self, event):
        if self.session.user == None:
            event.Skip()
            return

        if not self.IsSaved():
            dlg = wx.MessageDialog(None, 'There is some unsaved data. Are you sure you want to exit without saving?', 'Unsaved data',
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            result = dlg.ShowModal()
            if result == wx.ID_YES:
                self.session.Logout()
                event.Skip()
            else:
                try:
                    event.Veto()
                except:
                    pass
                return

        self.session.Logout()
        event.Skip()


    def _AddPage(self, pnl, title, iconfile):
        self.plMain.AddPage(pnl, title)
        pageid = self.plMain.GetPageIndex(pnl)
        self.plMain.SetPageBitmap(pageid, wx.Bitmap(Resource.GetFileName(iconfile)))
        self.plMain.SetSelection(pageid)


    def OnNewInvoice(self, event):
        #if not self.session.HasPermission('NEWINVOICE'):
        #    return
        self._InvoiceCount += 1

        window = Invoice(
                self.plMain,
                'New Sale {0}'.format(self._InvoiceCount),
                InvoiceLogic(self.session, self.peripherals))

        window.AddToAuiNotebook(self.plMain)


    def OnViewInvoice(self, event):
        window = InvoiceView(
                self.plMain,
                'View Sales',
                InvoiceViewLogic(self.session, self.peripherals))

        window.AddToAuiNotebook(self.plMain)


    def OnPurchase(self, event):
        window = Purchase(
                self.plMain,
                'Purchases',
                PurchaseLogic(self.session, self.peripherals))

        window.AddToAuiNotebook(self.plMain)


