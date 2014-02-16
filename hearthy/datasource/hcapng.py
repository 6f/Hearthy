import struct

def _format_ipv4(ip):
    """
    Converts an ip in numeric form to its dotted form.
    Assumes ip is given in native byte order.
    """
    return '{3}.{2}.{1}.{0}'.format( ip        & 0xff,
                                    (ip >>  8) & 0xff,
                                    (ip >> 16) & 0xff,
                                    (ip >> 24) & 0xff)

EV_NEW_CONNECTION, EV_CLOSE, EV_DATA = range(3)

class HCapException(Exception):
    """ Base class for all exceptions thrown by hcapng.py """
    pass

class EvNewConnection:
    __slots__ = ['stream_id', 'source', 'dest']

    @classmethod
    def decode(cls, buf):
        a = cls()
        a.stream_id, saddr, source, daddr, dest = struct.unpack('<IIHIH', buf)
        a.source = (_format_ipv4(saddr), source)
        a.dest = (_format_ipv4(daddr), dest)
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
        return '<EvData stream_id={0} who={1} data=<{2} bytes>>'.format(
            self.stream_id, self.who, len(self.data))

class EvClose:
    __slots__ = ['stream_id']

    @classmethod
    def decode(cls, buf):
        a = cls()
        a.stream_id = struct.unpack('<I', buf)[0]
        return a

    def __repr__(self):
        return '<EvClose stream_id={0}>'.format(
            self.stream_id)

class EvHeader:
    def __init__(self, ts):
        self.ts = ts

    def __repr__(self):
        return '<EvHeader ts={0}>'.format(self.ts)

EXPECTED_VERSION = b'HCaptureV0\x00'
def read_header(stream):
    version = stream.read(len(EXPECTED_VERSION))
    if version != EXPECTED_VERSION:
        raise HCapException('Expected to read {0!r} but got {1!r}'.format(
            EXPECTED_VERSION, version))
    buf = stream.read(8)
    timestamp = struct.unpack('<q', buf)[0]
    return timestamp

MAX_EVLEN = 16*1024
PREFIX_LEN = 13
def parse(stream):
    timestamp = read_header(stream)
    yield EvHeader(timestamp)

    while True:
        prefix_buf = stream.read(PREFIX_LEN)
        if len(prefix_buf) == 0:
            break
        elif len(prefix_buf) < PREFIX_LEN:
            raise HCapException('Unexpected EOF!')

        evlen, evtime, evtype = struct.unpack('<IqB', prefix_buf)

        # Sanity check, we don't want unbounded buffer sizes
        if evlen > MAX_EVLEN:
            raise HCapException('Event length {0} exceeds maximum of {1}'.format(
                evlen, MAX_EVLEN))

        # read event data
        buf = stream.read(evlen - PREFIX_LEN)

        if evtype == EV_NEW_CONNECTION:
            yield (evtime, EvNewConnection.decode(buf))
        elif evtype == EV_DATA:
            yield (evtime, EvData.decode(buf))
        elif evtype == EV_CLOSE:
            yield (evtime, EvClose.decode(buf))
        else:
            raise HCapException('Got unknown event type 0x{0:02x}'.format(evtype))

if __name__ == '__main__':
    import sys
    from datetime import datetime
    if len(sys.argv) < 2:
        print('Usage: {0} <file>'.format(sys.argv[0]))
        sys.exit(1)

    with open(sys.argv[1], 'rb') as f:
        gen = parse(f)

        header = next(gen)
        print('Recording started at {0}'.format(
            datetime.fromtimestamp(header.ts).strftime('%Y.%m.%d %H:%M:%S')))

        for ts, event in gen:
            print('[{0}] {1!r}'.format(ts, event))
