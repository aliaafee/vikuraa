import usb

from ReciptPrinter import ReciptPrinter


class EpsonEscPos(ReciptPrinter):
    '''
    Epson ESC/POS Printer
    ---------------------
    To use, enable direct printing from the printer settings,
    and install a supported backend for PyUSB.

    Always call End() when you are done printing

    Printer commands from:
    http://nicholas.piasecki.name/blog/wp-content/uploads/2009/12/ESC-POS-Command-Guide.pdf
    and
    http://code.google.com/p/python-escpos
    (not all commands are implemented yet)

    Raises IOError if printer not found/not working on init
    '''
    # Feed control sequences
    CTL_LF    = '\x0a'             # Print and line feed
    CTL_FF    = '\x0c'             # Form feed
    CTL_CR    = '\x0d'             # Carriage return
    CTL_HT    = '\x09'             # Horizontal tab
    CTL_VT    = '\x0b'             # Vertical tab
    # Feed control
    P_FEED_N_LINE  = '\x1b\x64'    # Print the data in buffer and feed n Lines append n, where 0<=n<=255
    P_RFEED_N_LINE = '\x1b\x65'    # Print the data in buffer and reverse feed n Lines append n, where 0<=n<=255
    # Printer hardware
    HW_INIT   = '\x1b\x40'         # Clear data in buffer and reset modes
    HW_SELECT = '\x1b\x3d\x01'     # Printer select
    HW_RESET  = '\x1b\x3f\x0a\x00' # Reset printer hardware
    # Cash Drawer
    CD_KICK_2 = '\x1b\x70\x00'     # Sends a pulse to pin 2 []
    CD_KICK_5 = '\x1b\x70\x01'     # Sends a pulse to pin 5 []
    # Paper
    PAPER_FULL_CUT  = '\x1d\x56\x00' # Full cut paper
    PAPER_PART_CUT  = '\x1d\x56\x01' # Partial cut paper
    # Text Color Only works on TM-J2000/TM-J2100/TM-U200/TMU210/TM-U220/TM-U230
    TXT_COLOR_1     = '\x1b\x72\x00' # Select text color 1(black)
    TXT_COLOR_2     = '\x1b\x72\x01' # Select text color 2(red)
    # Text format
    TXT_NORMAL      = '\x1b\x21\x00' # Normal text
    TXT_2HEIGHT     = '\x1b\x21\x10' # Double height text
    TXT_2WIDTH      = '\x1b\x21\x20' # Double width text
    TXT_UNDERL_OFF  = '\x1b\x2d\x00' # Underline font OFF
    TXT_UNDERL_ON   = '\x1b\x2d\x01' # Underline font 1-dot ON
    TXT_UNDERL2_ON  = '\x1b\x2d\x02' # Underline font 2-dot ON
    TXT_BOLD_OFF    = '\x1b\x45\x00' # Bold font OFF
    TXT_BOLD_ON     = '\x1b\x45\x01' # Bold font ON
    TXT_FONT_A      = '\x1b\x4d\x00' # Font type A
    TXT_FONT_B      = '\x1b\x4d\x01' # Font type B
    TXT_ALIGN_LT    = '\x1b\x61\x00' # Left justification
    TXT_ALIGN_CT    = '\x1b\x61\x01' # Centering
    TXT_ALIGN_RT    = '\x1b\x61\x02' # Right justification
    # Barcode format
    BARCODE_TXT_OFF = '\x1d\x48\x00' # HRI barcode chars OFF
    BARCODE_TXT_ABV = '\x1d\x48\x01' # HRI barcode chars above
    BARCODE_TXT_BLW = '\x1d\x48\x02' # HRI barcode chars below
    BARCODE_TXT_BTH = '\x1d\x48\x03' # HRI barcode chars both above and below
    BARCODE_FONT_A  = '\x1d\x66\x00' # Font type A for HRI barcode chars
    BARCODE_FONT_B  = '\x1d\x66\x01' # Font type B for HRI barcode chars
    BARCODE_HEIGHT  = '\x1d\x68\x64' # Barcode Height [1-255]
    BARCODE_WIDTH   = '\x1d\x77\x03' # Barcode Width  [2-6]
    BARCODE_UPC_A   = '\x1d\x6b\x00' # Barcode type UPC-A
    BARCODE_UPC_E   = '\x1d\x6b\x01' # Barcode type UPC-E
    BARCODE_EAN13   = '\x1d\x6b\x02' # Barcode type EAN13
    BARCODE_EAN8    = '\x1d\x6b\x03' # Barcode type EAN8
    BARCODE_CODE39  = '\x1d\x6b\x04' # Barcode type CODE39
    BARCODE_ITF     = '\x1d\x6b\x05' # Barcode type ITF
    BARCODE_NW7     = '\x1d\x6b\x06' # Barcode type NW7
    # Image format
    S_RASTER_N      = '\x1d\x76\x30\x00' # Set raster image normal size
    S_RASTER_2W     = '\x1d\x76\x30\x01' # Set raster image double width
    S_RASTER_2H     = '\x1d\x76\x30\x02' # Set raster image double height
    S_RASTER_Q      = '\x1d\x76\x30\x03' # Set raster image quadruple

    paper_width = 33

    device = None

    def __init__(self):

        self.device = usb.core.find(idVendor=0x04b8, idProduct=0x0202)

        if self.device == None:
            raise IOError("Printer not found")
            return

        try:
            self.device.set_configuration()
        except usb.core.USBError as e:
            print "Could not set configuration: %s" % str(e)
            raise IOError("Printer configuration error")

        self._raw(self.HW_INIT)

        self.SetSmallFont()


    def __del__(self):
        self.device = None
        return


    def _raw(self, data):
        self.device.write(1, data)


    def _cut(self):
        self._raw(self.PAPER_FULL_CUT)


    def SetSmallFont(self):
        self._raw(self.TXT_FONT_B)
        self.paper_width = 40


    def SetBigFont(self):
        self._raw(self.TXT_FONT_A)
        self.paper_width = 33


    def FeedForward(self, lines=1):
        if type(lines) == int:
            if lines > 0 and lines <= 255:
                self._raw(self.P_FEED_N_LINE + chr(lines))


    def FeedReverse(self, lines=1):
        if type(lines) == int:
            if lines > 0 and lines <= 255:
                self._raw(self.P_RFEED_N_LINE + chr(lines))


    def SetColor_black(self):
        self._raw(self.TXT_COLOR_1)


    def SetColor_red(self):
        self._raw(self.TXT_COLOR_2)


    def SetBig_on(self):
        self._raw(self.TXT_BOLD_ON)
        self._raw(self.TXT_2HEIGHT)
        self.SetBigFont()


    def SetBig_off(self):
        self._raw(self.TXT_BOLD_OFF)
        self._raw(self.TXT_NORMAL)
        self.SetSmallFont()


    def Line_b(self):
        self.FeedForward(1)


    def End(self):
        self.FeedForward(2)
        self.FeedForward(2)
        self.FeedForward(2)
        self._cut()
        self.FeedReverse(2)


    def Barcode(self, code):
        self._raw('\n')
        self._raw(self.TXT_ALIGN_CT)
        self._raw(self.BARCODE_HEIGHT)
        self._raw(self.BARCODE_WIDTH)
        self._raw(self.BARCODE_FONT_A)
        self._raw(self.BARCODE_TXT_OFF)

        self._raw(self.BARCODE_UPC_A)
        #self._raw(self.BARCODE_UPC_E)
        #self._raw(self.BARCODE_EAN13)
        #self._raw(self.BARCODE_EAN8)
        #self._raw(self.BARCODE_CODE39)
        #self._raw(self.BARCODE_ITF)
        #self._raw(self.BARCODE_NW7)

        self._raw(code)
        self._raw('\n')




if __name__ == "__main__":
    printer = EpsonEscPos()
    printer.TestPageShort()
