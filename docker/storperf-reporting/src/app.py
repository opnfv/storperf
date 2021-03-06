##############################################################################
# Copyright (c) 2017 Dell EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import json
import urllib

from flask import Flask, redirect, url_for, request, render_template, session
from flask import send_from_directory, flash

import validators


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /storperf/ {
        proxy_pass http://localhost:8085/;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /storperf;
    }

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')

        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme

        return self.app(environ, start_response)


app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.secret_key = 'storperf_graphing_module'


def get_data(data):
    metrics = {}
    report_data = {}
    temp = data.get("results") or data.get("report") or data.get("details")
    if type(temp) is list:
        length = len(temp)
        if length == 1:
            details = temp[0].get('details')
            metrics = details.get('metrics')
            report_data = details.get('report_data')
            return "single", metrics, report_data, temp
        else:
            return "multi", temp
    else:
        metrics = temp.get('metrics')
        report_data = temp.get('report_data')
        return "single", metrics, report_data, temp


@app.route('/reporting/success/')
def success():
    try:
        URL = session["url"]
        if URL.find("jobs") is not -1 and URL.find("metadata") is -1:
            data = urllib.urlopen(URL).read()
            data = json.loads(data)
            temp = data["job_ids"]
            if temp:
                info = {}
                for ID in temp:
                    url = URL + "?id=" + ID + "&type=metadata"
                    data_temp = urllib.urlopen(url).read()
                    data_temp = json.loads(data_temp)
                    report_data = get_data(data_temp)[-1]
                    info[ID] = report_data
                return render_template('plot_jobs.html', results=info)
        if validators.url(URL):
            data = urllib.urlopen(URL).read()
        else:
            data = open("./static/testdata/" + URL).read()
        data = json.loads(data)
        response = get_data(data)
        if response[0] == "single":
            metrics, report_data = response[1], response[2]
            results = response[3]
            return render_template('plot_tables.html',
                                   metrics=metrics, report_data=report_data,
                                   results=results)
        else:
            return render_template('plot_multi_data.html',
                                   results=response[1])
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


@app.route('/reporting/3rd_party/js/<path:path>')
def js(path):
    return send_from_directory('static/3rd_party/js/', path)


@app.route('/reporting/3rd_party/css/<path:path>')
def css(path):
    return send_from_directory('static/3rd_party/css/', path)


@app.route('/reporting/images/<path:path>')
def images(path):
    return send_from_directory('static/images/', path)


@app.route('/reporting/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=True)
