from flask import Flask, redirect, url_for, request, render_template,jsonify, session
import requests, json
import urllib, json
app = Flask(__name__)
app.secret_key = 'storperf_graphing_module'
#global url

@app.route('/reporting/success/')
def success():
    header = {'x-requested-with': 'XMLHttpRequest'}
    data = urllib.urlopen(session["url"]).read()
    data = json.loads(data)
    return render_template('plot_tables.html', data = data)

@app.route('/reporting/url',methods = ['POST', 'GET'])
def url():
    if request.method == 'POST':
#      global url 
      url = request.form['url']
      session["url"] = url
      return redirect(url_for('success'))

@app.route('/reporting/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug = True, threaded=True)