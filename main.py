import traceback
from time import sleep
from functools import partial
import threading
import schedule

from NewDoc import NewDoc
from AssignHost import AssignHost
from UpdateWeather import UpdateWeather

from flask import Flask
app = Flask(__name__)


@app.route('/')
def home():
    return "Everything's 200 OK."

@app.route('/a/<ad_hoc_host>')
def assign(ad_hoc_host):
    AssignAction = AssignHost(Host=ad_hoc_host.split('+'))
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
    tb = traceback.format_exc()
    app.logger.error(tb)
    return "<pre>%s</pre>" % (tb), e.code if 'code' in dir(e) else 500



class Scheduler(schedule.Scheduler):
    
    def __init__(self):
        schedule.Scheduler.__init__(self)
        fc = app.test_client() # Flask client stimulator
        # Schedule uses the local timezone, i.e. CST for DaoCloud.
        self.every().friday.at("16:10").do(partial(fc.get,'/newdoc'))
        self.every().sunday.at("07:27").do(partial(fc.get,'/updateweather'))
        self.every().wednesday.at("07:27").do(partial(fc.get,'/updateweather'))
    
    def run_sidelong(self, interval=1):
        class ScheduleThread(threading.Thread):
            @classmethod
            def run(cls):
                while 1:
                    self.run_pending()
                    sleep(interval)
        td = ScheduleThread()
        td.start()

        

if __name__ == '__main__':
    cron = Scheduler()
    cron.run_sidelong(interval=60)
    app.run(debug=False, host='0.0.0.0', port=80)
