import wx
from mx import DateTime


class DateTimePickerCtrl(wx.Panel):
    def __init__(self, parent, size=wx.Size(-1, -1), showtime = True):
        wx.Panel.__init__(self, parent, size=size)
        self.showtime = showtime
        self.SetBackgroundColour('WHITE')
        self._InitCtrls()
        self.SetValue(DateTime.now())


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
        "value as mx.DateTime"

        self.DatePicker.Show()

        tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec,tm_wday,tm_yday,tm_isdst = value.tuple()

        try:
            dt = wx.DateTimeFromDMY(tm_mday,tm_mon,tm_year)
            self.DatePicker.SetValue(dt)

            self.TimePicker.SetValue("{0}:{1}:{2}".format(
                                                    str(tm_hour).zfill(2),
                                                    str(tm_min).zfill(2),
                                                    str(tm_sec).zfill(2)))

            self.mxDateTime = value
            self.Layout()
        except:
            self.DatePicker.Hide()
            self.Layout()
            self.TimePicker.SetValue(str(value))


    def GetValue(self):
        self.DateTime = self.DatePicker.GetValue()

        tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec,tm_wday,tm_yday,tm_isdst = self.mxDateTime.tuple()

        if not self.showtime:
            tm_hour = 0
            tm_min = 0
            tm_sec = 0

        value = DateTime.DateTime(
                    self.DateTime.GetYear(),
                    self.DateTime.GetMonth(),
                    self.DateTime.GetDay(),
                    tm_hour,
                    tm_min,
                    tm_sec)

        self.mxDateTime = value
        return value




if __name__ == "__main__":
    "For testing"
    app = wx.App()
    frame = wx.Frame(None)
    pnl = DateTimePickerCtrl(frame)
    sz = wx.BoxSizer(wx.VERTICAL)
    sz.Add(pnl,0,wx.ALL|wx.EXPAND,10)
    frame.SetSizer(sz)
    frame.Show()
    value = DateTime.DateTime(2012,11,6,1,3,3)
    pnl.SetValue(value)
    print pnl.GetValue()
    app.MainLoop()
