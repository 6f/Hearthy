import struct
import socket

from ..protocol.decoder import decode_packet
from ..protocol.utils import Splitter, hexdump

EV_NEW_CONNECTION, EV_CLOSE, EV_DATA = range(3)

def format_ip(ip):
    return '{0}.{1}.{2}.{3}'.format(ip & 0xff,
                                    (ip >> 8) & 0xff,
                                    (ip >> 16) & 0xff,
                                    (ip >> 24) & 0xff)

class EvNewConnection:
    __slots__ = ['stream_id', 'source', 'dest']

    @classmethod
    def decode(cls, buf):
        a = cls()
        args = struct.unpack('<IIHIH', buf)
        a.stream_id = args[0]
        a.source = (format_ip(args[1]), args[2])
        a.dest = (format_ip(args[3]), args[4])
        return a

    def __repr__(self):
        return '<EvNewConnection stream_id={0}, source={1!r} dest={2!r}'.format(
            self.stream_id, self.source, self.dest)

class EvData:
    __slots__ = ['stream_id', 'data', 'who']

    @classmethod
    def decode(cls, buf):
        a = cls()
        a.stream_id, a.who = struct.unpack('<IB', buf[:5])
        a.data = buf[5:]
        return a

    def __repr__(self):
        return '<EvData stream_id={0} who={1} data=<{2} bytes> >'.format(
            self.stream_id, self.who, len(self.data))

class EvClose:
    __slots__ = ['stream_id']

    @classmethod
    def decode(cls, buf):
        a = cls()
        a.stream_id = struct.unpack('<I', buf)[0]
        return a

def decode_splitter_segment(atype, buf):
    if atype == EV_NEW_CONNECTION:
        return EvNewConnection.decode(buf)
    elif atype == EV_DATA:
        return EvData.decode(buf)
    elif atype == EV_CLOSE:
        return EvClose.decode(buf)

def read_splitter_file(f):
    buf = b''
    atype = -1
    needed = 5

    while True:
        newbuf = f.read(1024)

        if len(newbuf) == 0:
            return

        buf = buf + newbuf

        while len(buf) >= needed:
            if atype == -1:
                needed, atype = struct.unpack('<IB', buf[:5])
            else:
                yield decode_splitter_segment(atype, buf[5:needed])
                buf = buf[needed:]
                needed = 5
                atype = -1

class Connection:
    def __init__(self, source, dest):
        self.p = [source, dest]
        self._s = [Splitter(), Splitter()]

    def discard(self):
        pass

    def feed(self, who, buf):
        print('{0} -> {1}'.format(self.p[who], self.p[1-who]))
        for atype, abuf in self._s[who].feed(buf):
            hexdump(abuf)
            print(decode_packet(atype, abuf))

    def __repr__(self):
        print('<Connection source={0!r} dest={1!r}'.format(
            self.p[0], self.p[1]))

if __name__ == '__main__':
    import sys
    d = {}
    with open(sys.argv[1], 'rb') as f:
        for foo in read_splitter_file(f):
            if isinstance(foo, EvClose):
                conn = d[foo.stream_id]
                conn.discard()
                del d[foo.stream_id]
            elif isinstance(foo, EvData):
                conn = d[foo.stream_id]
                conn.feed(foo.who, foo.data)
            elif isinstance(foo, EvNewConnection):
                d[foo.stream_id] = Connection(foo.source, foo.dest)
