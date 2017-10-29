'''
Include a customized Quip client, some utilities, and timezone setting.
'''

"""Override the local timezone in the process environment"""
import os
os.environ['TZ'] = 'CST-08'
import time
try:
    time.tzset() # for UNIX only
except AttributeError:
    pass
import datetime
import sys
import argparse
import json
import threading
import websocket

from quip import QuipClient


class cache(object):

    def __init__(self, next_expr):
        self.__c = None
        self.__next_expr = next_expr
        self.__bestbefore = datetime.date.min

    def __call__(self, fn):

        def cached_fn(*args, **kwargs):
            if datetime.datetime.today().date() > self.__bestbefore:
                self.__c = fn(*args, **kwargs)
                self.__bestbefore = self.__next_expr()
            return self.__c

        return cached_fn


class QuipClient4AHA(QuipClient):
    """A customized Quip client dedicated for AHA Broadcast."""
    
    def __init__(self, conf):
        QuipClient.__init__(self, access_token=os.environ['token'])
        self.AHABC_ID = conf["folder_id"]
    
    @property
    @cache(lambda:datetime.date.max)
    def self_id(self):
        return self.get_authenticated_user()['id']

    @property
    def folder_AHABC(self):
        return self.get_folder(id=self.AHABC_ID)

    @property
    @cache(lambda:week.RecentWeekDay('next Wednesday'))
    def latest_script_id(self):
        AHABC = self.folder_AHABC
        nxtwed = week.RecentWeekDay('next Wednesday')
        title = nxtwed.strftime('%m%d')
        #lstfri = [int(time.mktime(
        #    time.strptime('%s 16:10:00' % (week.RecentWeekday('last Friday')), "%Y-%m-%d %H:%M:%S")))]
        docID = []
        for td in AHABC['children']:
            if (('thread_id' in td) and (self.get_thread(td['thread_id'])['thread']['title']==title)):
                docID.append(td['thread_id'])
        if docID == []:
            raise InvalidOperation("Script not found: There's no legitimate host script for next week's broadcast.")
        if len(docID) > 1:
            raise InvalidOperation("Redundancy Error: More than one scripts for the next broadcast are found!", 409)
        return docID[0]

    def message_feed(self, msg_handler):

        def __on_message(ws, rawmsg):
            m = json.loads(rawmsg)
            if (m['type']!='message' or m['thread']['id']!=self.latest_script_id 
                or self.self_id not in m['message'].get('mention_user_ids', [])):
                return
            m['message'].update({'thread_id':m['thread']['id']})
            try:
                msg_handler(m['message'])
            except Exception as e:
                print e

        websocket_info = self.new_websocket()
        websocket_run(websocket_info["url"], on_message=__on_message)


def parse_config():
    psr = argparse.ArgumentParser()
    psr.add_argument('-c', '--config')
    psr.add_argument('-l', '--listen', default=':')
    args = psr.parse_args()

    l = args.listen.split(':')
    sysconf = {
        'host': l[0] or '0.0.0.0',
        'port': int(l[1] or '80')
    }

    for p in ([args.config] if args.config else [])+["./config.json", "/etc/q4a/config.json"]:
        if os.path.exists(p):
            conffile = p
            confpath = os.path.dirname(conffile)
            break
    else:
        print "config file not found, exit."
        sys.exit(1)
    with open(conffile, "rb") as f:
        try:
            config = json.loads(f.read().decode('utf8'))
        except ValueError as e:
            print ('found an error while parsing config.json: %s' % e.message)
            sys.exit(1)

    tplfile = config.get("template", confpath+"/template.html")
    if not os.path.exists(tplfile):
        print "template file not found, exit."
        sys.exit(1)
    with open(tplfile, "rb") as f:
        template = f.read().decode('utf8')

    return sysconf, config, template


def websocket_run(url, on_message):
    HEARTBEAT_INTERVAL = 20

    #TODO: log
    def on_error(ws, err): print "websocket error:", err

    def on_close(ws): print "websocket disconnected"

    def on_open(ws):
        print "websocket connected"

        def run(*args):
            while True:
                time.sleep(HEARTBEAT_INTERVAL)
                ws.send(json.dumps({"type": "heartbeat"}))

        startd(run)

    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        url, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.run_forever()


def startd(fn):
    d = threading.Thread(target=fn)
    d.setDaemon(True)
    d.start()


class week(object):
    
    @classmethod
    def DaysTo(cls, TheDay, IgnoreToday=False):
        """Return the days to a specific day of last/next week.
        e.g. (assume today is May 24, Wed. IgnoreToday=False):
          >>> week.DaysTo('last Friday')
          -5
          >>> week.DaysTo('next Wednesday')
          0
        """
        argu = TheDay.split(' ')
        rel = {'last':-1, 'next':1}[argu[0].lower()]
        weekday = {'Monday':1, 'Tuesday':2, 'Wednesday':3, 'Thursday':4,
                   'Friday':5, 'Saturday':6, 'Sunday':7}[argu[1]]
        today = datetime.datetime.today().isoweekday()
        if IgnoreToday:
            return weekday - today + (rel*weekday<=rel*today) * rel * 7
        else:
            return weekday - today + (rel*weekday<rel*today) * rel * 7
    
    @classmethod
    def RecentWeekDay(cls, TheDay, IgnoreToday=False):
        '''Return the date object for a specific day of last/next week.
        e.g. (assume today is May 24, Wed. IgnoreToday=False):
          >>> repr(week.RecentWeekDay('last Friday'))
          datetime.date(2017, 5, 19)
          >>> repr(week.RecentWeekDay('next Wednesday'))
          datetime.date(2017, 5, 24)
        '''
        return datetime.datetime.today().date() + datetime.timedelta(cls.DaysTo(TheDay,IgnoreToday))


class InvalidOperation(Exception):
    """Exception for all actions that take place when the conditions are not fulfilled."""
    def __init__(self, message, http_code=202):
        Exception.__init__(self, message)
        self.code = http_code

sysconf, config, template = parse_config()
q4a = QuipClient4AHA(config)
