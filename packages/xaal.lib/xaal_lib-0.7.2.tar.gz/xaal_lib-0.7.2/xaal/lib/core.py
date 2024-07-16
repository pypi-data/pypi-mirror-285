#
#  Copyright 2014, Jérôme Colin, Jérôme Kerdreux, Philippe Tanguy,
#  Telecom Bretagne.
#
#  This file is part of xAAL.
#
#  xAAL is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  xAAL is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with xAAL. If not, see <http://www.gnu.org/licenses/>.
#

from .messages import MessageType, MessageAction, MessageFactory, ALIVE_ADDR
from .exceptions  import *

import time
import inspect

import logging
logger = logging.getLogger(__name__)

class EngineMixin(object):

    __slots__ = ['devices','timers','subscribers','msg_filter','_attributesChange','network','msg_factory']

    def __init__(self,address,port,hops,key):
        self.devices = []                        # list of devices / use (un)register_devices()
        self.timers = []                         # functions to call periodic
        self.subscribers = []                    # message receive workflow
        self.msg_filter = None                  # message filter

        self._attributesChange = []              # list of XAALAttributes instances

        # network connector
        self.network = None
        # start msg worker
        self.msg_factory = MessageFactory(key)
        # filter function activated
        self.enable_msg_filter()

    #####################################################
    # Devices management
    #####################################################
    def add_device(self, dev):
        """register a new device """
        if dev not in self.devices:
            self.devices.append(dev)
            dev.engine = self
        if self.is_running():
            self.send_alive(dev)

    def add_devices(self, devs):
        """register new devices"""
        for dev in devs:
            self.add_device(dev)

    def remove_device(self, dev):
        """unregister a device """
        dev.engine = None
        # Remove dev from devices list
        self.devices.remove(dev)

    #####################################################
    # xAAL messages Tx handling
    #####################################################
    # Fifo for msg to send
    def queue_msg(self, msg):
        logger.critical("To be implemented queue_msg: %s", msg)

    def send_request(self,dev,targets,action,body = None):
        """queue a new request"""
        msg = self.msg_factory.build_msg(dev, targets, MessageType.REQUEST, action, body)
        self.queue_msg(msg)

    def send_reply(self, dev, targets, action, body=None):
        """queue a new reply"""
        msg = self.msg_factory.build_msg(dev, targets, MessageType.REPLY, action, body)
        self.queue_msg(msg)

    def send_error(self, dev, errcode, description=None):
        """queue a error message"""
        msg = self.msg_factory.build_error_msg(dev, errcode, description)
        self.queue_msg(msg)

    def send_get_description(self, dev, targets):
        """queue a get_description request"""
        self.send_request(dev, targets, MessageAction.GET_DESCRIPTION.value)

    def send_get_attributes(self, dev, targets):
        """queue a get_attributes request"""
        self.send_request(dev, targets, MessageAction.GET_ATTRIBUTES.value)

    def send_notification(self, dev, action, body=None):
        """queue a notificaton"""
        msg = self.msg_factory.build_msg(dev, [], MessageType.NOTIFY, action,body)
        self.queue_msg(msg)

    def send_alive(self, dev):
        """Send a Alive message for a given device"""
        timeout = dev.get_timeout()
        msg = self.msg_factory.build_alive_for(dev, timeout)
        self.queue_msg(msg)
        dev.update_alive()

    def send_is_alive(self, dev, targets=[ALIVE_ADDR,], dev_types=["any.any",]):
        """Send a is_alive message, w/ dev_types filtering"""
        body = {'dev_types': dev_types}
        self.send_request(dev,targets, MessageAction.IS_ALIVE.value, body)


    #####################################################
    # Messages filtering
    #####################################################
    def enable_msg_filter(self, func=None):
        """enable message filter"""
        self.msg_filter = func or self.default_msg_filter

    def disable_msg_filter(self):
        """disable message filter"""
        self.msg_filter = None

    def default_msg_filter(self, msg):
        """
        Filter messages:
        - check if message has alive request address
        - check if the message is for us
        return False, if message should be dropped
        """
        # Alive request
        if ALIVE_ADDR in msg.targets:
            return True
        # Managed device ?
        for dev in self.devices:
            if dev.address in msg.targets:
                return True
        return False

    #####################################################
    # Alive messages
    #####################################################
    def process_alives(self):
        """Periodic sending alive messages"""
        now = time.time()
        for dev in self.devices:
            if dev.next_alive < now :
                self.send_alive(dev)

    #####################################################
    # xAAL attributes changes
    #####################################################
    def add_attributes_change(self, attr):
        """add a new attribute change to the list"""
        self._attributesChange.append(attr)

    def get_attributes_change(self):
        """return the pending attributes changes list"""
        return self._attributesChange

    def process_attributes_change(self):
        """Processes (send notify) attributes changes for all devices"""
        devices = {}
        # Group attributes changed by device
        for attr in self.get_attributes_change():
            if attr.device not in devices.keys():
                devices[attr.device] = {}
            devices[attr.device][attr.name] = attr.value

        for dev in devices:
            self.send_notification(dev, MessageAction.ATTRIBUTES_CHANGE.value, devices[dev])
        self._attributesChange = []  # empty array

    #####################################################
    # xAAL messages subscribers
    #####################################################
    def subscribe(self,func):
        self.subscribers.append(func)

    def unsubscribe(self,func):
        self.subscribers.remove(func)

    #####################################################
    # timers
    #####################################################
    def add_timer(self, func, period,counter=-1):
        """ 
        func: function to call
        period: period in second
        counter: number of repeat, -1 => always
        """
        if counter == 0:
            raise EngineError("Timer counter should =-1 or >0")
        t = Timer(func, period, counter)
        self.timers.append(t)
        return t

    def remove_timer(self, timer):
        """remove a given timer from the list"""
        self.timers.remove(timer)

    #####################################################
    # start/stop/run API
    #####################################################
    def start(self):
        logger.critical("To be implemented start")

    def stop(self):
        logger.critical("To be implemented stop")

    def shutdown(self):
        logger.critical("To be implemented shutdown")

    def run(self):
        logger.critical("To be implemented run")

    def is_running(self):
        logger.critical("To be implemented is_running")

