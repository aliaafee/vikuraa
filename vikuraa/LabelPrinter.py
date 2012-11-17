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
BC_CODE128 = '1'

HR_YES = 'B'
HR_NO = 'N'


class LabelPaper(object):
    label_cols  = 3
    label_rows  = 1

    #_page_width   = 140 #mm
    #_page_height  = 27  #mm
    _label_height = 25 #mm
    _label_width  = 32 #mm
    _label_border = 2 #mm

    dpmm = 8 #dots per mm

    def __init__(self, dpmm):
        self.dpmm = dpmm

        self.label_width = self._label_width * self.dpmm
        self.label_height = self._label_height * self.dpmm
        self.label_border = self._label_border * self.dpmm
        #self.page_width = self._page_width * self.dpmm
        #self.page_height = self._page_height * self.dpmm



class Zebra(object):
    '''
    Zebra EPL Label printing
    '''
    dpmm = 8

    def __init__(self, paper):
        self.paper = paper(self.dpmm)
        self._labelTitle = ''


    def _raw(self, data):
        sys.stdout.write(data)


    def _text(self, x, y, text,
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
        return data


    def _barcode(self, x, y, code, height,
                    narrowbar=2, widebar=5, bctype=BC_CODE128, humanreadable=HR_NO, rotation=ROT_NORMAL):
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


        return data


    def _print_page(self, content, count=1):
        page = 'N\n'
        page += content
        page += 'P{0}\n'.format(count)
        self._raw(page)


    def _print_one(self, x, y, itemid, itembc, itemdesc, itemselling, itemtax):
        result  = self._text(x + 0, y + 0, str(self._labelTitle))
        result += self._barcode(x + ((self.paper.label_width - 160)/2), y + 55, itembc, 80)
        result += self._text(x + 40, y + 160, str(itemdesc))
        result += self._text(x + 40, y + 175, str(itemid))
        result += self._text(x + 40, y + 190, str(itemselling))
        return result


    def _fill_page(self, itemid, itembc, itemdesc, itemselling, itemtax, count):
        page = ''
        c = 0
        for r in range(self.paper.label_rows):
            y = self.paper.label_border + (r * (self.paper.label_height + self.paper.label_border))
            for c in range(self.paper.label_cols):
                x = self.paper.label_border + (c * (self.paper.label_width + self.paper.label_border))
                page += self._print_one(x, y, itemid, itembc, itemdesc, itemselling, itemtax)
                c += 1

                if c >= count:
                    break
            if c >= count:
                break
        return page        


    def SetLabelTitle(self, title):
        self._labelTitle = title
        

    def PrintLabel(self, itemid, itembc, itemdesc, itemselling, itemtax, count):
        lblperpage = self.paper.label_cols * self.paper.label_rows
        pagecount = abs(count/lblperpage)
        remainder = count%lblperpage
        
        if pagecount >= 1:                
            page = self._fill_page(itemid, itembc, itemdesc, itemselling, itemtax, count)
            print "print {0} pages each with {1} labels".format(pagecount, lblperpage)
            self._print_page(page, pagecount)
            
        if remainder >= 1:
            page = self._fill_page(itemid, itembc, itemdesc, itemselling, itemtax, remainder)
            print "printing {0} remaining lbls".format(remainder)
            self._print_page(page)



class ZebraUsb(Zebra):
    '''
    Zebra usb label printer
    '''
    idVendor  = 0
    idProduct = 0
    dpmm = 8

    def __init__(self, paper):
        Zebra.__init__(self, paper)

        self.device = usb.core.find(idVendor=self.idVendor, idProduct=self.idProduct)

        if self.device == None:
            raise IOError("Printer {0}:{1} not found".format(
                            hex(self.idVendor), hex(self.idProduct)))
            return

        try:
            self.device.set_configuration()
        except usb.core.USBError as e:
            print "Could not set configuration: %s" % str(e)
            raise IOError("Printer configuration error")


    def _raw(self, data):
        self.device.write(1, data)




class BirchBP744Plus(ZebraUsb):
    '''
    Birch BP-744 Plus
    '''
    idVendor  = 0x1203
    idProduct = 0x0133
    dpmm = 8




if __name__ == "__main__":
    print "starting"
    #printer = BirchBP744Plus(paper)
    printer = Zebra(LabelPaper)
    printer.SetLabelTitle('Sash')
    printer.PrintLabel(1234, 12345, 'Shirt', 'Rf 106.00', 'Rf 6.00', 9)
