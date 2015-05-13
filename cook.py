from flask import Flask, jsonify, abort, make_response, request
import thread
import Queue
import sys
import logging
import time
import json
import requests
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
cashier_string = 'Cashier: '
ordersQueue = Queue.Queue()
appPort = sys.argv[1]


def polar():
    while True:
        if ordersQueue.qsize() > 0:
            client_info = ordersQueue.get()
            time.sleep(10)
            order_ready(client_info['host'], client_info['port'])


def order_ready(host, port):
    customer_msg = json.dumps({"msg": "Your order is ready. Enjoy your meal"})
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Request-Code': 5}
    customer_url = 'http://'+host+':'+port+'/api/v1.0/order_ready'
    response = requests.post(customer_url, customer_msg, headers=headers)
    r = response.json()
    if int(r['message']['Response-Code']) == 5:
        print ('Customer: '+r['message']['msg'])


@app.route('/api/v1.0/set_order', methods=['POST'])
def set_order():
    if not request.json:
        abort(400)
        # message = {}
    request_code = request.headers['Request-Code']
    # print(request.json)
    clientInfo = {'host': request.json['host'], 'port': request.json['port']}
    ordersQueue.put(clientInfo)
    if int(request_code) == 4:
        message = {
            # 'customer_id': messages[-1]['customer_id'] + 1,
            'msg': 'Preparing...',
            'Response-Code': 4
        }
    time.sleep(2)
    return jsonify({'message': message}), 201

try:
    thread.start_new_thread(polar, ())

except:
    print "Error: unable to start thread"

if __name__ == '__main__':
    app.run('0.0.0.0', port=int(appPort), debug=True, use_reloader=False)