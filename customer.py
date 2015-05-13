import requests
import json
from flask import Flask, jsonify, abort, make_response, request
import socket
import sys

'''socket.gethostbyname(socket.gethostname())'''
'''
order_url = 'http://127.0.0.1:5000/todo/api/v1.0/orders'
order_detail = json.dumps({"item": "tudy"})
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.post(order_url, order_detail, headers=headers)
data = response.text
print(data)
'''
'''
response = requests.get('http://127.0.0.1:5000/todo/api/v1.0/orders')
data = response.json()
print(data)
'''

cashier_url = 'http://localhost:5001/api/v1.0/greeting'
cashier_string = 'Cashier: '
app = Flask(__name__)
appPort = sys.argv[1]


def say_hi():
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
        message = {
            # 'customer_id': messages[-1]['customer_id'] + 1,
            'msg': 'Can I get one Pizza',
            'Response-Code': 2
        }

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
            'msg': 'Here you go!',
            'Response-Code': 3
        }

    return jsonify({'message': message}), 201


say_hi()
if __name__ == '__main__':
    app.run('0.0.0.0', port=int(appPort), debug=True, use_reloader=False)


'''
if r is "Hi! How can I help you today?":
    order_url = 'http://10.189.184.232:5000/api/v1.0/order'
    customer_order = json.dumps({"message": "Can I get these items?", "items": ["Coffee", "Chai"]})
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
'''


