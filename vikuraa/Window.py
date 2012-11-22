import wx

class VWindow(wx.Panel):
    def __init__(self, parent, title, logic):
        self.title = title
        self.parent = parent
        self.Logic = logic
        self.icon = None
        self.toolbar = None
        wx.Panel.__init__(self, parent)
        self.GlueCallBack()
        self.InitToolbar()
        self.InitControls()
        self.GlueLogic()

        self.Logic.Start()


    def AddToAuiNotebook(self, notebook):
        notebook.AddPage(self, self.title)
        pageid = notebook.GetPageIndex(self)
        if self.icon != None:
            notebook.SetPageBitmap(pageid, self.icon)
        notebook.SetSelection(pageid)
        self.DefaultFocus()


    def Layout1(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        if self.toolbar != None:
            sizer.Add(self.toolbar, 0, wx.ALL|wx.EXPAND, 0)
        self.SetSizer(sizer)
        return sizer


    def Layout2(self):
        top = wx.BoxSizer(wx.VERTICAL)
        gridr = wx.FlexGridSizer(cols=2)
        gridl = wx.FlexGridSizer(cols=2)
        gridr.AddGrowableCol(1)
        gridl.AddGrowableCol(1)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(gridl, 1, wx.ALL| wx.EXPAND)
        hbox.Add(gridr, 1, wx.ALL| wx.EXPAND)
        if self.toolbar != None:
            top.Add(self.toolbar, 0, wx.ALL|wx.EXPAND, 0)
        top.Add(hbox,0, wx.ALL| wx.EXPAND,0)
        self.SetSizer(top)
        return gridl, gridr, top


    def LabeledTextCtrls(self, sizer, labels, style):
        ctrls = []
        for label in labels:
            ctrl = wx.TextCtrl(self, style=style)
            lbl = wx.StaticText(self, label=label)
            ctrl.label = lbl
            sizer.Add(lbl, 0, wx.ALL, 3)
            sizer.Add(ctrl, 0, wx.ALL| wx.EXPAND, 3)
            ctrls.append(ctrl)
        return ctrls


    def GlueCallBack(self):
        pass

    def GlueLogic(self):
        pass

    def InitToolbar(self):
        pass

    def InitControls(self):
        pass


    def DefaultFocus(self):
        pass


    def IsSaved(self):
        return True

