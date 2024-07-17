"""
This module provides a set of utilities to interact with the xAAL bus and devices.
The module use a lot of AsyncEngine features, so the code can be a bit tricky to read.
If you're looking for simples examples, please check the legacy tools instead.
"""

import sys

if sys.argv[0].endswith('pkgrun'):
    # right now, some packages depend on gevent, so we need to import it here.
    # this is only needed for the pkgrun command
    try:
        from gevent import monkey
        monkey.patch_all(thread=False)
        # print("Loaded gevent")
    except ModuleNotFoundError:
        pass

# xAAL import
from xaal.lib import AsyncEngine, Device, tools, helpers, config
from xaal.lib.messages import MessageType

# General python import
import asyncio
import time
import importlib
import logging
import enum
import optparse

# colors & styles
from colored import fore, style
from tabulate import tabulate
import pprint
import shutil  # needed by the tail command


HIDE_ACTION = ['get_attributes', 'get_description', 'get_keys_values', 'get_devices', 'is_alive']
TABLE_STYLE = 'psql'
LINE = "="*78
DB_DEV_TYPE = "metadatadb.basic"


class Colors(enum.Enum):
    DEFAULT   = fore.WHITE
    # ALIVE     = fore.LIGHT_GRAY
    # ATTRIBUTS = fore.LIGHT_YELLOW
    # REQUEST   = fore.LIGHT_RED
    # IS_ALIVE  = fore.LIGHT_MAGENTA
    # REPLY     = fore.LIGHT_CYAN
    # NOTIFY    = fore.LIGHT_GREEN
    # DEV_TYPE  = fore.LIGHT_BLUE
    # ADDR      = fore.LIGHT_RED
    # INFO      = fore.CYAN
    # DB        = fore.SPRING_GREEN_1

    ALIVE     = fore.LIGHT_GRAY
    ATTRIBUTS = fore.YELLOW
    REQUEST   = fore.RED
    IS_ALIVE  = fore.MAGENTA
    REPLY     = fore.CYAN
    NOTIFY    = fore.LIGHT_GREEN
    DEV_TYPE  = fore.BLUE
    ADDR      = fore.RED
    INFO      = fore.CYAN
    DB        = fore.SPRING_GREEN_1

    def __str__(self):
        return self.value


class DeviceInfo(object):
    def __init__(self):
        self.alive = False
        self.address = None
        self.dev_type = None
        self.description = None
        self.attributes = None
        self.db = None
        self.ready_event = asyncio.Event()
        self.displayed = False

    def ready(self):
        if self.address is None:
            return False
        if self.dev_type is None:
            return False
        if self.description is None:
            return False
        if self.attributes is None:
            return False
        return True

    def display(self, color=True):
        if color:
            self.color_display()
        else:
            self.normal_display()

    def color_display(self):
        # info & description
        r = []
        r.append(['Informations', ''])
        r.append(['============', ''])
        r.append(["alive", colorize(Colors.IS_ALIVE, self.alive)])
        r.append(['dev_type', colorize(Colors.DEV_TYPE, self.dev_type)])
        r.append(['address', colorize(Colors.ADDR, self.address)])
        if self.description and len(self.description) > 0:
            for k, v in self.description.items():
                if k == 'info':
                    v = colorize(Colors.INFO, v)
                else:
                    v = colorize(Colors.DEFAULT, v)
                r.append([k, v])

        # attributes
        if self.attributes and len(self.attributes) > 0:
            # tabulate has no minimal width so used this trick
            r.append(['-'*22, '-'*46])
            r.append(['Attributes', ''])
            r.append(['==========', ''])
            for k, v in self.attributes.items():
                v = pprint.pformat(v, width=55).split('\n')
                tmp = ''
                for line in v:
                    tmp = tmp + colorize(Colors.ATTRIBUTS, line) + '\n'
                r.append([k, tmp])

        # metadata
        if self.db and len(self.db.keys()) > 0:
            r.append(['-'*22, '-'*46])
            r.append(['Metadata', ''])
            r.append(['========', ''])
            for k, v in self.db.items():
                v = colorize(Colors.DB, v)
                r.append([k, v])
        print(tabulate(r, tablefmt=TABLE_STYLE))

    def normal_display(self):
        # info & description
        r = []
        r.append(['Informations', ''])
        r.append(['============', ''])
        r.append(["alive", self.alive])
        r.append(['dev_type', self.dev_type])
        r.append(['address', self.address])
        for k, v in self.description.items():
            r.append([k, v])

        # attributes
        if len(self.attributes) > 0:
            # tabulate has no minimal width so used this trick
            r.append(['-'*22, '-'*46])
            r.append(['Attributes', ''])
            r.append(['==========', ''])
            for k, v in self.attributes.items():
                v = pprint.pformat(v, width=55).split('\n')
                tmp = ''
                for line in v:
                    tmp = tmp + line + '\n'
                r.append([k, tmp])
        # metadata
        if self.db and len(self.db.keys()) > 0:
            r.append(['-'*22, '-'*46])
            r.append(['Metadata', ''])
            r.append(['========', ''])
            for k, v in self.db.items():
                r.append([k, v])
        print(tabulate(r, tablefmt=TABLE_STYLE))


