#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import sys
from datetime import timedelta
from flask import Flask, make_response, request, current_app
from functools import update_wrapper
import yaml

from camera_manager_proxy import CameraManagerProxy

CONFIG_FILE = '/config.yaml'

# load config
with open(CONFIG_FILE, 'r') as f:
    try:
        print('Loading config %s' % (CONFIG_FILE))
        cfg_obj = yaml.load(f, Loader=yaml.Loader)
    except yaml.scanner.ScannerError:
        print('Bad yaml syntax')
        raise
print(cfg_obj)

# setup logging
logging.basicConfig(
    stream = sys.stdout,
    level = cfg_obj['log_level'],
    filemode = "a",
    format = "%(asctime)s %(funcName)s Line:%(lineno)s [%(levelname)-8s] %(message)s",
    datefmt = "%H:%M:%S")

cam_manager = CameraManagerProxy(cfg_obj['backend'])
cam_manager.setup()
# create flask app
app = Flask(__name__)

# implementation of CORS
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, (str,bytes)):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, (str,bytes)):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

@app.route("/get_cam_ids")
@crossdomain(origin='*')
def list_cam_ids():
    print('list_cam_ids')
    print(cam_manager.list())
    return str(cam_manager.list())

@app.route("/take_picture/<int:cam_id>")
@crossdomain(origin='*')
def take_picture(cam_id):
    cam_manager.take_picture(cam_id)
    return ("Cam %d take picture" % (cam_id))

@app.route("/heartbeat/<int:cam_id>")
@crossdomain(origin='*')
def keep_cam_streaming(cam_id):
    cam_manager.start_cam(cam_id)
    return ("Cam %d keeps streaming" % (cam_id))

@app.route("/")
def hello():
    return "Hello Flask!"

if __name__ == "__main__":
    
    app.run(host='0.0.0.0', port=80)
