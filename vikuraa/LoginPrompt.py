import wx


class LoginPrompt(wx.Dialog):
    def __init__(self, parent, message=''):
        self.message = message

        self._init_ctrls(parent)


    def _init_ctrls(self, parent):
        wx.Dialog.__init__(
            self, name='LoginPrompt', parent=parent,
			style=wx.DEFAULT_DIALOG_STYLE,
			title="Login",
			size=wx.Size(350,150)
			)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.AddSpacer(10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddSpacer(10)

        self.lblUsername = wx.StaticText(self, label="Username", size=wx.Size(100, -1))
        self.txtUsername = wx.TextCtrl(self)
        self.txtUsername.Bind(wx.EVT_KEY_UP, self.onUserName)

        hbox.Add(self.lblUsername, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.Add(self.txtUsername, 1, wx.ALL | wx.EXPAND, 5)
        hbox.AddSpacer(10)
        vbox.Add(hbox,0,wx.EXPAND)
        vbox.AddSpacer(10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddSpacer(10)

        self.lblPassword = wx.StaticText(self, label="Password", size=wx.Size(100, -1))
        self.txtPassword = wx.TextCtrl(self, style = wx.TE_PASSWORD)
        self.txtPassword.Bind(wx.EVT_KEY_UP, self.onPassword)

        hbox.Add(self.lblPassword, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.Add(self.txtPassword, 1, wx.ALL | wx.EXPAND, 5)
        hbox.AddSpacer(10)
        vbox.Add(hbox,0,wx.EXPAND)
        vbox.AddSpacer(10)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btnLogin = wx.Button(self, label="Login", size=wx.Size(80, -1))
        self.btnLogin.Bind(wx.EVT_BUTTON, self.onLogin)

        btnSizer.Add(self.btnLogin)
        btnSizer.AddSpacer(10)

        self.btnCancel = wx.Button(self, label="Exit", size=wx.Size(80, -1))
        self.btnCancel.Bind(wx.EVT_BUTTON, self.onCancel)

        btnSizer.Add(self.btnCancel)

        vbox.Add(btnSizer, 0, wx.ALL|wx.CENTER)

        self.SetSizer(vbox)

        self.Center()

        self.txtUsername.SetFocus()

        #for debug only
        #self.txtUsername.SetValue('admin')
        #self.txtPassword.SetValue('admin')


    def onUserName(self, event):
        kcode = event.GetKeyCode()
        if kcode == wx.WXK_RETURN or kcode == 370:
            self.txtPassword.SetFocus()

    def onPassword(self, event):
        kcode = event.GetKeyCode()
        if kcode == wx.WXK_RETURN or kcode == 370:
            self.onLogin(event)

    def onLogin(self, event):
        self.EndModal(wx.ID_OK)


    def onCancel(self, event):
        self.EndModal(wx.ID_CANCEL)


    def getLogin(self):
        username = self.txtUsername.GetValue()
        password = self.txtPassword.GetValue()

        return (username, password)


if __name__ == "__main__":
    app = wx.App()
    top = LoginPrompt(None, "")
    top.Show()
    app.MainLoop()
