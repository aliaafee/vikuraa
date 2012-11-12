import usb
import sys

ROT_NORMAL = '0'
ROT_90 = '1'
ROT_180 = '2'
ROT_270 = '3'

FONT_1 = '1'
FONT_2 = '2'
FONT_3 = '3'
FONT_4 = '4'
FONT_5 = '5'

REV_NORMAL = 'N'
REV_REVERSE = 'R'

BC_CODE39 = '3'

HR_YES = 'B'
HR_NO = 'N'


class ZebraUSB(object):
    def __init__(self):
        #get idvendor and id product
        self.device = usb.core.find(idVendor=0x04b8, idProduct=0x0202)

        if self.device == None:
            raise IOError("Printer not found")
            return

        try:
            self.device.set_configuration()
        except usb.core.USBError as e:
            print "Could not set configuration: %s" % str(e)
            raise IOError("Printer configuration error")


    def _raw(self, data):
        self.device.write(1, data)


    def StartPage(self):
        self._raw('N\n')


    def EndPage(self):
        self._raw('P1\n')


    def Text(self, x, y, text,
                rotation=ROT_NORMAL, font=FONT_1,
                hmult=1, vmult=1, rev=REV_NORMAL):
        if text == '':
            return

        text = text.replace("\\", "\\\\")
        text = text.replace('"',"\\\"")

        data = 'A{p1},{p2},{p3},{p4},{p5},{p6},{p7},"{data}"\n'.format(
                        p1=x,
                        p2=y,
                        p3=rotation,
                        p4=font,
                        p5=hmult,
                        p6=vmult,
                        p7=rev,
                        data=text)
        self._raw(data)


    def BarCode(self, x, y, code, height,
                    narrowbar=3, widebar='Y', bctype=BC_CODE39, humanreadable=HR_NO, rotation=ROT_NORMAL):
        data='B{p1},{p2},{p3},{p4},{p5},{p6},{p7},{p8},"{data}"\n'.format(
                    p1=x,
                    p2=y,
                    p3=rotation,
                    p4=bctype,
                    p5=narrowbar,
                    p6=widebar,
                    p7=height,
                    p8=humanreadable,
                    data=code
                    )
        self._raw(data)



    def TestPage(self):
        self.StartPage()
        self.Text(0,0, '"Hello"')
        self.BarCode(0,10, 12345, 10)
        self.EndPage()


if __name__ == "__main__":
    p = ZebraUSB()
    p.TestPage()