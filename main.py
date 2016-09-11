from NewDoc import NewDoc # quip4aha has set the CST timezone
from AssignHost import AssignHost
from UpdateWeather import UpdateWeather

from traceback import format_exc
from logging import getLogger
import logging
logging.basicConfig(level=logging.INFO)
from datetime import datetime
from time import sleep
from threading import Thread

from flask import Flask, request
from schedule import Scheduler


app = Flask(__name__)

@app.route('/')
def home():
    return "Everything's 200 OK."

@app.route('/a')
def assign():
    AssignAction = AssignHost(Host=request.args.get('host','').split()) # ''.split() => []
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
        # Schedule uses the local timezone, which has been set to CST.
        self.every().friday.at("16:10").do(fc.get, '/newdoc')
        self.every().sunday.at("07:27").do(fc.get, '/updateweather')
        self.every().wednesday.at("07:27").do(fc.get, '/updateweather')
    
    def run_alongside(self):
        class ScheduleThread(Thread):
            @classmethod
            def run(cls):
                while 1:
                    self.run_pending()
                    while self.idle_seconds > 0:
                        sleep(self.idle_seconds)
        td = ScheduleThread()
        td.start()

        
cron = Scheduler4AHA()
cron.run_alongside()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
