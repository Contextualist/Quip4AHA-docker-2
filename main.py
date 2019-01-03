from quip4aha import sysconf, startd, cleanupd, week # quip4aha has set the CST timezone
from NewDoc import NewDoc
from AssignHost import AssignHost
from UpdateWeather import UpdateWeather
#from Bot import Chatbot # __main__ only

from traceback import format_exc
from logging import getLogger
import logging
logging.basicConfig(level=logging.INFO)
from datetime import datetime
from time import sleep

from flask import Flask, request
from schedule import Scheduler


app = Flask(__name__)

@app.route('/')
def home():
    return "Everything's 200 OK."

@app.route('/a')
def assign():
    AssignAction = AssignHost()
    return AssignAction.do()

@app.route('/newdoc')
def newdoc():
    NewDocAction = NewDoc()
    return NewDocAction.do()

@app.route('/updateweather')
def updateweather():
    UpdateAction = UpdateWeather()
    return UpdateAction.do()

@app.errorhandler(Exception)
def handle_exception(e):
    tb = format_exc()
    app.logger.error(datetime.today().strftime('%m%d(%w)%H {}').format(tb.replace('\n','\n--- ')))
    return "<pre>%s</pre>" % tb, getattr(e,'code',500)


class Scheduler4AHA(Scheduler):
    
    def __init__(self):
        Scheduler.__init__(self)
        fc = app.test_client() # Flask client emulator
        from Bot import Chatbot
        cb = Chatbot()
        # Schedule uses the local timezone, which has been set to CST.
        self.every().friday.at("16:10").do(fc.get, '/newdoc')
        self.every().sunday.at("07:27").do(fc.get, '/updateweather')
        j = self.every().tuesday.at("09:00").do(startd, cb.run, cb.quit)
        if week.DaysTo('last Tuesday') == 0:
            j.run()
        self.every().tuesday.at("22:00").do(cb.quit)
        self.every().wednesday.at("07:27").do(fc.get, '/updateweather')
    
    def run(self):
        while 1:
            self.run_pending()
            while self.idle_seconds > 0:
                sleep(self.idle_seconds)

        
if __name__ == '__main__':
    startd(Scheduler4AHA().run)
    app.run(host=sysconf['host'], port=sysconf['port'])
    cleanupd()
