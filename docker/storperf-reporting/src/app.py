##############################################################################
# Copyright (c) 2017 Dell EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from flask import Flask, redirect, url_for, request, render_template, session
from flask import send_from_directory, flash
import urllib
import validators
import json
app = Flask(__name__)
app.secret_key = 'storperf_graphing_module'


def get_data(data):
    metrics = {}
    report_data = {}
    temp = data.keys()[0]
    if type(data[temp]) is list:
        details = data[temp][0].get('details')
        metrics = details.get('metrics')
        report_data = details.get('report_data')
    else:
        metrics = data[temp].get('metrics')
        report_data = data[temp].get('report_data')
    return metrics, report_data


@app.route('/reporting/success/')
def success():
    try:
        URL = session["url"]
        if validators.url(URL):
            data = urllib.urlopen(URL).read()
        else:
            data = open("./static/testdata/" + URL).read()
        data = json.loads(data)
        metrics, report_data = get_data(data)
        return render_template('plot_tables.html',
                               metrics=metrics, report_data=report_data)
    except Exception as e:
        session['server_error'] = e.message + ' ' + repr(e.args)
        return redirect(url_for('file_not_found'))


@app.route('/reporting/url', methods=['POST', 'GET'])
def url():
    if request.method == 'POST':
        url = request.form['url']
        session["url"] = url
        return redirect(url_for('success'))


@app.route('/reporting/file_not_found/')
def file_not_found():
    error = session.get('server_error')
    flash("Server Error: " + error)
    return redirect(url_for('index'))


@app.route('/reporting/js/<path:path>')
def js(path):
    return send_from_directory('static/js/', path)


@app.route('/reporting/css/<path:path>')
def css(path):
    return send_from_directory('static/css/', path)


@app.route('/reporting/images/<path:path>')
def images(path):
    return send_from_directory('static/images/', path)


@app.route('/reporting/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=True)
