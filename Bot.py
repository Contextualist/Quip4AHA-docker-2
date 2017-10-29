import urllib2
import json

from quip4aha import q4a, config

payload = {
    "currentNode": "",
    "complete": None,
    "context": {},
    "parameters": [],
    "extractedParameters": {},
    "speechResponse": "",
    "intent": {},
    "input": "",
    "missingParameters": []
}

def iky_relay(msg):
    payload['input'] = msg['text'].replace('https://quip.com/%s'%q4a.self_id, '')

    req = urllib2.Request(config['iky_api'], json.dumps(payload))
    req.add_header("Content-Type", "application/json; charset=utf-8")
    rpl = json.loads(urllib2.urlopen(req).read())

    q4a.new_message(thread_id=msg['thread_id'], parts='[["system","%s"]]'%rpl['speechResponse'])

def RunChatbot():
    q4a.message_feed(iky_relay)


if __name__ == "__main__":
    RunChatbot()
