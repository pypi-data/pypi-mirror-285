import time
import random
from enum import Enum

from xaal.lib import tools, config
from xaal.lib import Message


import logging
logger = logging.getLogger(__name__)

# how often we force refresh the devices attributes/description/keyvalues
REFRESH_RATE = 600
BOOT_TIMER = 1
REFRESH_TIMER = 7
AUTOWASH_TIMER = 10


def now():
    return int(time.time())


class TimedDict(dict):
    def __init__(self,refresh_rate=REFRESH_RATE,data={}):
        dict.__init__(self,data)
        self.last_update = 0
        self.next_update = 0

    def updated(self):
        self.last_update = now()
        self.next_update = self.last_update + REFRESH_RATE + random.randint(-30, 30)

    def __setitem__(self, key, item):
        super().__setitem__(key,item)
        self.updated()

    def update(self,dict_):
        changed = False if self.last_update !=0 else True
        if dict_!= self:
            changed = True
        super().update(dict_)
        self.updated()
        return changed

    def is_ready(self):
        return True if (self.last_update != 0) else False


class Device:
    def __init__(self, addr, dev_type):
        self.address = addr
        self.short_address = tools.reduce_addr(addr)
        self.dev_type = dev_type
        # device cache
        self.attributes  = TimedDict(refresh_rate=REFRESH_RATE)
        self.description = TimedDict(refresh_rate=REFRESH_RATE*3)
        self.db          = TimedDict(refresh_rate=REFRESH_RATE*3)
        # Alive management
        self.last_alive = now()
        self.next_alive = 0

    def update_attributes(self, data):
        """ rude update attributes. Return true if updated"""
        # really not the best comparaison, but we just need a flag
        return self.attributes.update(data)

    def update_description(self, data):
        """
        group_id = data.get('groupId',None)
        if group_id:
            data['groupId'] = tools.bytes_to_uuid(group_id)
        """
        return self.description.update(data)

    def update_db(self,data):
        return self.db.update(data)

    def set_db(self,data):
        purge = []
        for k in data:
            if data[k]==None:
                purge.append(k)
        r = self.db.update(data)
        for k in purge:
            self.db.pop(k)
        return r

    def is_ready(self):
        if self.attributes.is_ready() and self.description.is_ready() and self.db.is_ready():
        #if self.description.is_ready():
            return True
        return False

    def alive(self,value):
        self.last_alive = int(time.time())
        self.next_alive = self.last_alive + value

    def get_kv(self,key):
        return self.db.get(key,None)

    def dump(self):
        print("*** %s %s **" % (self.address,self.dev_type))
        print("    Description : %s" % self.description)
        print("    Attributes : %s" % self.attributes)
        print()

    @property
    def display_name(self):
        result = tools.reduce_addr(self.address)
        result = self.db.get('nickname',result)
        result = self.db.get('name',result)
        return result

class Devices:
    """ Device List for monitoring """
    def __init__(self):
        self.__devs = {}
        self.__list_cache = None

    def add(self,addr,dev_type):
        dev = Device(addr,dev_type)
        self.__devs.update({addr : dev})
        self.__list_cache = None
        return dev

    def remove(self, addr):
        del self.__devs[addr]
        self.__list_cache = None

    def get(self):
        if not self.__list_cache:
            #print("Refresh cache")
            res = list(self.__devs.values())
            res.sort(key = lambda d: d.dev_type)
            self.__list_cache = res
        return self.__list_cache

    def get_with_addr(self, addr):
        try:
            return self.__devs[addr]
        except KeyError:
            return None

    def get_with_group(self, addr):
        r = []
        for d in self.get():
            if addr==d.description.get('group_id', None):
                r.append(d)
        return r

    def get_with_dev_type(self,dev_type):
        r = []
        for d in self.get():
            if d.dev_type == dev_type:
                r.append(d)
        return r

    def get_with_key(self,key):
        r = []
        for d in self.get():
            if key in d.db:
                r.append(d)
        return r

    def get_with_key_value(self,key,value):
        r = []
        for d in self.get():
            if (key in d.db) and (d.db[key]==value):
                r.append(d)
        return r

    def fetch_one_kv(self,key,value):
        r = self.get_with_key_value(key,value)
        try:
            return r[0]
        except IndexError:
            return None

    def get_dev_types(self):
        """ return the list of distinct dev_types"""
        l = []
        for dev in self.__devs.values():
            if dev.dev_type not in l:
                l.append(dev.dev_type)
        l.sort()
        return l

    def __len__(self):
        return len(self.__devs)

    def __getitem__(self,idx):
        if isinstance(idx, str):
            return self.__devs[idx]
        return self.get()[idx]

    def __repr__(self):
        return str(self.get())

    def __contains__(self,key):
        return key in self.__devs

    def auto_wash(self):
        now_ =now()
        result = []
        for dev in self.get():
            if dev.next_alive < now_:
                logger.info("Needed Auto Wash %s" % dev.address)
                result.append(dev)
        return result

    def dump(self):
        for d in self.get():
            print("%s %s" % (d.address,d.dev_type))


