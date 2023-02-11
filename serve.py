from flask import Flask, render_template, url_for, jsonify, request
import requests
import pickle
import json
import pandas as pd
import os

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

# @app.route('/queryALL/')
# def queryALLform():
# 	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
# 	json_url = os.path.join(SITE_ROOT, "static/data", "range_min.json")
# 	range_min = json.load(open(json_url))
# 	json_url = os.path.join(SITE_ROOT, "static/data", "range_max.json")
# 	range_max = json.load(open(json_url))
# 	return render_template('queryALL.html',range_min=range_min, range_max=range_max)

# query the neural network
@app.route('/queryALL/', methods = ['GET','POST'])
def queryALL():
	if(request.method=='POST'):
		n = request.form['n']
		p = request.form['p']
		k = request.form['k']
		temp = request.form['temperature']
		humid = request.form['humidity']
		ph = request.form['ph']
		rain = request.form['rainfall'] # average annual rainfall

		X = [[n, p, k, temp, humid, ph, rain]]
		x = pd.DataFrame(X, columns=head)

		prob = grad.predict_proba(x)[0]
		p = [[targets[str(i)], prob[i]] for i in range(len(prob))]
		p = sorted(p, key=lambda x: x[1], reverse=True)

		r= {'top': p[0], 'next4': p[1:5]}
		jsonify(r)
		print(r)
		return render_template('recommend.html',r=r)
	else:
		SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
		json_url = os.path.join(SITE_ROOT, "static/data", "range_min.json")
		range_min = json.load(open(json_url))
		json_url = os.path.join(SITE_ROOT, "static/data", "range_max.json")
		range_max = json.load(open(json_url))
		return render_template('queryALL.html',range_min=range_min, range_max=range_max)

@app.route('/queryLD/')
def queryLDform():
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	json_url = os.path.join(SITE_ROOT, "static/data", "location.json")
	loc = json.load(open(json_url))
	json_url = os.path.join(SITE_ROOT, "static/data", "range_min.json")
	range_min = json.load(open(json_url))
	json_url = os.path.join(SITE_ROOT, "static/data", "range_max.json")
	range_max = json.load(open(json_url))
	return render_template('queryLD.html', loc=loc, range_min=range_min, range_max=range_max)

@app.route('/queryLD/', methods = ['POST'])
def queryLD():
	district = request.form['district']
	state = request.form['state']
	month = request.form['month']
	year = request.form['year']
	n = request.form['n']
	p = request.form['p']
	k = request.form['k']
	ph = request.form['ph']

	month = str(month)
	if(len(month) == 1):
		month = '0' + month
	rain = rainfall[district.upper()] * 0.0393701
	
	w = getWeather(location = district, year = year, month = month)
	temp = w['avgtemp']
	humid = w['avghum']

	X = [[n, p, k, temp, humid, ph, rain]]
	x = pd.DataFrame(X, columns=head)

	prob = grad.predict_proba(x)[0]
	p = [[targets[str(i)], prob[i]] for i in range(len(prob))]
	p = sorted(p, key=lambda x: x[1], reverse=True)

	return jsonify({'predicted': p[0], 'next4': p[1:5]})


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
