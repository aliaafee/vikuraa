import sys, os
import getopt
import wx

from datetime import datetime

from MainFrame import MainFrame
import Database
from SessionManager import SessionManager


class Peripherals(object):
    ReciptPrinter = None
    ReportPrinter = None


class Vikuraa(wx.App):
    def __init__(self, session, peripherals, parent=None):
        self.session = session
        self.peripherals = peripherals
        wx.App.__init__(self, parent)


    def OnInit(self):
        self.mainFrame = MainFrame(None, self.session, self.peripherals)
        self.mainFrame.Show()
        return True


def start(dbconnectionstring, username, password):
    Database.StartEngine(dbconnectionstring)

    session = SessionManager()
    
    if username != '' and password != '':
        if session.Login(username, password):
            print "Login success"
        else:
            print "Login Error Invalid Username/Password"

    peripherals = Peripherals

    from ReciptPrinter import ReciptPrinter
    peripherals.ReciptPrinter = ReciptPrinter

    #from EpsonEscPos import EpsonEscPos
    #peripherals.ReciptPrinter = EpsonEscPos
    
    app = Vikuraa(session, peripherals)
    
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
    print "    -u, --user"
    print "       Username to login"
    print " "
    print "    -p, --password"
    print "       Password to login"
    print " "
    print "    -l, --log"
    print "       Log file for error, if not set error to stdout"
    print " "


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hl:u:p:", ["help", "log=", "user=", "password="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    log = ''
    username = ''
    password = ''
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-l", "--log"):
            log = arg
        elif opt in ("-u", "--user"):
            username = arg 
        elif opt in ("-p", "--password"):
            password = arg

    uri = 'sqlite:///' + os.path.abspath('shop.db')

    if log == '':
        start(uri, username, password)
    else:
        "Log all errors to log file"
        import logging
        logging.basicConfig(level=logging.DEBUG, filename=log)
        try:
            start(uri)
        except:
            logging.exception(str(datetime.now()))
            raise


if __name__ == '__main__':
    main(sys.argv[1:])
