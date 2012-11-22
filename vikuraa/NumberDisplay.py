import wx




class NumberDisplay(wx.Panel):
    def __init__(self, parent, rows, first_row_big=True, size=wx.Size(-1,-1)):
        wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER, size=size)

        self.SetBackgroundColour('WHITE')

        self.label = {}
        self.value = {}

        gs = wx.FlexGridSizer(len(self.label), 2, 0, 0)

        self.fontBig = wx.Font(
                        24,
                        family=wx.MODERN,
                        style=wx.NORMAL,
                        weight=wx.FONTWEIGHT_BOLD)
        self.fontMed = wx.Font(
                        16,
                        family=wx.MODERN,
                        style=wx.NORMAL,
                        weight=wx.FONTWEIGHT_BOLD)

        for i in range(len(rows)):
            self.label[i] = wx.StaticText(
                            self,
                            label = rows[i],
                            size = wx.Size(-1,-1),
                            style=0)

            self.value[i] = wx.StaticText(
                            self,
                            label = '',
                            size = wx.Size(-1,-1),
                            style=0)
            if i == 0:
                if first_row_big == True:
                    self.value[i].SetFont(self.fontBig)
                else:
                    self.value[i].SetFont(self.fontMed)
            else:
                self.value[i].SetFont(self.fontMed)

            gs.Add(self.label[i],
                    proportion=0,
                    flag=wx.ALL| wx.ALIGN_CENTER_VERTICAL,
                    border=5)

            gs.Add(self.value[i],
                    proportion=0,
                    flag=wx.ALL| wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT,
                    border=5)


        for i in range(len(self.label)):
            gs.AddGrowableRow(i)

        gs.AddGrowableCol(0)
        self.SetSizer(gs)


    def SetValue(self, row, value):
        self.value[row].SetLabel(value)
        self.Layout()


    def GetStaticText(self, row):
        return self.value[row]




if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    pnl = NumberDisplay(frame,
            ['Total Due',
             'Incl. 6% GST',
             'Tender',
             'Balance'])
    pnl.SetValue(0, 'Rf 9412.00')
    sz = wx.BoxSizer()
    sz.Add(pnl,1,wx.ALL|wx.EXPAND,10)
    frame.SetSizer(sz)
    frame.Show()
    app.MainLoop()


