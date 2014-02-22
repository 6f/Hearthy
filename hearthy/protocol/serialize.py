"""
Reference:
https://developers.google.com/protocol-buffers/docs/encoding
"""

from hearthy.exceptions import DecodeError

WTYPE_VARINT = 0     # int32, int64, uint32, uint64, sint32, sint64, bool, enum
WTYPE_LEN_DELIM = 2  # string, bytes, embedded messages, packed repeated fields

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

def write_varint(val, buf, offset=0):
    r"""
    Writes val using varint encoding.

    Note: If val is negative it will be "cast" to an unsigned 64 bit integer,
    which takes up 10 bytes of the buffer.

    Note: The mapping from integer values to bytestrings is not unique,
    big unsigned integers can not be distinguished from signed integers.

    >>> buf = bytearray(10)
    >>> write_varint(-1, buf)
    10
    >>> read_varint(buf)
    (-1, 10)
    >>> write_varint(42, buf)
    1
    >>> read_varint(buf)
    (42, 1)
    """
    val = val & _MASK
    while True:
        byte = val & 0x7f
        val = val >> 7
        if val == 0:
            buf[offset] = byte
            return offset + 1

        buf[offset] = byte | 0x80
        offset += 1

def read_packed_varint(buf, offset=0, end=None, signed=True):
    if end is None:
        end = len(buf)

    ret = []
    while offset < end:
        var, offset = read_varint(buf, offset, signed)
        ret.append(var)

    if offset != end:
        raise DecodeError('Misaligned')

    return ret

def write_packed_varint(intarr, buf, offset=0):
    for val in intarr:
        offset = write_varint(val, buf, offset)
    return offset

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

def write_field(val, field_number, wire_type, buf, offset=0):
    buf[offset] = (field_number << 3) | wire_type

    if wire_type == 0: # varint
        return write_varint(val, buf, offset+1)
    elif wire_type == 2: # bytes
        offset = write_varint(len(val), buf, offset+1)
        end = offset + len(val)
        buf[offset:end] = val
        return end

    assert False, "Unhandled wire type"

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