class ToolboxHelper(object):
    def __init__(self) -> None:
        self.name = None       # cmdline name
        self.parser = None
        self.engine = None     # toolbox engine
        self.device = None     # current device
        self.devices = []      # devices list (alive / walker)
        # idle detector / force exit
        self.exit_event = asyncio.Event()
        self.last_msg_time = now()

        # display time
        self.start_time = 0

        # db server
        self.db_server = None
        self.db_server_found = asyncio.Event()

        # Let's start
        self.setup_name()
        self.setup_parser()

    def setup_name(self):
        name = sys.argv[0].split('/')[-1]
        # helpers.set_console_title(name)
        self.name = name
        return self.name

    def setup_parser(self, usage=None):
        self.parser = optparse.OptionParser(usage=usage)
        self.parser.add_option("-c", dest="no_color", help="disable color", action="store_true", default=False)
        self.parser.add_option("-l", dest="debug", help="Enable logging", action="store_true", default=False)
        self.parser.add_option("-a", dest="mcast_addr", help="Multicast address", default=config.address)
        self.parser.add_option("-p", dest="mcast_port", help="Multicast port", default=config.port)
        return self.parser

    def setup_device(self):
        # toolbox device
        dev = Device("cli.basic")
        dev.address = tools.get_random_uuid()
        dev.info = f'Aiotoolbox CLI {self.name}'
        self.device = dev
        self.engine.add_device(self.device)
        return self.device

    def setup_engine(self):
        # engine
        bus_addr = self.options.mcast_addr
        try:
            bus_port = int(self.options.mcast_port)
        except ValueError:
            self.error("Invalid port number")
        eng = AsyncEngine(address=bus_addr, port=bus_port)
        eng.disable_msg_filter()
        # start the engine
        self.engine = eng
        self.start_time = now()
        eng.start()
        return eng

    def setup_basic(self):
        eng = self.setup_engine()
        dev = self.setup_device()
        return (eng, dev)

    #####################################################
    # command line parsing
    #####################################################
    def setup_msg_parser(self):
        self.engine.subscribe(self.parse_msg)

    def parse(self):
        self.options, self.args = self.parser.parse_args()
        if self.options.debug:
            helpers.setup_console_logger()
        return self.options, self.args

    def check_address(self, value):
        addr = None
        if value:
            addr = tools.get_uuid(value)
            if addr is None:
                self.error(f"Invalid address: {value}")
        return addr

    def check_devtype(self, value):
        dev_type = 'any.any'
        if value:
            if not tools.is_valid_dev_type(value):
                self.error("Invalid device type: %s" % value)
            dev_type = value
        return dev_type

    #####################################################
    # devices
    #####################################################
    def add_device(self, dev):
        if dev.address:
            if self.get_device(dev.address):
                # device already know
                return
        self.devices.append(dev)

    def get_device(self, addr):
        for k in self.devices:
            if k.address == addr:
                return k
        return None

    def new_device(self, addr):
        dev = DeviceInfo()
        dev.address = addr
        self.add_device(dev)
        return dev

    def display_device(self, dev):
        # show device only once
        if dev.displayed:
            return

        if self.options.no_color:
            dev.normal_display()
        else:
            dev.color_display()
        dev.displayed = True

    def is_ready(self, dev):
        if self.db_server:
            if dev.db is None:
                return False
        return dev.ready()

    #####################################################
    # messages
    #####################################################
    def dump_msg(self, msg):
        color = not self.options.no_color
        color_value = self.color_for_msg(msg)
        if color:
            print(color_value, end='')
        msg.dump()
        if color:
            print(style.RESET, end='')

    def color_for_msg(self, msg):
        color_value = Colors.DEFAULT
        if msg.is_request_isalive():
            color_value = Colors.IS_ALIVE
        elif msg.is_alive():
            color_value = Colors.ALIVE
        elif msg.is_attributes_change():
            color_value = Colors.ATTRIBUTS
        elif msg.is_request():
            color_value = Colors.REQUEST
        elif msg.is_reply():
            color_value = Colors.REPLY
        elif msg.is_notify():
            color_value = Colors.NOTIFY
        return color_value

    def parse_msg(self, msg):
        """ default parser used for info/walker"""
        target = self.get_device(msg.source)
        if target is None:
            target = DeviceInfo()
            target.address = msg.source
            target.dev_type = msg.dev_type
            self.add_device(target)
        if target.dev_type is None:
            target.dev_type = msg.dev_type
        if msg.is_get_attribute_reply():
            target.attributes = msg.body
        elif msg.is_get_description_reply():
            target.description = msg.body
        elif msg.is_alive():
            target.alive = True
        return target

    def parse_db_msg(self, msg):
        found = msg.body.get('device', None)
        found_map = msg.body.get('map', None)
        tmp = self.get_device(found)
        if not tmp:
            tmp = self.new_device(found)
        tmp.db = found_map
        return tmp

    def request_info(self, addr):
        self.engine.send_get_description(self.device, [addr])
        self.engine.send_get_attributes(self.device, [addr])

    def request_is_alive(self, addr=None, dev_type=None):
        if addr:
            self.engine.send_is_alive(self.device, [addr])
        elif dev_type:
            self.engine.send_is_alive(self.device, dev_types=[dev_type])
        else:
            self.engine.send_is_alive(self.device)

    def request_action(self, addr, action, body=None):
        self.engine.send_request(self.device, [addr], action, body)

    #####################################################
    # db server
    #####################################################
    def find_db_callback(self, msg):
        if not match_dev_type(msg, DB_DEV_TYPE):
            return
        # new db server found
        if msg.is_alive():
            self.db_server = msg.source
            self.db_server_found.set()

    async def find_db_server(self):
        self.engine.subscribe(self.find_db_callback)
        self.engine.send_is_alive(self.device, dev_types=[DB_DEV_TYPE])
        await wait_for_event(self.db_server_found, timeout=0.3)
        self.engine.unsubscribe(self.find_db_callback)

    def request_db_values(self, addr):
        if self.db_server:
            self.engine.send_request(self.device, [self.db_server, ], "get_keys_values", {'device': addr})

    def request_db_devices(self, key, value):
        if self.db_server:
            self.engine.send_request(self.device, [self.db_server, ], "get_devices", {'key': key, 'value': value})

    def is_db_reply(self, msg):
        if match_dev_type(msg, DB_DEV_TYPE) and msg.is_reply() and self.device.address in msg.targets:
            return True
        return False

    #####################################################
    # start/stop/idle/error
    #####################################################
    async def wait_completed(self, timeout=0.5):
        """wait until exit event is set"""
        await wait_for_event(self.exit_event, timeout=timeout)

    def update_idle(self):
        self.last_msg_time = now()

    async def idle_detector(self):
        while True:
            await asyncio.sleep(0.1)
            if now() - self.last_msg_time > 0.4:
                break
        self.quit()

    def run_until_timeout(self, timeout=3):
        """ run the engine until timeout """
        self.engine.add_timer(self.quit, timeout)
        self.engine.run()

    def run_until_idle(self):
        self.engine.new_task(self.idle_detector())
        self.engine.run()

    def run_forever(self):
        self.engine.run()

    def quit(self):
        self.engine.shutdown()
        print()
        print(LINE)
        print(f"Found devices: {len(self.devices)}")
        if self.db_server:
            print(f"Metadb server: {self.db_server}")
        t = round(now() - self.start_time, 2)
        print(f"Total runtime: {t}s")
        print(LINE)

    def error(self, error_msg):
        print(f"error: {error_msg}")
        self.parser.print_help()
        exit(1)


