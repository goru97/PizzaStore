import requests
import json
from flask import Flask, jsonify, abort, make_response, request
import socket
import sys
import logging
import time
import thread
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


cashier_url = 'http://localhost:5001/api/v1.0/greeting'
cashier_string = 'Cashier: '
cook_string = 'Cook: '
app = Flask(__name__)
config_file = sys.argv[1]
with open(config_file) as data_file:
            customer_config = json.load(data_file)
food_choice = customer_config['food_choice']
appPort = customer_config['port']
# appPort = sys.argv[1]


def say_hi(delay):
    time.sleep(delay)
    customer_msg = json.dumps({'msg': 'Hi!', 'host': socket.gethostbyname(socket.gethostname()), 'port': appPort})
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Request-Code': 1}
    response = requests.post(cashier_url, customer_msg, headers=headers)
    r = response.json()
    if int(r['message']['Response-Code']) == 1:
        print(cashier_string+r['message']['msg'])
        # send_order()


@app.route('/api/v1.0/ask_order', methods=['POST'])
def ask_order():
    if not request.json:
        abort(400)
        # message = {}
    request_code = request.headers['Request-Code']
    print(cashier_string+request.json['msg'])
    if int(request_code) == 2:
        msg = ''
        for food in food_choice:
            msg = msg+" "+food['name']
        message = {
            'msg': 'Can I get '+msg,
            'Response-Code': 2,
            'food_choice': food_choice
        }
    time.sleep(2)
    return jsonify({'message': message}), 201


@app.route('/api/v1.0/order_total', methods=['POST'])
def order_total():
    if not request.json:
        abort(400)
        # message = {}
    request_code = request.headers['Request-Code']
    print(cashier_string+request.json['msg'])
    if int(request_code) == 3:
        message = {
            # 'customer_id': messages[-1]['customer_id'] + 1,
            "msg": "The wicked borrows but does not pay back, but the righteous is generous and gives- Psalm 37:21",
            "Response-Code": 3
        }
    time.sleep(2)
    return jsonify({"message": message}), 201

@app.route('/api/v1.0/order_ready', methods=['POST'])
def order_ready():
    if not request.json:
        abort(400)
        # message = {}
    request_code = request.headers['Request-Code']
    print(cook_string+request.json['msg'])
    if int(request_code) == 5:
        message = {
            "msg": "Thank You!",
            "Response-Code": 5
        }
    time.sleep(2)
    return jsonify({"message": message}), 201
try:
    thread.start_new_thread(say_hi, (2,))

except:
    print "Error: unable to start thread"


if __name__ == '__main__':
    app.run('0.0.0.0', port=int(appPort), debug=True, use_reloader=False)



