from flask import Flask, jsonify, request
import requests
import pickle
import json
import pandas as pd

URL = 'http://api.weatherapi.com/v1/future.json'
APIKEY = '49937b2e2ca847928e150828231102'
# &q=Islampur&dt=2023-03-13


grad = pickle.load(open('local.sav', 'rb'))
head = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
targets = json.loads(open('map.dict').read())


df = pd.read_csv('rainfall.csv')
dist = dict(list(df.groupby('STATE_UT_NAME')['DISTRICT']))
rainfall = df[['DISTRICT', 'ANNUAL']].set_index('DISTRICT').to_dict()['ANNUAL']


app = Flask(__name__)


@app.route('/', methods = ['GET', 'POST'])
def home():
	if(request.method == 'GET'):
		data = "hello world"
		return jsonify({'data': data})


# query the neural network
@app.route('/queryALL/', methods = ['POST'])
def queryALL():
	n = request.form['N']
	p = request.form['P']
	k = request.form['K']
	temp = request.form['temp']
	humid = request.form['humid']
	ph = request.form['ph']
	rain = request.form['rain'] # average annual rainfall

	X = [[n, p, k, temp, humid, ph, rain]]
	x = pd.DataFrame(X, columns=head)

	prob = grad.predict_proba(x)[0]
	p = [[targets[str(i)], prob[i]] for i in range(len(prob))]
	p = sorted(p, key=lambda x: x[1], reverse=True)

	return jsonify({'predicted': p[0], 'next 4': p[1:5]})

@app.route('/queryLD/', methods = ['POST'])
def queryLD():
	district = request.form['district']
	state = request.form['state']
	month = request.form['month']
	year = request.form['year']
	n = request.form['N']
	p = request.form['P']
	k = request.form['K']
	ph = request.form['ph']

	month = str(month)
	if(len(month) == 1):
		month = '0' + month
	rain = rainfall[district.upper()] * 0.0393701
	
	w = getWeather(location = district, year = year, month = month)
	temp = w['avgtemp']
	humid = w['avghum']
	X = [n, p, k, temp, humid, ph, rain]
	print(X)

	res = targets[str(grad.predict([X])[0])]
	return jsonify({'predicted': res})


def getWeather(location, year, month):
	ym = str(year) + '-' + str(month) + '-'
	params = {
		'key': APIKEY,
		'q'  : location,
		'dt' : ym + '01'
	}
	res = []
	r = requests.get(url = URL, params = params)
	if(r.status_code != 200):
		print(r.json())
		raise Exception("Somethings wrong cant get from weather API")
	res.append(r.json())
	params['dt'] = ym + '15'
	res.append(requests.get(url = URL, params = params).json())
	params['dt'] = ym + '28'
	res.append(requests.get(url = URL, params = params).json())

	t = [r['forecast']['forecastday'][0]['day']['avgtemp_c'] for r in res]
	h = [r['forecast']['forecastday'][0]['day']['avghumidity'] for r in res]
	result = {
		'avgtemp' : sum(t) / 3,
		'avghum' : sum(h) / 3
	}
	return result

if __name__ == '__main__':

	app.run(debug = True)