def colorize(color, text):
    return f"{color}{text}{style.RESET}"


def now():
    return time.time()


def match_dev_type(msg, dev_type):
    if dev_type == 'any.any':
        return True
    if dev_type.endswith('.any'):
        subtype = msg.dev_type.split('.')[0] + '.any'
        if subtype == dev_type:
            return True
    else:
        if msg.dev_type == dev_type:
            return True
    return False


def match_address(msg, addr):
    if (msg.source == addr) or (addr in msg.targets):
        return True
    return False


async def wait_for_event(event, timeout):
    """ wait for a given event or timeout"""
    wait_task = asyncio.create_task(event.wait())
    await asyncio.wait([wait_task], timeout=timeout)


#####################################################
# dumper
#####################################################
def dumper():
    helper = ToolboxHelper()
    helper.parser.add_option("-f", dest="filter_address", help="only show given address")
    helper.parser.add_option("-t", dest="filter_type", help="only show given device type")

    helper.parse()
    target = helper.check_address(helper.options.filter_address)
    dev_type = helper.check_devtype(helper.options.filter_type)

    eng = helper.setup_engine()

    async def dumper_callback(msg):
        # filter by address or dev_type
        if target and not match_address(msg, target):
            return
        if dev_type and not match_dev_type(msg, dev_type):
            return

        # dump message
        helper.dump_msg(msg)

    eng.subscribe(dumper_callback)
    helper.run_forever()

