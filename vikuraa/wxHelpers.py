import wx

def LabeledCtrl(parent, label, 
                        labelalign = wx.ALIGN_RIGHT, 
                        size = wx.Size(-1, -1),
                        labelexpand = False,
                        ctrl = wx.TextCtrl):
    
    stctrl = wx.StaticText(parent, 
                            label = label, 
                            size = wx.Size(100,-1), 
                            style=labelalign | wx.ALL)
    txtctrl = ctrl(parent, size=size)
    txtctrl.label = stctrl
    hbox = wx.BoxSizer(wx.HORIZONTAL)
    
    if labelexpand:
        hbox.Add(stctrl, 1, 
                        wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        hbox.Add(txtctrl, 0, wx.ALL, 5)
    else:
        hbox.Add(stctrl,0, wx.ALL, 5)
        hbox.Add(txtctrl, 1, wx.EXPAND|wx.ALL, 5)
        
    return txtctrl, hbox
    
    
def LabelCtrl(parent, label, ctrl,
                size = wx.Size(-1, -1), 
                labelalign = wx.ALIGN_RIGHT, 
                labelexpand = False):
    stctrl = wx.StaticText(parent, 
                            label = label, 
                            size = wx.Size(-1,-1), 
                            style=labelalign | wx.ALL)
    ctrl.SetSize(size)
    ctrl.label = stctrl
    hbox = wx.BoxSizer(wx.HORIZONTAL)
    if labelexpand:
        hbox.Add(stctrl, 1, 
                        wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        hbox.Add(ctrl, 0, wx.ALL, 5)
    else:
        hbox.Add(stctrl,0, wx.ALL, 5)
        hbox.Add(ctrl, 1, wx.EXPAND|wx.ALL, 5)
        
    return hbox
    
    
def BoxSizerVerticalAdd(Ctrls):
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    for Ctrl in Ctrls:
        sizer.Add(Ctrl ,0 ,wx.EXPAND | wx.ALL, 5)
        
    return sizer
