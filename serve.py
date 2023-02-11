from flask import Flask, jsonify, request
import pickle
import json


grad = pickle.load(open('local.sav', 'rb'))
head = ['N', 'P', 'K', 'temp', 'humid', 'ph', 'rain']
targets = json.loads(open('map.dict').read())
print(targets)

app = Flask(__name__)


@app.route('/', methods = ['GET', 'POST'])
def home():
	if(request.method == 'GET'):
		data = "hello world"
		return jsonify({'data': data})


# query the neural network
@app.route('/query/', methods = ['POST'])
def disp():
	n = request.form['N']
	p = request.form['P']
	k = request.form['K']
	temp = request.form['temp']
	humid = request.form['humid']
	ph = request.form['ph']
	rain = request.form['rain']

	X = [n, p, k, temp, humid, ph, rain]

	res = targets[str(grad.predict([X])[0])]
	
	return jsonify({'predicted': res})

# @app.route('/query2/', methods = ['POST'])
# def disp():
# 	n = request.form['location']
# 	p = request.form['month']


	# X = [n, p, k, temp, humid, ph, rain]

	# res = targets[str(grad.predict([X])[0])]
	
	# return jsonify({'predicted': res})


# driver function
if __name__ == '__main__':

	app.run(debug = True)
