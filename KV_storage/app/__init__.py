from flask import Flask, request
import logging
import tarantool


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, filename='commands.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


def connect():
	connection = tarantool.connect('localhost', 3301)
	return connection.space('KV_storage')


@app.route('/<string:key>', methods=['GET'])
def get_value(key):
	storage = connect()
	logging.info(f'GET - key = {key}')
	try:
		res = storage.select(key)[0][1]
	except IndexError:
		return tuple(['Not Found\n', 404, []])
	return tuple([str(res), 200, []])


@app.route('/', methods=['POST'])
def post_key_value():
	storage = connect()
	try:
		value = request.json['value']
		key = request.json['key']
		logging.info(f'POST - key = {key}')
		storage.insert([key, value])
		return tuple(['Done\n', 200, []])
	except tarantool.error.DatabaseError:
		return tuple(['Key already exists\n', 409, []])
	except Exception:
		return tuple(['Request error\n', 400, []])
	

@app.route('/<string:key>', methods=['DELETE'])
def delete_key(key):
	storage = connect()
	logging.info(f'DELETE - key = {key}')
	if storage.delete(key):
		return tuple(['Deleted\n', 200, []])
	else:
		return tuple(['Not Found\n', 404, []])

	
@app.route('/<string:key>', methods=['PUT'])
def update_key_value(key):
	storage = connect()
	logging.info(f'PUT - key = {key}')
	try:
		value = request.json['value']
		storage.update(key, [('=', 1, value)])
		return tuple(['Updated\n', 200, []])
	except IndexError:
		return tuple(['Not Found\n', 404, []])
	except Exception:
		return tuple(['Request error\n', 400, []])


if __name__ == '__main__':
    app.run(debug=True)
