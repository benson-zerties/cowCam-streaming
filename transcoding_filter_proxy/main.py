#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import logging
import sys
import zmq
import json
import time

from jsonrpc import JSONRPCResponseManager, Dispatcher
from jsonrpc.exceptions import JSONRPCMethodNotFound
from zmq_process import ZmqThread
from restartable_timer import RestartableTimer
from camera_manager_proxy import CameraManagerProxy

class CamHandlerProxy(ZmqThread):
    def __init__(self, bind_addr, on_recv_cb):
        super().__init__()
        self.bind_addr = bind_addr
        self._port = None
        self.recv_cb = on_recv_cb
        self.rep_stream = None

    @property
    def port(self):
        return self._port

    def setup(self):
        """Sets up PyZMQ and creates all streams."""
        super().setup()

        # Create the stream and add the message handler
        self.rep_stream, self._port = self.stream(zmq.REP, self.bind_addr, bind=True)
        self.rep_stream.on_recv(lambda msg: self.rep_stream.send_string(self.recv_cb(msg)))

    def run(self):
        """Sets up everything and starts the event loop."""
        self.setup()
        self.loop.start()

    def stop(self):
        """Stops the event loop."""
        self.loop.stop()


def getStartMethod(cam_manager, timeout):
    print('setting up start-method')
    def start(*cam_id):
        cam_id1 = cam_id[0]
        if cam_id1 not in start.timers or \
                not start.timers[cam_id1].is_alive():
            # we received a new cam_id -> validate if it exists
            try:
                json_result_dict = json.loads(cam_manager.list())
                cam_list = json_result_dict['result']
            except e:
                print(e)
            if cam_id1 in cam_list:
                # cam id valid -> start streaming
                cam_manager.start_cam(cam_id1)
                # if timeout == 0, never stop streaming
                if timeout != 0:
                    start.timers[cam_id1] = \
                        RestartableTimer(timeout,
                                     lambda: (cam_manager.stop_cam(cam_id1)))
                    start.timers[cam_id1].start()
                return "cam_started"
        else:
            start.timers[cam_id1].restart()

    start.timers = dict()
    return start

def handle_json(cam_manager, response_mgr, msg_dispatcher, message):
    """Callback function, called if new message is received."""
    msgStr = message[0].decode('utf-8')
    response = response_mgr.handle(msgStr, msg_dispatcher)
    if response.error and (response.error['code'] == JSONRPCMethodNotFound.CODE):
        # method not implemented -> dispatch to backend
        logging.debug('Dispatching: %s' % (msgStr))
        result = cam_manager.msgDispatch(msgStr)
    else:
        result = response.json

    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--timeout', type=int, default=0, 
            help="Specify when to stop camera backend after stearming start in seconds")
    parser.add_argument('-C', '--cam_mgr', type=str, help="Specify the camera backend uri")
    parser.add_argument('-p', '--port', type=int, help="Specify the port to listen to", )
    args = parser.parse_args()
    
    assert args.timeout >= 0

    logging.basicConfig(
        #filename = "cam_handler_remote.log",
        stream = sys.stdout,
        level = logging.DEBUG,
        filemode = "a",
        format = "%(asctime)s %(funcName)s Line:%(lineno)s [%(levelname)-8s] %(message)s",
        datefmt = "%H:%M:%S")

    uri = 'tcp://*:' + str(args.port)

    cam_manager = CameraManagerProxy(args.cam_mgr)
    cam_manager.setup()
    response_mgr = JSONRPCResponseManager()
    my_dispatcher = Dispatcher()
    my_dispatcher.add_method(getStartMethod(cam_manager, args.timeout), name='start')
    a = CamHandlerProxy(uri, lambda msg : handle_json(cam_manager, response_mgr, my_dispatcher, msg))
    a.start()
    a.join()
