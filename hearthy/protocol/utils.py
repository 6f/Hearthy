import sys
import struct

from hearthy import exceptions
from hearthy.protocol.enums import *

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

_gametag_to_enum = {
    GameTag.ZONE: Zone,
    GameTag.CARDTYPE: CardType,
    GameTag.STEP: Step,
    GameTag.NEXT_STEP: Step,
    GameTag.RARITY: CardRarity,
    GameTag.PLAYSTATE: PlayState,
    GameTag.MULLIGAN_STATE: MulliganState,
    GameTag.STATE: TagState,
    GameTag.FACTION: Faction,
    GameTag.CARDRACE: Race
}
def format_tag_value(tag, value):
    enum = _gametag_to_enum.get(tag, None)
    if enum:
        return '{0}:{1}'.format(value, enum.reverse[value])
    else:
        return str(value)

class Splitter:
    def __init__(self, max_bufsize=MAX_BUF):
        self._buf = bytearray(max_bufsize)
        self._offset = 0
        self._needed = 8

        # Note atype == -1 <-> we are parsing the header
        self._atype = -1

    def feed(self, buf):
        newoffset = self._offset + len(buf)
        if newoffset > MAX_BUF:
            raise exceptions.BufferFullException()
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
