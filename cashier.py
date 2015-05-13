#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request
import requests
import json
import sys
import thread
import Queue
import time
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

customerQueue = Queue.Queue()
currently_serving = 0
appPort = sys.argv[1]
app = Flask(__name__)
customer_string = 'Customer: '
clientInfo = {}
cust_id = 0

messages = [
    {
        'customer_id':1,
        'msg': u'Hi customer 1',
    },
    {
        'customer_id':2,
        'msg': u'Hi customer 2',
    }
]


@app.route('/api/v1.0/greeting', methods=['POST'])
def get_message():
    if not request.json:
        abort(400)
        # message = {}
    request_code = request.headers['Request-Code']
    print(customer_string+request.json['msg'])
    if int(request_code) == 1:
        global clientInfo
        clientInfo = {'id': ++cust_id, 'host': request.json['host'], 'port': request.json['port']}
        customerQueue.put(clientInfo)
        message = {
            # 'customer_id': messages[-1]['customer_id'] + 1,
            'msg': 'Wait',
            'Response-Code': 1
        }
    # messages.append(message)
    # print "Following message has been created: %s " % message
    elif int(request_code) == 2:
        message = {
            'msg': 'So your total is $9',
            'Response-Code': 2
        }

    return jsonify({'message': message}), 201


def polar():
    while True:
        global currently_serving
        if int(currently_serving) == 0:
            if customerQueue.qsize() != 0:
                currently_serving = 1
                client_info = customerQueue.get()
                host = client_info['host']
                port = client_info['port']
                try:
                    ask_order(host, port, client_info)
                except:
                    print 'Have a good day!'


def ask_order(host, port, client_info):
    cashier_msg = json.dumps({'msg': 'Hi! How can I help you today?'})
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Request-Code': 2}
    customer_url = 'http://'+host+':'+port+'/api/v1.0/ask_order'
    response = requests.post(customer_url, cashier_msg, headers=headers)
    r = response.json()
    if int(r['message']['Response-Code']) == 2:
        print (customer_string+r['message']['msg'])
        client_info['msg'] = r['message']['msg']
        time.sleep(2)
        order_total(host, port, client_info)


def order_total(host, port, client_info):
    cashier_msg = json.dumps({'msg': 'So your total is $15'})
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Request-Code': 3}
    customer_url = 'http://'+host+':'+port+'/api/v1.0/order_total'
    response = requests.post(customer_url, cashier_msg, headers=headers)
    r = response.json()
    if int(r['message']['Response-Code']) == 3:
        print (customer_string+r['message']['msg'])
        global currently_serving
        currently_serving = 0
        set_order('localhost', '5002', client_info)


def set_order(host, port, client_info):
    cashier_msg = json.dumps({'msg': client_info['msg'], 'client_host': client_info['host'],
                              'client_port': client_info['port']})
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Request-Code': 4}
    cook_url = 'http://'+host+':'+port+'/api/v1.0/set_order'
    response = requests.post(cook_url, cashier_msg, headers=headers)
    r = response.json()
    if int(r['message']['Response-Code']) == 4:
        print ('Cook: '+r['message']['msg'])


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

try:
    thread.start_new_thread(polar, ())

except:
    print "Error: unable to start thread"

if __name__ == '__main__':
    app.run('0.0.0.0', port=int(appPort), debug=True, use_reloader=False)