#####################################################
# alive
#####################################################
def is_alive():
    helper = ToolboxHelper()
    helper.parser.add_option("-t", dest="filter_type", help="only show given device type")
    helper.parse()
    dev_type = helper.check_devtype(helper.options.filter_type)
    color = not helper.options.no_color

    (eng, dev) = helper.setup_basic()

    async def alive_callback(msg):
        if (msg.source == dev.address) or (msg.is_alive() is False):
            return
        if match_dev_type(msg, dev_type) is False:
            return

        # idle detectiong
        helper.update_idle()
        if helper.get_device(msg.source) is None:
            helper.parse_msg(msg)
            if color:
                print(f"{colorize(Colors.ADDR,msg.source)}: {colorize(Colors.DEV_TYPE,msg.dev_type)}")
            else:
                print(f"{msg.source}: {msg.dev_type}")

    def start():
        print(LINE)
        helper.request_is_alive(dev_type=dev_type)

    eng.subscribe(alive_callback)
    eng.on_start(start)
    helper.run_until_idle()

#####################################################
# info
#####################################################
def info():
    helper = ToolboxHelper()
    # redefine parser to add usage
    helper.setup_parser("Usage: %prog [options] device_address")
    (_, args) = helper.parse()
    # command line address
    if len(args) != 1:
        helper.error("empty address")
    target = tools.get_uuid(args[0])
    if target is None:
        helper.error("Invalid address: %s" % args[0])

    (eng, dev) = helper.setup_basic()

    def ready_to_show(dev):
        if dev and helper.is_ready(dev):
            helper.display_device(dev)
            helper.exit_event.set()

    def info_callback(msg, addr=target):
        # collecting description and attributes
        if msg.source != addr:
            return
        found = helper.parse_msg(msg)
        ready_to_show(found)

    def query_db_callback(msg):
        if helper.is_db_reply(msg):
            found = helper.parse_db_msg(msg)
            ready_to_show(found)

    async def run():
        await helper.find_db_server()
        if helper.db_server:
            helper.request_db_values(target)
            eng.subscribe(query_db_callback)
        helper.request_is_alive(addr=target)
        helper.request_info(target)
        await helper.wait_completed()
        helper.quit()

    eng.subscribe(info_callback)
    eng.on_start(run)
    helper.run_forever()

