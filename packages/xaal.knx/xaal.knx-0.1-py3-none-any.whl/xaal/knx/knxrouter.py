
# xaal use multicast cnx too, so reuse it here. 
# TODO : drop this 

from xaal.lib import network 
from enum import Enum

from . import dpts
import logging
import struct
import time

EMPTY_FRAME = [0x6,0x10,0x5,0x30,0x0,0x0,0x29,0x0,0xbc,0xe0,0x0,0x0,0x0,0x0,0x1,0x0,0x0,]


logger = logging.getLogger(__name__)


def hex_dump(tab):
    for k in tab:
        print('0x%x' % k,end=',')
    print()

def bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result

def int_to_bytes(value, length):
    result = []
    for i in range(0, length):
        result.append(value >> (i * 8) & 0xff)
    result.reverse()
    return result


class KNXCommand(Enum):
    READ = 0x00
    RESP = 0x40
    WRITE = 0x80

class KNXcEMIException(Exception):pass

class KNXcEMI:
    def __init__(self,buf):
        self.parse(buf)
        self.check_sanity()

    def parse(self,buf):
        bytes_ = bytearray(buf)
        #MC if len(bytes_) < 17:
        if len(bytes_) < 16:
            raise KNXcEMIException("Packet to short %d" % len(bytes_))

        self.pkt = bytes_
        # header 
        self.header_lenght = bytes_[0]    # 0x6
        self.version       = bytes_[1]    # 0x10
        self.service       = bytes_[2:4]  # 0x0530 ROUTING_INDICATION
        #self.total_lenght
        # body
        self.msg_code        = bytes_[6]     # 0x29
        self.add_info_lenght = bytes_[7]     # 0x0
        self.ctr_field1      = bytes_[8]     # 0xbc
        self.ctr_field2      = bytes_[9]     # 0xe0
        #self.phy_addr
        #self.group_addr
        self.npdu_lenght     = bytes_[14]    # 0x1
        self.udt             = bytes_[15]    # 0x0 (unsused)
        #self.data   # 0x81 => write 1 / 0x80=> write 0 / 0x0 => read / 0x40 => response

    def check_sanity(self):
        if self.header_lenght != 0x06 : raise KNXcEMIException("Wrong header size 0x%x" % self.header_lenght)
        if self.version     != 0x10: raise KNXcEMIException("Wrong version 0x%x" % self.version)
        if self.service     != bytearray([0x05,0x30]): raise KNXcEMIException("Wrong service 0x%x 0x%x" % self.service[0] % self.service[1])
        if self.msg_code    != 0x29 : raise KNXcEMIException("Wrong msg_code 0x%x" % self.msg_code)
        if self.ctr_field1 not in [0xbc,0xb0] : raise KNXcEMIException("Wrong ctr_field1 0x%x" % self.ctr_field1)
        # JKX: ctr_field2 shoub in [0xe0,0xd0,0xc0] but Mael fix that to: 
        if self.ctr_field2 not in [0xe0,0xd0,0xc0,0xb0,0x40,0x50]: raise KNXcEMIException("Wrong ctr_field2 0x%x" % self.ctr_field2)
        # JKX : how could this arrive ? 
        #if self.npdu_lenght != 0x01 : raise KNXcEMIException("Wrong npdu_lenght 0x%x" % self.npdu_lenght)

    @property
    def total_lenght(self):
        return bytes_to_int(self.pkt[4:6])
    
    @total_lenght.setter
    def total_lenght(self,val):
        self.pkt[4:6] = int_to_bytes(val,2)

    @property
    def phy_addr(self):
        return dpts.decode['pa'](self.pkt[10:12])

    @phy_addr.setter
    def phy_addr(self,val):
        self.pkt[10:12] = dpts.encode['pa'](val)

    @property
    def group_addr(self):
        return dpts.decode['ga'](self.pkt[12:14])

    @group_addr.setter
    def group_addr(self,val):
        self.pkt[12:14] = dpts.encode['ga'](val)

    @property
    def command(self):
        try:
            cmd = KNXCommand(self.pkt[16] & 0xc0) # 0xc0 mask for 0x[0|4|8] in pload
        except ValueError:
            raise KNXcEMIException("wrong command pload : 0x%x" % self.pkt[16])
        return cmd

    @command.setter
    def command(self,cmd):
        self.pkt[16] = cmd.value

    @property
    def data(self):
        if self.total_lenght == 17: # last byte only ie: 0x81 => 1
            return bytearray([self.pkt[16]&0x3f])
        else:
            return self.pkt[17:]

    @data.setter
    def data(self,pload):
        if len(pload) == 1:
            self.pkt[16] = self.pkt[16]|pload[0]
        else:
            self.pkt.extend(pload)

    def __str__(self):
        r = "<KNXcEMI at 0x%x " % (id(self))
        r = r + "pa=%s ga=%s code=0x%x cmd=%s data=%s>" % (self.phy_addr,self.group_addr,self.msg_code,str(self.command),str(self.data))
        return r

class KNXConnector:
    def __init__(self,phy_addr='6.6.6'):
        self.phy_addr = phy_addr
        self.nc = network.NetworkConnector('224.0.23.12',3671,10)
        self.nc.connect()

    def _new_cemi(self,group_addr):
        cemi = KNXcEMI(EMPTY_FRAME)
        cemi.phy_addr = self.phy_addr
        cemi.group_addr = group_addr
        return cemi

    def write(self,group_addr,data,dtype='1'):
        """ send a write request to KNX group_addr"""
        cemi = self._new_cemi(group_addr)
        cemi.command = KNXCommand.WRITE
        cemi.data = dpts.encode[dtype](data)
        self.send(cemi)

    def read(self,group_add):
        """ send a read request to KNX group_addr"""
        frame = self._new_cemi(group_add)
        frame.command = KNXCommand.READ
        self.send(frame)

    def send(self,frame):
        frame.total_lenght = len(frame.pkt) # fix the lenght . 
        logger.debug("Sending: " + str(frame))
        #hex_dump(frame.pkt)
        self.nc.send(frame.pkt)

    def receive(self):
        buf = self.nc.receive()
        if buf:
            frame = KNXcEMI(buf)
            if frame.phy_addr != self.phy_addr:
                return frame
        return None


def test():
    c = KNXConnector()
    for i in range(1,5):
        #c.write('0/0/%s' % i,1)
        c.read('0/0/%s' % i)
        time.sleep(1)
    while 1:
        frame = c.receive()
        if frame:
            logger.debug("Receive: " + (str(frame)))

if __name__ == '__main__':
    test()
    


        
        
