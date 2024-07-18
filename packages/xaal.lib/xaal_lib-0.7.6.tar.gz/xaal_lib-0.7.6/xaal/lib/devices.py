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


from . import config
from . import tools
from . import bindings
from .exceptions import DeviceError

from tabulate import tabulate
import logging
logger = logging.getLogger(__name__)

import time

class Attribute(object):

    def __init__(self, name, dev=None, default=None):
        self.name = name
        self.default = default
        self.device = dev
        self.__value = default

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if value != self.__value:
            eng = self.device.engine
            if eng:
                eng.add_attributes_change(self)
                logger.debug("Attr change %s %s=%s" % (self.device.address,self.name,value))
        self.__value = value

    def __repr__(self): # pragma: no cover
        return f"<{self.__module__}.Attribute {self.name} at 0x{id(self):x}>"
    

class Attributes(list):
    """Devices owns a attributes list. This list also have dict-like access"""

    def __getitem__(self,value):
        if isinstance(value,int):
            return list.__getitem__(self,value)
        for k in self:
            if (value == k.name):
                return k.value
        raise KeyError(value)
    
    def __setitem__(self,name,value):
        if isinstance(name,int):
            return list.__setitem__(self,name,value)
        for k in self:
            if (name == k.name):
                k.value = value
                return
        raise KeyError(name)
    
class Device(object):

    __slots__ = ['__dev_type','__address','group_id',
                'vendor_id','product_id','hw_id',
                '__version','__url','schema','info',
                'unsupported_attributes','unsupported_methods','unsupported_notifications',
                'alive_period','next_alive',
                '__attributes','methods','engine']

    def __init__(self,dev_type,addr=None,engine=None):
        # xAAL internal attributes for a device
        self.dev_type = dev_type        # xaal dev_type
        self.address = addr             # xaal addr
        self.group_id = None            # group devices
        self.vendor_id = None           # vendor ID ie : ACME
        self.product_id = None          # product ID
        self.hw_id = None               # hardware info
        self.__version = None           # product release
        self.__url = None               # product URL
        self.schema = None              # schema URL
        self.info = None                # additionnal info
        
        # Unsupported stuffs
        self.unsupported_attributes = []
        self.unsupported_methods = []
        self.unsupported_notifications = []
        # Alive management
        self.alive_period = config.alive_timer # time in sec between two alive
        self.next_alive = 0
        # Default attributes & methods
        self.__attributes = Attributes()
        self.methods = {'get_attributes' : self._get_attributes,
                        'get_description': self._get_description }
        self.engine = engine

    @property
    def dev_type(self):
        return self.__dev_type

    @dev_type.setter
    def dev_type(self, value):
        if not tools.is_valid_dev_type(value):
            raise DeviceError(f"The dev_type {value} is not valid")
        self.__dev_type = value

    @property
    def version(self):
        return self.__version

    @version.setter
    def version(self, value):
        # version must be a string
        if value:
            self.__version = "%s" % value
        else:
            self.__version = None

    @property
    def address(self):
        return self.__address

    @address.setter
    def address(self, value):
        if value == None:
            self.__address = None
            return
        if not tools.is_valid_address(value):
            raise DeviceError("This address is not valid")
        self.__address = value

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self,value):
        if value == None:
            self.__url = None
        else:
            self.__url = bindings.URL(value)

    # attributes
    def new_attribute(self,name,default=None):
        attr = Attribute(name,self,default)
        self.add_attribute(attr)
        return attr

    def add_attribute(self, attr):
        if attr:
            self.__attributes.append(attr)
            attr.device = self
    
    def del_attribute(self,attr):
        if attr:
            attr.device = None
            self.__attributes.remove(attr)

    def get_attribute(self,name):
        for attr in self.__attributes:
            if attr.name == name:
                return attr
        return None

    @property
    def attributes(self):
        return self.__attributes

    @attributes.setter
    def attributes(self,values):
        if isinstance(values,Attributes):
            self.__attributes = values
        else:
            raise DeviceError("Invalid attributes list, use class Attributes)")

    def add_method(self,name,func):
        self.methods.update({name:func})

    def get_methods(self):
        return self.methods

    def update_alive(self):
        """ update the alive timimg"""
        self.next_alive = time.time() + self.alive_period

    def get_timeout(self):
        """ return Alive timeout used for isAlive msg"""
        return 2 * self.alive_period

    #####################################################
    # Usefull methods
    #####################################################
    def dump(self):
        print("= Device: %s" % self)
        # info & description
        r = []
        r.append(['dev_type',self.dev_type])
        r.append(['address',self.address])
        for k,v in self._get_description().items():
            r.append([k,v])
        print(tabulate(r,tablefmt="fancy_grid"))
        
        # attributes
        if len(self._get_attributes()) > 0:
            r = []
            for k,v in self._get_attributes().items():
                r.append([k,str(v)])
            print(tabulate(r,tablefmt="fancy_grid"))

        # methods
        if len(self.methods) > 0:
            r = []
            for k,v in self.methods.items():
                r.append([k,v.__name__])
            print(tabulate(r,tablefmt="fancy_grid"))


    def __repr__(self):
        return f"<xaal.Device {id(self):x} {self.address} {self.dev_type}>"

    #####################################################
    # default public methods
    #####################################################
    def _get_description(self):
        result = {}
        if self.vendor_id:  result['vendor_id']  = self.vendor_id
        if self.product_id: result['product_id'] = self.product_id
        if self.version:    result['version']    = self.version
        if self.url:        result['url']        = self.url
        if self.schema:     result['schema']     = self.schema
        if self.info:       result['info']       = self.info
        if self.hw_id:      result['hw_id']      = self.hw_id
        if self.group_id:   result['group_id']   = self.group_id
        if self.unsupported_methods:       result['unsupported_methods']       = self.unsupported_methods
        if self.unsupported_notifications: result['unsupported_notifications'] = self.unsupported_notifications
        if self.unsupported_attributes:    result['unsupported_attributes']    = self.unsupported_attributes
        return result

    def _get_attributes(self, _attributes=None):
        """
        attributes:
            - None = body empty and means request all attributes
            - Empty array means request all attributes
            - Array of attributes (string) and means request attributes in the
              list

        TODO: (Waiting for spec. decision) add test on attribute devices
            - case physical sensor not responding or value not ready add error
            with specific error code and with value = suspicious/stale/cached
        """
        result = {}
        dev_attr = {attr.name: attr for attr in self.__attributes}
        if _attributes:
            # Process attributes filter
            for attr in _attributes:
                if attr in dev_attr.keys():
                    result.update({dev_attr[attr].name: dev_attr[attr].value})
                else:
                    logger.debug(f"Attribute {attr} not found")
        else:
            # Process all attributes
            for attr in dev_attr.values():
                result.update({attr.name: attr.value})
        return result

    def send_notification(self,notification,body={}):
        """ queue an notification, this is just a method helper """
        if self.engine:
            self.engine.send_notification(self,notification,body)
