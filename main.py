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

@app.route('/a', methods=['POST', 'GET'])
def assign():
    AssignAction = AssignHost(Host=request.form['host'].split('+') if request.method=='POST' else None)
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
    return "<pre>%s</pre>" % tb, e.code if hasattr(e,'code') else 500



class Scheduler4AHA(Scheduler):
    
    def __init__(self):
        Scheduler.__init__(self)
        fc = app.test_client() # Flask client emulator
        # Schedule uses the local timezone, i.e. CST for DaoCloud.
        self.every().friday.at("16:10").do(fc.get,'/newdoc')
        self.every().sunday.at("07:27").do(fc.get,'/updateweather')
        self.every().wednesday.at("07:27").do(fc.get,'/updateweather')
    
    def run_alongside(self, interval=1):
        class ScheduleThread(Thread):
            @classmethod
            def run(cls):
                while 1:
                    self.run_pending()
                    sleep(interval)
        td = ScheduleThread()
        td.start()

        

if __name__ == '__main__':
    cron = Scheduler4AHA()
    cron.run_alongside(interval=60)
    app.run(debug=False, host='0.0.0.0', port=80)
