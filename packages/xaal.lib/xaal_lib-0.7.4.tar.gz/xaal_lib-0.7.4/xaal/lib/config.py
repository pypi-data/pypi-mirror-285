
# Default configuration
import os
import sys
import binascii
from configobj import ConfigObj

self = sys.modules[__name__]

# Default settings
DEF_ADDR = '224.0.29.200'       # mcast address
DEF_PORT = 1236                 # mcast port
DEF_HOPS = 10                   # mcast hop
DEF_ALIVE_TIMER = 100           # Time between two alive msg
DEF_CIPHER_WINDOW = 60 * 2      # Time Window in seconds to avoid replay attacks
DEF_QUEUE_SIZE = 10             # How many packet we can send in one loop
DEF_LOG_LEVEL = 'DEBUG'         # should be INFO|DEBUG|None
DEF_LOG_PATH  = '/var/log/xaal' # where log are 

# TBD : Move this stuff
STACK_VERSION = 7


if 'XAAL_CONF_DIR' in os.environ:
    self.conf_dir = os.environ['XAAL_CONF_DIR']
else:
    self.conf_dir = os.path.expanduser("~") + '/.xaal'


def load_config(name='xaal.ini'):
    filename = os.path.join(self.conf_dir, name)
    if not os.path.isfile(filename):
        print("Unable to load xAAL config file [%s]" % filename)
        sys.exit(-1)

    cfg = ConfigObj(filename)
    self.address       = cfg.get('address',DEF_ADDR)
    self.port          = int(cfg.get('port',DEF_PORT))
    self.hops          = int(cfg.get('hops',DEF_HOPS))
    self.alive_timer   = int(cfg.get('alive_timer',DEF_ALIVE_TIMER))
    self.cipher_window = int(cfg.get('ciper_window',DEF_CIPHER_WINDOW))
    self.queue_size    = int(cfg.get('queue_size',DEF_QUEUE_SIZE))
    self.log_level     = cfg.get('log_level',DEF_LOG_LEVEL)
    self.log_path      = cfg.get('log_path',DEF_LOG_PATH)
    key = cfg.get('key',None)

    if key:
        self.key = binascii.unhexlify(key.encode('utf-8'))
    else:
        print("Please set key in config file [%s]" % filename)
        self.key = None

load_config()
