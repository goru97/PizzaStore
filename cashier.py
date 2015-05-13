#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request
import requests
import json
import sys
import thread
import Queue
import time
import logging
import thread
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

customerQueue = Queue.Queue()
currently_serving = 0
appPort = sys.argv[1]
app = Flask(__name__)
customer_string = 'Customer: '
clientInfo = {}
cust_id = 0

with open('menu.json') as data_file:
    menu = json.load(data_file)


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
        msg = " "
        if customerQueue.qsize() == 1:
            msg = "Hi!"
        else:
            msg = "Hi! I'll be right with you."
        message = {
            # 'customer_id': messages[-1]['customer_id'] + 1,
            'msg': msg,
            'Response-Code': 1
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
                ask_order(host, port, client_info)
                '''try:
                    ask_order(host, port, client_info)
                except:
                    print 'Have a good day!'''


def ask_order(host, port, client_info):
    cashier_msg = json.dumps({'msg': 'How can I help you today?'})
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Request-Code': 2}
    customer_url = 'http://'+host+':'+port+'/api/v1.0/ask_order'
    response = requests.post(customer_url, cashier_msg, headers=headers)
    r = response.json()
    if int(r['message']['Response-Code']) == 2:
        print (customer_string+r['message']['msg'])
        client_info['msg'] = r['message']['msg']
        client_info['food_choice'] = r['message']['food_choice']
        time.sleep(2)
        order_total(host, port, client_info)


def order_total(host, port, client_info):
    food_choice = client_info['food_choice']
    total = 0
    for food in food_choice:
        for choice in menu:
            if food['id'] == choice['id']:
                total += float(choice['price'][1:])

    cashier_msg = json.dumps({'msg': 'So your total is $'+str(total)})
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
    client_info.pop("msg", None)
    cashier_msg = json.dumps(client_info)
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

