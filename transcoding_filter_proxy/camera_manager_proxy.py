#!/usr/bin/python3
# -*- coding: utf-8 -*-

import zmq
import json
import time

import logging

class CameraManagerProxy(object):
    def __init__(self, addr):
        super().__init__()
        self._port = None
        self.req_stream = None
        self.context = None
        self.SERVER_ENDPOINT = addr

    @property
    def port(self):
        return self._port

    def zmq_socket_creator(f, *args):
        def new_f(*args):
            self = args[0]
            logging.debug("Entering %s" % (f.__name__))
            self.client = self.context.socket(zmq.REQ)
            self.client.connect(self.SERVER_ENDPOINT)
            result = f(*args)
            msg = self.client.recv_unicode()
            self.client.close()
            return msg
        return new_f

    def setup(self):
        """Sets up PyZMQ and creates all streams."""
        self.context = zmq.Context()
        print("I: Connecting to server ...")

    @zmq_socket_creator
    def msgDispatch(self, msgStr):
        self.client.send_unicode(msgStr)

    def start_cam(self, cam_id):
        payload = {
            "method": "start",
            "params": [cam_id],
            "id": 2,
            "jsonrpc": "2.0"
        }
        request = json.dumps(payload)
        self.msgDispatch(request)

    def stop_cam(self, cam_id):
        print('stopping cam json')
        payload = {
            "method": "stop",
            "params": [cam_id],
            "id": 2,
            "jsonrpc": "2.0"
        }
        request = json.dumps(payload)
        self.msgDispatch(request)

    def take_picture(self, cam_id):
        payload = {
            "method": "take_picture",
            "params": [cam_id],
            "id": 2,
            "jsonrpc": "2.0"
        }
        request = json.dumps(payload)
        self.msgDispatch(request)

    def list(self):
        payload = {
            "method": "list",
            "id": 2,
            "jsonrpc": "2.0"
        }
        request = json.dumps(payload)
        #self.client.send_unicode(request)
        msg = self.msgDispatch(request)
        print(msg)
        return msg
