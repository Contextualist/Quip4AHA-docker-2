import traceback
import logging
logging.basicConfig(level=logging.INFO)
from time import sleep
from functools import partial
import threading
import schedule
'''
from NewDoc import NewDoc
from AssignHost import AssignHost
from UpdateWeather import UpdateWeather
'''
from flask import Flask
app = Flask(__name__)


@app.route('/')
def home():
    logging.info("Flask client stimulator visits home.")
'''
@app.route('/b/<ad_hoc_host>')
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
'''
@app.errorhandler(Exception)
def handle_exception(e):
    tb = traceback.format_exc()
    logging.error(tb)
    return "<pre>%s</pre>" % (tb), e.code if 'code' in dir(e) else 500



class Scheduler(schedule.Scheduler):
    
    def __init__(self):
        schedule.Scheduler.__init__(self)
        fc = app.test_client() # Flask client stimulator
        '''self.every().friday.at("08:10").do(partial(fc.get,'/newdoc')) # Fri 16:10 UTC+8
        self.every().saturday.at("23:27").do(partial(fc.get,'/updateweather')) # Sun 07:10 UTC+8
        self.every().tuesday.at("23:27").do(partial(fc.get,'/updateweather')) # Wed 07:10 UTC+8
        '''
        self.every(3).minutes.do(partial(fc.get,'/'))
    
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