from flask import Flask, request, send_from_directory
import requests
import json
from flask_socketio import SocketIO, send, emit
import elasticsearch

#es = ES('http://search-ccas2-wkp2mz4ca2wjtxn6kvlo6gw6vi.us-east-1.es.amazonaws.com')
es = elasticsearch.Elasticsearch([{'host': "search-ccas2-wkp2mz4ca2wjtxn6kvlo6gw6vi.us-east-1.es.amazonaws.com",'port':80, 'use_ssl':False}])

application = Flask(__name__,static_folder='static')
socketio = SocketIO(application)
curq = 'magicword'

def msg_process(msg, tstamp):
    js = json.loads(msg)
    print (js)
    print ("curq",curq)
    es.index(index='test-index',doc_type='status',body=js)
    if curq in js['status'].lower():
        print ("emitting second")
        socketio.emit('second',{"stuff":'New Tweet!'})

# routing for static files like the bootstrap css file we use
@application.route('/static/<path:filename>')
def send_css(filename):
  return send_from_directory('/static/',filename)


@socketio.on('first')
def handle_my_custom_event(curquery):
    global curq
    print('received query: ' + str(curquery))
    curq = str(curquery)



@application.route('/', methods = ['GET', 'POST', 'PUT'])

def sns():
    # AWS sends JSON with text/plain mimetype
    try:
        print("sssssssssssssssssssssssss")
        js = json.loads(request.data)
    except:
        pass

    hdr = request.headers.get('X-Amz-Sns-Message-Type')
    # subscribe to the SNS topic
    if hdr == 'SubscriptionConfirmation' and 'SubscribeURL' in js:
        r = requests.get(js['SubscribeURL'])

    if hdr == 'Notification':
        msg_process(js['Message'], js['Timestamp'])
    return send_from_directory('static/',"index.html")
    # return 'OK\n'

if __name__ == '__main__':
    # socketio.run(app,
    #     host = "localhost",
    #     port = 80,
    #     debug = True
    # )
    application.debug=True
    application.run()