#####################################################
# Timer class
#####################################################
class Timer(object):
    def __init__(self, func, period, counter):
        self.func = func
        self.period = period
        self.counter = counter
        self.deadline = time.time() + period

#####################################################
# Usefull functions to Engine developpers
#####################################################
def filter_msg_for_devices(msg, devices):
    """
    loop throught the devices, to find which are expected w/ the msg
    - Filter on dev_types for is_alive broadcast request.
    - Filter on device address
    """
    results = []
    if msg.is_request_isalive() and (ALIVE_ADDR in msg.targets):
        # if we receive a broadcast is_alive request, we reply
        # with filtering on dev_tyes. 
        if 'dev_types' in msg.body.keys():
            dev_types = msg.body['dev_types']
            if 'any.any' in dev_types:
                results = devices
            else:
                for dev in devices:
                    any_subtype = dev.dev_type.split('.')[0] + '.any'
                    if dev.dev_type in dev_types:
                        results.append(dev)
                    elif any_subtype in dev_types:
                        results.append(dev)
    else:
        # this is a normal request, only filter on device address
        # note: direct is_alive are treated like normal request 
        # so dev_types filtering is discarded
        for dev in devices:
            if dev.address in msg.targets:
                results.append(dev)
    return results

def search_action(msg, device):
    """
    Extract an action (match with methods) from a msg on the device.
    Return:
        - None
        - found method & matching parameters

    Note: If method not found raise error, if wrong parameter error log
    """
    methods = device.get_methods()
    params = {}
    result = None
    if msg.action in methods.keys():
        method = methods[msg.action]
        body_params = None
        if msg.body:
            method_params = get_args_method(method)
            body_params = msg.body

            for k in body_params:
                temp = '_%s' %k
                if temp in method_params:
                    params.update({temp:body_params[k]})
                else:
                    logger.warning("Wrong method parameter [%s] for action %s" %(k, msg.action))
        result =  (method,params)
    else:
        raise XAALError("Method %s not found on device %s" % (msg.action,device))
    return result

def get_args_method(method):
    """ return the list on arguments for a given python method """
    spec = inspect.getfullargspec(method)
    try:
        spec.args.remove('self')
    except Exception:
        pass
    return spec.args