#####################################################
# walker
#####################################################
def walker():
    helper = ToolboxHelper()
    helper.parser.add_option("-t", dest="filter_type", help="only show given device type")
    helper.parse()
    dev_type = helper.check_devtype(helper.options.filter_type)
    (eng, dev) = helper.setup_basic()

    def ready_to_show(dev):
        if dev and helper.is_ready(dev):
            helper.display_device(dev)

    async def walker_callback(msg):
        if msg.source == dev.address:
            return
        if match_dev_type(msg, DB_DEV_TYPE):
            return
        if match_dev_type(msg, dev_type) is False:
            return

        found = helper.parse_msg(msg)
        helper.update_idle()
        if msg.is_alive():
            if not found.ready():
                helper.request_info(msg.source)
                helper.request_db_values(msg.source)
        ready_to_show(found)

    async def query_db_callback(msg):
        if helper.is_db_reply(msg):
            helper.update_idle()
            found = helper.parse_db_msg(msg)
            ready_to_show(found)

    async def start():
        await helper.find_db_server()
        helper.update_idle()
        if helper.db_server:
            eng.subscribe(query_db_callback)
        eng.subscribe(walker_callback)
        helper.request_is_alive(dev_type=dev_type)

    eng.on_start(start)
    helper.run_until_idle()

#####################################################
# log
#####################################################
def log():
    helper = ToolboxHelper()
    helper.parser.add_option("-f", dest="filter_address", help="only show given address")
    helper.parser.add_option("-t", dest="filter_type", help="only show given device type")
    helper.parse()

    target = helper.check_address(helper.options.filter_address)
    dev_type = helper.check_devtype(helper.options.filter_type)
    color = not helper.options.no_color

    eng = helper.setup_engine()

    def log_callback(msg):
        if msg.is_alive() or (msg.action in HIDE_ACTION):
            return
        if target and not match_address(msg, target):
            return
        if dev_type and not match_dev_type(msg, dev_type):
            return

        color_value = Colors.DEFAULT
        if msg.is_attributes_change():
            color_value = Colors.ATTRIBUTS
        elif msg.is_notify():
            color_value = Colors.NOTIFY
        elif msg.is_request():
            color_value = Colors.REQUEST
        elif msg.is_reply():
            color_value = Colors.REPLY

        if color:
            dump = f"{Colors.DEFAULT}{time.ctime()} {Colors.ADDR}{msg.source} {Colors.DEV_TYPE}{msg.dev_type}\t{color_value}{msg.action} {msg.body}{style.RESET}"
        else:
            dump = f"{time.ctime()} {msg.source} {msg.dev_type}\t{msg.action} {msg.body}"
        print(dump)

    eng.subscribe(log_callback)
    helper.run_forever()

#####################################################
# query db
#####################################################
def query_db():
    helper = ToolboxHelper()
    helper.parser.add_option("-d", dest="device_address", help="search by device address")
    helper.parser.add_option("-k", dest="key", help="search by key")
    helper.parser.add_option("-v", dest="value", help="search by value")
    helper.parse()
    # command line parsing
    target = helper.check_address(helper.options.device_address)
    key = helper.options.key
    value = helper.options.value
    color = not helper.options.no_color

    if target and key:
        helper.error("-d and -k are exclusive")

    if not (target or key):
        helper.error("-d or -k is required")

    if value and not key:
        helper.error("-v requires -k")

    (eng, dev) = helper.setup_basic()

    def device_callback(msg):
        # search by device address
        if helper.is_db_reply(msg):
            found = msg.body.get('device', None)
            found_map = msg.body.get('map', None)
            if found == target:
                r = []
                r.append(['Metadata', ''])
                r.append(['========', ''])
                if color:
                    r.append(['Server:', colorize(Colors.ADDR, helper.db_server)])
                else:
                    r.append(['Server:', helper.db_server])
                for k, v in found_map.items():
                    if color:
                        v = colorize(Colors.DB, v)
                    r.append([k, v])
                print(tabulate(r, tablefmt=TABLE_STYLE))
                helper.exit_event.set()

    def key_callback(msg):
        # search by key / value
        if helper.is_db_reply(msg):
            k = msg.body.get('key', None)
            v = msg.body.get('value', None)
            print(LINE)
            print(f"Search result for key={k} value={v}")
            print(LINE)
            devs = msg.body.get('devices', [])
            for dev in devs:
                if color:
                    print(f"- {colorize(Colors.ADDR,dev)}")
                else:
                    print(f"- {dev}")
            print(f"\n# Found {len(devs)} devices")
            helper.exit_event.set()

    async def run():
        await helper.find_db_server()
        if helper.db_server:
            # found db server, send request and wait to complete
            if target:
                eng.subscribe(device_callback)
                helper.request_db_values(target)
                await helper.wait_completed()
            elif key:
                eng.subscribe(key_callback)
                helper.request_db_devices(key, value)
                await helper.wait_completed()
        else:
            print("\nNo metadata server found")
        helper.quit()

    eng.on_start(run)
    helper.run_forever()

