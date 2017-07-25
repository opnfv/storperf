##############################################################################
# Copyright (c) 2017 Dell EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from flask import Flask, redirect, url_for, request, render_template, session
from flask import send_from_directory
import urllib
import json
app = Flask(__name__)
app.secret_key = 'storperf_graphing_module'


@app.route('/reporting/success/')
def success():
    data = urllib.urlopen(session["url"]).read()
    data = json.loads(data)
    return render_template('plot_tables.html', data=data)


@app.route('/reporting/url', methods=['POST', 'GET'])
def url():
    if request.method == 'POST':
        url = request.form['url']
        session["url"] = url
        return redirect(url_for('success'))


@app.route('/reporting/js/<path:path>')
def js(path):
    return send_from_directory('static/js/', path)


@app.route('/reporting/css/<path:path>')
def css(path):
    return send_from_directory('static/css/', path)


@app.route('/reporting/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=True)
