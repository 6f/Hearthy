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
    yield (0, EvHeader(timestamp))

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

HEADER_SIZE = len(EXPECTED_VERSION) + 8
MAX_BUF = 64 * 1024
class AsyncParser:
    """
    Parser than can be used for asynchronous parsing
    (i.e. using asyncore or similar)
    """
    def __init__(self, max_buf=MAX_BUF):
        self._buf = bytearray(max_buf)
        self._buf_start = 0
        self._buf_end = 0
        self._max_buf = max_buf

        self._needed = HEADER_SIZE
        self._parser = self._read_header

    def _read(self, n):
        end = self._buf_start + n
        buf = self._buf[self._buf_start:end]
        self._buf_start = end
        return buf

    def _read_event(self):
        buf = self._read(self._evlen - PREFIX_LEN)
        evtype = self._evtype
        evtime = self._evtime
        
        # read header
        self._needed = PREFIX_LEN
        self._parser = self._read_prefix

        if evtype == EV_NEW_CONNECTION:
            return (evtime, EvNewConnection.decode(buf))
        elif evtype == EV_DATA:
            return (evtime, EvData.decode(buf))
        elif evtype == EV_CLOSE:
            return (evtime, EvClose.decode(buf))
        else:
            raise HCapException('Got unknown event type 0x{0:02x}'.format(evtype))

    def _read_prefix(self):
        self._evlen, self._evtime, self._evtype = struct.unpack('<IqB', self._read(PREFIX_LEN))

        # read event
        self._needed = self._evlen - PREFIX_LEN
        self._parser = self._read_event

    def _read_header(self):
        version = self._read(len(EXPECTED_VERSION))
        if version != EXPECTED_VERSION:
            raise HCapException('Expected to read {0!r} but got {1!r}'.format(
                EXPECTED_VERSION, version))
        
        timestamp = struct.unpack('<q', self._read(8))[0]

        self._needed = PREFIX_LEN
        self._parser = self._read_prefix

        return (0, EvHeader(timestamp))
        
    def feed_buf(self, buf):
        end = self._buf_end + len(buf)
        if end > self._max_buf:
            raise HCapException('Buffer size exceeded')

        # copy new data into buf
        self._buf[self._buf_end:end] = buf
        self._buf_end = end

        # process data
        while end - self._buf_start >= self._needed:
            data = self._parser()
            if data is not None:
                yield data

        # copy to make more room
        if end > self._max_buf // 4:
            inbuff = end - self._buf_start
            self._buf[:inbuff] = self._buf[self._buf_start:end]
            self._buf_start = 0
            self._buf_end = inbuff

if __name__ == '__main__':
    import sys
    from datetime import datetime
    if len(sys.argv) < 2:
        print('Usage: {0} <file>'.format(sys.argv[0]))
        sys.exit(1)

    with open(sys.argv[1], 'rb') as f:
        gen = parse(f)

        _, header = next(gen)
        print('[{0:8}] Recording started at {1}'.format(0,
            datetime.fromtimestamp(header.ts).strftime('%Y.%m.%d %H:%M:%S')))

        for ts, event in gen:
            print('[{0:8}] {1!r}'.format(ts, event))