#####################################################
# cleanup db
#####################################################
def clean_db():
    helper = ToolboxHelper()
    helper.parse()

    (eng, dev) = helper.setup_basic()
    db_devices = []

    def alive_callback(msg):
        if (msg.source == dev.address) or (msg.is_alive() is False):
            return
        if helper.get_device(msg.source) is None:
            helper.parse_msg(msg)
            # print(msg)

    def devices_callback(msg):
        if helper.is_db_reply(msg) and msg.action == 'get_devices':
            r = msg.body.get('devices', [])
            for k in r:
                db_devices.append(k)

    async def gather():
        print("Gathering devices infos...")
        await asyncio.sleep(2)
        print("Done..")
        missing = []
        for k in db_devices:
            dev = helper.get_device(tools.get_uuid(k))
            if not dev:
                missing.append(k)
        for k in missing:
            drop = input(f"Drop {k} from db server ? [Y|*]")
            if drop == 'Y':
                body = {"device": k, "map": None}
                helper.request_action(helper.db_server, "update_keys_values", body)
                await asyncio.sleep(0)

    async def start():
        await helper.find_db_server()
        if helper.db_server:
            eng.subscribe(alive_callback)
            eng.subscribe(devices_callback)
            helper.request_is_alive()
            helper.request_db_devices(None, None)
            await gather()
            helper.quit()

        else:
            print("\nNo metadata server found")
        # helper.quit()

    eng.on_start(start)
    helper.run_forever()
    # helper.run_until_idle()

#####################################################
# send request
#####################################################
def send():
    helper = ToolboxHelper()
    helper.parser.add_option("-d", dest="target_address", help="target device address")
    helper.parser.add_option("-r", dest="request_action", help="request action")
    helper.parser.add_option("-b", dest="request_body", help="request body example: 'smooth:10 speed:20'")
    helper.parse()

    # cmd line parsing
    target = helper.check_address(helper.options.target_address)
    action = helper.options.request_action
    if not (target and action):
        helper.error("-d and -r are mandatory")
    # body parsing
    tmp = helper.options.request_body
    body = None
    if tmp:
        body = {}
        for k in tmp.split(' '):
            (i, j) = k.split(':')
            body[i] = j
    # let's go
    (eng, dev) = helper.setup_basic()

    def action_callback(msg):
        if msg.is_alive():
            return
        if msg.source == target:
            helper.dump_msg(msg)
            helper.exit_event.set()

    async def run():
        helper.request_action(target, action, body)
        # wait at least 1 msg
        await helper.wait_completed(2)
        helper.quit()

    eng.subscribe(action_callback)
    eng.on_start(run)
    helper.run_forever()

