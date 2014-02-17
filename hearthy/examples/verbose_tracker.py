from hearthy import exceptions
from hearthy.tracker import processor
from hearthy.protocol.decoder import decode_packet
from hearthy.protocol.utils import Splitter

class Connection:
    def __init__(self, source, dest):
        self.p = [source, dest]
        self._s = [Splitter(), Splitter()]
        self._t = processor.Processor()

    def feed(self, who, buf):
        for atype, abuf in self._s[who].feed(buf):
            decoded = decode_packet(atype, abuf)
            self._t.process(who, decoded)

    def __repr__(self):
        print('<Connection source={0!r} dest={1!r}'.format(
            self.p[0], self.p[1]))

if __name__ == '__main__':
    import sys
    from hearthy.datasource import hcapng

    if len(sys.argv) < 2:
        print('Usage: {0} <hcapng file>'.format(sys.argv[0]))
        sys.exit(1)

    d = {}
    with open(sys.argv[1], 'rb') as f:
        parser = hcapng.parse(f)
        begin = next(parser)
        for ts, event in parser:
            if isinstance(event, hcapng.EvClose):
                if event.stream_id in d:
                    del d[event.stream_id]
            elif isinstance(event, hcapng.EvData):
                if event.stream_id in d:
                    try:
                        d[event.stream_id].feed(event.who, event.data)
                    except exceptions.BufferFullException:
                        del d[event.stream_id]
            elif isinstance(event, hcapng.EvNewConnection):
                d[event.stream_id] = Connection(event.source, event.dest)
