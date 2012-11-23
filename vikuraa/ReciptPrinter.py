import sys


class ReciptPrinter(object):
    ALIGN_L = 0
    ALIGN_R = 1
    ALIGN_C = 2

    paper_width = 33

    def __init__(self):
        self.SetColor_black()


    def _raw(self, data):
        sys.stdout.write(data)


    def _text(self, text):
        self._raw(str(text))


    def Line_b(self):
        self._raw('\n')


    def End(self):
        print "\x1b[0m"


    def Line_u(self, line):
        self._text(line+'\n')
        ul = ''
        for i in range(len(line)):
            ul += '-'
        self._text(ul+'\n')


    def Hr(self):
        ul = ''
        for i in range(self.paper_width):
            ul += '-'
        self._text(ul+'\n')


    def Line_l(self, line, trimtopagewidth = True):
        if trimtopagewidth:
            line = line[:self.paper_width]

        self._text(line + '\n')


    def Line_r(self, line):
        line = line[:self.paper_width]

        line = line.rjust(self.paper_width)
        self._text(line + '\n')


    def Line_c(self, line):
        line = line[:self.paper_width]

        lpad = (self.paper_width - len(line))/2
        line = line.rjust(lpad+(len(line)))

        self._text(line + '\n')


    def Table(self, columns):
        for col in columns:
            col_title, align, values = col
            maxwidth = len(col_title)
            for val in values:
                l = len(val)
                if l > maxwidth:
                    maxwidth = l
            col.append(maxwidth)

        totalmaxwidth2 = 0
        for i in range(len(columns)):
            if i != 0:
                totalmaxwidth2 += columns[i][3]
        columns[0][3] = self.paper_width - totalmaxwidth2 - (len(columns)-1)

        lines = []
        title_col = ''
        for col in columns:
            col_title, align, values, maxWidth = col
            if col_title != '':
                t = col_title[0:maxWidth]
                if align == self.ALIGN_R:
                    t = t.rjust(maxWidth)
                else:
                    t = t.ljust(maxWidth)
                if title_col == '':
                    title_col +=  t
                else:
                    title_col += ' ' + t

            for i in range(len(values)):
                val = values[i][0:maxWidth]
                if align == self.ALIGN_R:
                    val = val.rjust(maxWidth)
                else:
                    val = val.ljust(maxWidth)

                try:
                    lines[i] += ' ' + val
                except IndexError:
                    lines.append(val)
        if title_col != '':
            self.Line_l(title_col)
        for line in lines:
            self.Line_l(line)


    def SetColor_black(self):
        self._raw('\x1b[47m')
        self._raw('\x1b[30m')

    def SetColor_red(self):
        self._raw( '\x1b[47m')
        self._raw( '\x1b[31m')

    def SetBig_on(self):
        self._raw( '\x1b[1m')

    def SetBig_off(self):
        self._raw( '\x1b[22m')

    def Barcode(self, code):
        self._raw('Barcode:')
        self._raw(code)
        self._raw('\n')

    def TestPage(self):
        self.Line_c('TITLE')
        self.Line_c('Some Street')
        self.Line_c('Z. Somewheresdhoo')
        self.Line_c('Somedives')
        self.Line_b()
        self.Line_c('INVOICE')
        self.Line_b()
        self.Table([
            ['', self.ALIGN_L, ['2012-10-10 12:55:12.00']],
            ['', self.ALIGN_R, ['ID:1000000000000']]])
        self.Line_b()
        self.Line_l('Billed to: Some guy somewhere, with a long address', trimtopagewidth=False)
        self.Line_b()
        a = ['Tuna', 'Eggs', 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX']
        b = ['1', '1', '3']
        c = ['10.00', '1000000.00', '11.00']
        d = ['1000000.00', '1313.00', '13311.00']

        self.Table([
            ['Desc' , self.ALIGN_L, a],
            ['Qty' , self.ALIGN_R, b],
            ['Rate' , self.ALIGN_R, c],
            ['Total' , self.ALIGN_R, d]])
        self.Line_b()
        self.Line_l('')
        self.SetBig_on()
        self.SetColor_red()
        self.Line_r('Total:   Rf ' + ('1000000.00'.rjust(10)))
        self.SetColor_black()
        self.SetBig_off()
        self.Line_r('Tax:     Rf ' + ('1000000.00'.rjust(10)))
        self.Line_r('Tender:  Rf ' + ('1000000.00'.rjust(10)))
        self.Line_r('Balance: Rf ' + ('1000000.00'.rjust(10)))
        self.Line_l('')
        self.Line_c('Thank You')

        self.End()

    def TestPageShort(self):
        self.Line_c('Centered Text')
        self.Line_l('00000111112222233333444445555566666777778888899999')
        self.SetBig_on()
        self.Line_l('Big Red Text')
        self.SetBig_off()
        self.Barcode('12345')
        self.End()




if __name__ == "__main__":
    printer = ReciptPrinter()
    printer.TestPage()
