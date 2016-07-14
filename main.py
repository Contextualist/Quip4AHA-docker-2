from traceback import format_exc
from time import sleep
from threading import Thread
from schedule import Scheduler

from NewDoc import NewDoc
from AssignHost import AssignHost
from UpdateWeather import UpdateWeather

from flask import Flask, request
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
    app.logger.error(tb)
    return "<pre>%s</pre>" % tb, getattr(e,'code',500)



class Scheduler4AHA(Scheduler):
    
    def __init__(self):
        Scheduler.__init__(self)
        fc = app.test_client() # Flask client emulator
        # Schedule uses the local timezone, i.e. CST for DaoCloud.
        self.every().friday.at("16:10").do(fc.get, '/newdoc')
        self.every().sunday.at("07:27").do(fc.get, '/updateweather')
        self.every().wednesday.at("07:27").do(fc.get, '/updateweather')
    
    def run_alongside(self):
        class ScheduleThread(Thread):
            @classmethod
            def run(cls):
                while 1:
                    self.run_pending()
                    sleep(self.idle_seconds())
        sleep(3)
        td = ScheduleThread()
        td.start()

        
cron = Scheduler4AHA()
cron.run_alongside()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
