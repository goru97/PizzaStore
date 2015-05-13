from flask import Flask, jsonify, abort, make_response, request
import thread
import Queue
import sys
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
cashier_string = 'Cashier: '
ordersQueue = Queue.Queue()
appPort = sys.argv[1]


@app.route('/api/v1.0/set_order', methods=['POST'])
def set_order():
    if not request.json:
        abort(400)
        # message = {}
    request_code = request.headers['Request-Code']
    print(request.json)
    if int(request_code) == 4:
        message = {
            # 'customer_id': messages[-1]['customer_id'] + 1,
            'msg': 'Preparing...',
            'Response-Code': 4
        }

    return jsonify({'message': message}), 201

if __name__ == '__main__':
    app.run('0.0.0.0', port=int(appPort), debug=True, use_reloader=False)