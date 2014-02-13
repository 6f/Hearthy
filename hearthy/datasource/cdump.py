import re
from ..protocol.decoder import decode_packet
from ..protocol.utils import hexdump, Splitter
from ..protocol.enums import PacketType

READ_BUFSIZE = 16 * 1024

def tokenizer(f):
    leftover = ''
    while True:
        buf = f.read(READ_BUFSIZE)
        if not buf:
            break

        fields = re.split('[\n\r, ]', leftover + buf)
        for field in filter(None, fields[:-1]):
            yield field
        leftover = fields[-1]

    if leftover:
        yield leftover

def parse_cdump(f):
    t = tokenizer(f)

    header = next(t, None)
    ret = []

    while header != None:
        assert(header == 'char')

        # peerN_N[] where N is some decimal?
        peer = next(t, None)
        assert(peer.startswith('peer'))
        assert(peer.endswith('[]'))
        p,n = map(int, peer[4:-2].split('_'))

        assert(next(t) == '=')
        assert(next(t) == '{')

        l = []
        while True:
            a = next(t)
            if a == '};':
                break
            l.append(int(a.rstrip(','), 16))

        yield (p, n, bytes(l))
        header = next(t, None)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: {0} <file>'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        s = Splitter()
        for p, n, buf in parse_cdump(f):
            print('== Client -> Server ==' if p == 0 else '== Server -> Client==')
            print('Sequence: {0}'.format(n))
            hexdump(buf)
            for atype, buf in s.feed(buf):
                print('\nFound packet {0}:{1}'.format(
                    atype, PacketType.reverse.get(atype, '???')))
                print('\nDecoded packet:')
                print(decode_packet(atype, buf))
                print()