class Notification(Enum):
    new_device          = 0
    drop_device         = 1  # sending drop_device notif is not implemented yet,
    attribute_change    = 2
    description_change  = 3
    metadata_change     = 4


class Monitor:
    """
    use this class to monitor a xAAL network
    """
    def __init__(self,device,filter_func=None,db_server=None):
        self.dev = device
        self.engine = device.engine
        self.db_server = db_server

        self.boot_finished = False
        self.last_isalive = 0
        self.devices = Devices()
        self.filter = filter_func
        self.subscribers = []

        self.engine.subscribe(self.on_receive_msg)
        # disable all engine filtering
        self.engine.disable_msg_filter()
        # only send isAlive message every 2 expirations
        self.send_is_alive()
        self.engine.add_timer(self.refresh_alives,REFRESH_TIMER)
        # delete expired device every 10s 
        self.engine.add_timer(self.auto_wash, AUTOWASH_TIMER)
        # wait x seconds for the first isAlive answers before the initial crawl
        self.refresh_timer = self.engine.add_timer(self.refresh_devices, BOOT_TIMER)

    def on_receive_msg(self, msg: Message):
        # do nothing for some msg
        if (self.filter!=None) and self.filter(msg)==False:
            return
        if msg.source not in self.devices:
            dev = self.add_device(msg)
            self.notify(Notification.new_device,dev)

        dev = self.devices.get_with_addr(msg.source)

        if msg.is_alive():
            dev.alive(msg.body.get('timeout', config.DEF_ALIVE_TIMER))

        elif msg.is_request_isalive():
            self.last_isalive = now()

        elif msg.is_attributes_change() or msg.is_get_attribute_reply():
            if dev.update_attributes(msg.body):
                self.notify(Notification.attribute_change,dev)

        elif msg.is_get_description_reply():
            if dev.update_description(msg.body):
                self.notify(Notification.description_change,dev)

        elif self.is_from_metadb(msg):
            addr = msg.body.get('device')
            target = self.devices.get_with_addr(addr)
            changed = False
            if target and 'map' in msg.body:
                if self.is_reply_metadb(msg):
                    changed = target.set_db(msg.body['map'])
                if self.is_update_metadb(msg):
                    changed = target.update_db(msg.body['map'])
                if changed:
                    self.notify(Notification.metadata_change,target)

    def subscribe(self,func):
        self.subscribers.append(func)

    def unsubscribe(self,func):
        self.subscribers.remove(func)

    def notify(self,ev_type,device):
        for s in self.subscribers:
            #logger.warning(f"{s} {ev_type}")
            s(ev_type,device)

    def add_device(self,msg):
        return self.devices.add(msg.source,msg.dev_type)

    def auto_wash(self):
        """call the Auto-wash on devices List"""
        devs = self.devices.auto_wash()
        for d in devs:
            self.notify(Notification.drop_device, d)
            self.devices.remove(d.address)

    def send_is_alive(self):
        self.engine.send_is_alive(self.dev)
        self.last_isalive = now()

    def refresh_alives(self):
        """ every REFRESH we check if need to send a isAlive"""
        tmp = self.last_isalive + config.alive_timer * 2
        if tmp < now():
            self.send_is_alive()
        
    def refresh_devices(self):
        now_ = now()
        cnt = 0
        for dev in self.devices:
            # description
            if dev.description.next_update < now_:
                self.request_description(dev.address)
                dev.description.next_update = now_ + REFRESH_RATE
                cnt = cnt +1                
            # metadata
            if self.db_server and dev.db.next_update < now_:
                self.request_metadb(dev.address)
                dev.db.next_update = now_ + REFRESH_RATE
                cnt = cnt +1
            # attributes
            if dev.attributes.next_update < now_:
                self.request_attributes(dev.address)
                dev.attributes.next_update = now_ + REFRESH_RATE
                cnt = cnt +1

            if cnt > 40:
                break
        # switch to normal timer after boot
        if self.boot_finished == False and cnt == 0 and len(self.devices)!=0:
            self.refresh_timer.period = REFRESH_TIMER
            logger.debug("Switching to slow refresh timer")
            self.boot_finished = True
        elif cnt!=0:
            logger.debug("request queued: %d" % cnt )

    def request_metadb(self,addr):
        if self.db_server:
            self.engine.send_request(self.dev,[self.db_server,],'get_keys_values',{'device':addr})

    def request_attributes(self,addr):
        self.engine.send_get_attributes(self.dev,[addr,])

    def request_description(self,addr):
        self.engine.send_get_description(self.dev,[addr,])

    def is_from_metadb(self,msg):
        if (msg.is_notify() or msg.is_reply()) and msg.source == self.db_server : 
            return True
        return False

    def is_reply_metadb(self,msg):
        if msg.is_reply() and msg.action == 'get_keys_values' and msg.source == self.db_server:
            return True
        return False

    def is_update_metadb(self,msg):
        if msg.is_notify() and msg.action == 'keys_values_changed' and msg.source == self.db_server:
            return True
        return False

    def debug_timers(self):
        for dev in self.devices:
            print("%s\t%s\t%d\t%d\t%d" % (dev.address,dev.dev_type,dev.description.last_update,dev.db.last_update,dev.attributes.last_update))
