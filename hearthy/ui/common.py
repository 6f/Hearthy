import threading
import queue

from hearthy.datasource import hcapng
from hearthy.protocol.utils import Splitter
from hearthy.protocol.decoder import decode_packet

MAX_QUEUE = 1000

class Connection:
    __slots__ = ['p', '_s']
    """
    Represent a connection between two endpoints source and dest.
    Decodes packet in the connection
    """
    def __init__(self, source, dest):
        self.p = [source, dest]
        self._s = [Splitter(), Splitter()]

    def feed(self, who, buf):
        for atype, abuf in self._s[who].feed(buf):
            decoded = decode_packet(atype, abuf)
            yield decoded

    def __repr__(self):
        print('<Connection source={0!r} dest={1!r}'.format(
            self.p[0], self.p[1]))

class AsyncLogGenerator:
    def __init__(self):
        self._conns = {}

    def process_event(self, ts, event):
        conns = self._conns

        if isinstance(event, hcapng.EvHeader):
            yield (-1, ('basets', event.ts))
        elif isinstance(event, hcapng.EvNewConnection):
            conns[event.stream_id] = Connection(event.source, event.dest)
            yield (event.stream_id, ('create', event.source, event.dest, ts))
        elif event.stream_id in conns:
            if isinstance(event, hcapng.EvClose):
                yield (event.stream_id, ('close', ts))
                del conns[event.stream_id]
            elif isinstance(event, hcapng.EvData):
                try:
                    for packet in conns[event.stream_id].feed(event.who, event.data):
                        yield (event.stream_id, ('packet', packet, event.who, ts))
                except Exception as e:
                    del conns[event.stream_id]
                    yield (event.stream_id, ('exception', e))
        
def hcap_generate_logs(f):
    generator = hcapng.parse(f)
    _, header = next(generator)

    conns = {}

    yield (-1, ('basets', header.ts))

    for ts, event in generator:
        if isinstance(event, hcapng.EvNewConnection):
            conns[event.stream_id] = Connection(event.source, event.dest)
            yield (event.stream_id, ('create', event.source, event.dest, ts))
        elif event.stream_id in conns:
            if isinstance(event, hcapng.EvClose):
                yield (event.stream_id, ('close', ts))
                del conns[event.stream_id]
            elif isinstance(event, hcapng.EvData):
                try:
                    for packet in conns[event.stream_id].feed(event.who, event.data):
                        yield (event.stream_id, ('packet', packet, event.who, ts))
                except Exception as e:
                    del conns[event.stream_id]
                    yield (event.stream_id, ('exception', e))

class LogGenerationThread(threading.Thread):
    def __init__(self, fn):
        super().__init__()
        self._fn = fn
        self.queue = queue.Queue(MAX_QUEUE)

    def run(self):
        with open(self._fn, 'rb') as f:
            for event in hcap_generate_logs(f):
                self.queue.put(event, block=True)