#####################################################
# tail msg
#####################################################
def tail():
    helper = ToolboxHelper()
    helper.parser.add_option("-f", dest="filter_address", help="only show given address")
    helper.parser.add_option("-t", dest="filter_type", help="only show given device type")
    helper.parser.add_option("-m", dest="filter_mode", help="hide some messages:\n 1=alives, 2=core actions, 3=replies, 4=all except notif")

    helper.parse()
    target = helper.check_address(helper.options.filter_address)
    dev_type = helper.check_devtype(helper.options.filter_type)
    mode = helper.options.filter_mode
    if mode:
        try:
            mode = int(mode)
        except ValueError:
            helper.error("-m must be an integer")
        if mode not in range(1, 5):
            helper.error("-m must be in range 1-4")
    else:
        mode = 0
    color = not helper.options.no_color
    eng = helper.setup_engine()

    def tail_callback(msg):
        if mode > 0 and msg.is_alive():
            return
        if target and not match_address(msg, target):
            return
        if dev_type and not match_dev_type(msg, dev_type):
            return
        if mode > 1 and msg.action in HIDE_ACTION:
            return
        if mode > 2 and msg.is_reply():
            return
        if mode > 3 and msg.is_request():
            return

        color_value = helper.color_for_msg(msg)
        schem = '*'
        if msg.msg_type == MessageType.REQUEST.value:
            schem = '>'
        elif msg.msg_type == MessageType.REPLY.value:
            schem = '<'
        elif msg.msg_type == MessageType.NOTIFY.value:
            schem = '='

        targets = [tools.reduce_addr(addr) for addr in msg.targets]
        tmp = shutil.get_terminal_size()[0] - (2 + 18 + 36 + 20 + 16 + 7)
        if tmp < 22:
            tmp = 22
        BODY_FORMAT = '%-22.'+str(tmp)+'s'
        FORMAT = '%-2.02s %-18.18s %-36.36s (%-20.20s) %-16.16s '+BODY_FORMAT
        res = FORMAT % (schem, msg.action, msg.source, msg.dev_type, targets, msg.body)
        if color:
            print(colorize(color_value, res))
        else:
            print(res)

    # FIXME: find a better way to do this
    print('\x1bc', end='')  # clear screen
    FORMAT = '%-2.02s %-18.18s %-36.36s (%-20.20s) %-16.16s %-22.22s'
    print(FORMAT % ('=', 'action', 'source', 'dev_type', 'targets', 'body'))

    eng.subscribe(tail_callback)
    helper.run_forever()

#####################################################
# run pkg
#####################################################
def pkgrun():
    helper = ToolboxHelper()
    # redefine parser to add usage
    helper.setup_parser("Usage: %prog [options] pkg1 pkg2 ...")
    (_, args) = helper.parse()
    eng = helper.setup_engine()
    logger = logging.getLogger(helper.name)

    def load_pkgs():
        for k in args:
            xaal_mod = 'xaal.' + k
            try:
                mod = importlib.import_module(xaal_mod)
            except ModuleNotFoundError:
                logger.critical("Unable to load module: %s" % xaal_mod)
                continue

            if hasattr(mod, 'setup') is False:
                logger.critical("Unable to find setup %s" % xaal_mod)
                continue
            logger.info(f"{xaal_mod} loaded")
            result = mod.setup(eng)
            if result is not True:
                logger.critical("something goes wrong with package: %s" % xaal_mod)

    load_pkgs()
    helper.run_forever()

#####################################################
# ipdb shell on steroid
#####################################################
def shell():
    helper = ToolboxHelper()
    helper.parse()
    eng = helper.setup_engine()
    eng.disable_msg_filter()

    # load IPython
    try:
        import IPython
        from IPython.lib import backgroundjobs
    except ModuleNotFoundError:
        print("Error: Unable to load IPython\n")
        print("Please install IPython to use xAAL shell")
        print("$ pip install ipython\n")
        exit(1)

    logging.getLogger("parso").setLevel(logging.WARNING)
    logging.getLogger("blib2to3").setLevel(logging.WARNING)

    # run the engine in background
    jobs = backgroundjobs.BackgroundJobManager()
    jobs.new(eng.run)

    # imported modules for convenient use in the shell
    from xaal.schemas import devices
    from xaal.lib import Message, Attribute, Device
    from xaal.monitor import Monitor

    IPython.embed(banner1="==============================  xAAL Shell ==============================",
                  banner2=f"* AsyncEngine running in background:\n* eng = {eng}\n\n",
                  colors="Linux",
                  confirm_exit=False,
                  separate_in='',
                  autoawait=True)

    print("* Ending Engine")
    eng.shutdown()
    print("* Bye bye")

