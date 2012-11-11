import sys, os
import getopt
import wx

from mx import DateTime

from MainFrame import MainFrame
from Database import Db
from SessionManager import SessionManager
#from ReciptPrinter import Epson, Printer


class Peripherals(object):
    ReciptPrinter = None
    ReportPrinter = None


class Vikuraa(wx.App):
    def __init__(self, db, session, peripherals, parent=None):
        self.db = db
        self.session = session
        self.peripherals = peripherals
        wx.App.__init__(self, parent)


    def OnInit(self):
        self.mainFrame = MainFrame(None, self.db, self.session, self.peripherals)
        self.mainFrame.Show()
        return True



def start(dbconnectionstring):
    db = Db(dbconnectionstring)

    session = SessionManager(db)

    peripherals = Peripherals
    
    from ReciptPrinter import ReciptPrinter
    peripherals.ReciptPrinter = ReciptPrinter
    #from EpsonEscPos import EpsonEscPos
    #peripherals.ReciptPrinter = EpsonEscPos

    app = Vikuraa(db, session, peripherals)
    app.MainLoop()


def license():
    print "Vikuraa Retail Management System"
    print "--------------------------------"
    print "Copyright (C) 2010 Ali Aafee"
    print ""


def usage():
    license()
    print "Usage:"
    print "    -h, --help"
    print "       Displays this help"
    print " "
    print "    -l, --log"
    print "       Log file for error, if not set error to stdout"
    print " "


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hl:", ["help", "log="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    log = ''
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-l", "--log"):
            log = arg

    uri = 'sqlite:' + os.path.abspath('shop.db') #+ '?debug=t'

    if log == '':
        start(uri)
    else:
        import logging
        logging.basicConfig(level=logging.DEBUG, filename=log)
        try:
            start(uri)
        except:
            logging.exception(str(DateTime.now()))
            raise


if __name__ == '__main__':
    main(sys.argv[1:])
