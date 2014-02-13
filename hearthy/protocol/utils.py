import sys
import struct

from .enums import *

# 16K ought to be enough for anybody :)
MAX_BUF = 16 * 1024

def hexdump(src, length=16, sep='.', file=sys.stdout):
    FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or sep for x in range(256)])
    lines = []
    for c in range(0, len(src), length):
        buf = src[c:c+length]
        shex = ' '.join('{0:02x}'.format(x) for x in buf)
        printable = ''.join("%s" % ((x <= 127 and FILTER[x]) or sep) for x in buf)
        lines.append('{0:08x}:  {2:{1}}  |{3}|'.format(c, length*3-1, shex, printable))
    print('\n'.join(lines), file=file)

def format_tag_value(tag, value):
    if tag == GameTag.ZONE:
        return '{0}:{1}'.format(value, Zone.reverse[value])
    elif tag == GameTag.CARDTYPE:
        return '{0}:{1}'.format(value, CardType.reverse[value])
    elif tag == GameTag.STEP or tag == GameTag.NEXT_STEP:
        return '{0}:{1}'.format(value, Step.reverse[value])
    elif tag == GameTag.RARITY:
        return '{0}:{1}'.format(value, CardRarity.reverse[value])
    elif tag == GameTag.PLAYSTATE:
        return '{0}:{1}'.format(value, PlayState.reverse[value])
    elif tag == GameTag.MULLIGAN_STATE:
        return '{0}:{1}'.format(value, MulliganState.reverse[value])
    else:
        return '{0}'.format(value)

class Splitter:
    def __init__(self, max_bufsize=MAX_BUF):
        self._buf = bytearray(max_bufsize)
        self._offset = 0
        self._needed = 8

        # Note atype == -1 <-> we are parsing the header
        self._atype = -1

    def feed(self, buf):
        newoffset = self._offset + len(buf)
        self._buf[self._offset:newoffset] = buf

        while newoffset >= self._needed:
            if self._atype == -1:
                atype, alen = struct.unpack('<II', self._buf[:8])
                self._needed = alen + 8
                self._atype = atype
            else:
                yield (self._atype, self._buf[8:self._needed])
                newoffset -= self._needed
                self._buf[:newoffset] = self._buf[self._needed:self._needed+newoffset]
                self._needed = 8
                self._atype = -1

        self._offset = newoffset

    def __repr__(self):
        return '<Splitter offset={0._offset} needed={0._needed}>'.format(self)
