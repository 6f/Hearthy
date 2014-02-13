"""
Reference:
https://developers.google.com/protocol-buffers/docs/encoding
"""

from .exceptions import DecodeError

_MASK = (1 << 64) - 1
def read_varint(buf, offset=0, signed=True):
    r"""Reads a varint from buf at offset.

    >>> read_varint(b'\x2a')
    (42, 1)
    >>> read_varint(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01')
    (-1, 10)
    """
    result = 0
    shift_amount = 0
    while True:
        byte = buf[offset]
        offset += 1
        result |= ((byte & 0x7f) << shift_amount)
        if not (byte & 0x80):
            if signed and result >> 63:
                # reinterpret integer as signed
                result &= _MASK
                result = ~(result ^ _MASK)
            else:
                result &= _MASK
            return (result, offset)

        shift_amount += 7
        if shift_amount >= 64:
            raise DecodeError('Not a valid varint')

def read_packed_varint(buf, offset=0, end=None):
    if end is None:
        end = len(buf)

    ret = []
    while offset < end:
        var, offset = read_varint(buf, offset)
        ret.append(var)

    if offset != end:
        raise DecodeError('Misaligned')

    return ret

def read_field(buf, offset):
    a = buf[offset]
    field_number = a >> 3
    wire_type = a & 7

    if wire_type == 0: # varint
        val, offset = read_varint(buf, offset+1)
        return ((field_number, val), offset)
    elif wire_type == 2: # bytes
        val, after = read_varint(buf, offset+1)
        return ((field_number, bytes(buf[after:after+val])), after+val)
    else:
        raise DecodeError('Unimplemented or wrong wire type {0}'.format(wire_type))

def read_fields(buf, offset=0, end=None):
    if end is None:
        end = len(buf)

    fields = []
    while offset < end:
        field, offset = read_field(buf, offset)
        fields.append(field)

    if offset != end:
        raise DecodeError('misaligned')

    return fields

if __name__ == '__main__':
    import doctest
    doctest.testmod()
