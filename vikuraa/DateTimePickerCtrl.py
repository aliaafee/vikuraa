import wx
from datetime import datetime


class DateTimePickerCtrl(wx.Panel):
    def __init__(self, parent, size=wx.Size(-1, -1), showtime = True):
        wx.Panel.__init__(self, parent, size=size)
        self.showtime = showtime
        self.SetBackgroundColour('WHITE')
        self._InitCtrls()
        self.SetValue(datetime.now())


    def _InitCtrls(self):
        self.DatePicker = wx.DatePickerCtrl(self, style=wx.DP_DROPDOWN|wx.NO_BORDER)
        self.TimePicker = wx.TextCtrl(self, style=wx.SIMPLE_BORDER)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.DatePicker, 1, wx.ALL | wx.EXPAND, 0)
        sizer.Add(self.TimePicker, 1, wx.ALL | wx.EXPAND, 0)
        
        self.SetSizer(sizer)
        if not self.showtime:
            self.TimePicker.Hide()


    def SetValue(self, value):
        "value as python datetime"
        self.value = value

        wxdt = wx.DateTimeFromDMY(self.value.day, self.value.month-1, self.value.year)
        self.DatePicker.SetValue(wxdt)

        self.TimePicker.SetValue("{0}:{1}:{2}".format(
                                                str(self.value.hour).zfill(2),
                                                str(self.value.minute).zfill(2),
                                                str(value.second).zfill(2)))


    def GetValue(self):
        wxdt = self.DatePicker.GetValue()

        if not self.showtime:
            tm_hour = 0
            tm_min = 0
            tm_sec = 0
        else:
            tm_hour = self.value.hour
            tm_min = self.value.minute
            tm_sec = self.value.second

        self.value = datetime(
                    wxdt.Year,
                    wxdt.Month+1,
                    wxdt.Day,
                    tm_hour,
                    tm_min,
                    tm_sec)

        return self.value




if __name__ == "__main__":
    "For testing"
    app = wx.App()
    frame = wx.Frame(None)
    pnl = DateTimePickerCtrl(frame)
    sz = wx.BoxSizer(wx.VERTICAL)
    sz.Add(pnl,0,wx.ALL|wx.EXPAND,10)
    frame.SetSizer(sz)
    frame.Show()
    print pnl.GetValue()
    app.MainLoop()
