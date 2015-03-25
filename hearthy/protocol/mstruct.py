import struct
from hearthy.protocol import serialize
from hearthy.exceptions import DecodeError

class MInteger:
    def __init__(self, nbits, signed):
        self._nbits = nbits
        self._signed = signed

    def encode_buf(self, val, buf, offset=0):
        return serialize.write_varint(val, buf, offset)

    def decode_buf(self, buf, offset=0, end=None):
        # Note: could check/clamp to _nbits here
        if end is None:
            return serialize.read_varint(buf, offset, signed=self._signed)
        else:
            return serialize.read_packed_varint(buf, offset, end, self._signed)

class MBasicFixed:
    def __init__(self, is_float, nbits, signed=True):
        if is_float:
            if nbits == 32:
                self._n_bytes = 4
                self._s = 'f'
            elif nbits == 64:
                self._n_bytes = 8
                self._s = 'd'
            else:
                assert False, 'Unsupported size'
        else:
            if nbits == 32:
                self._n_bytes = 4
                self._s = 'i' if signed else 'I'
            elif nbits == 64:
                self._n_bytes = 8
                self._s = 'q' if signed else 'Q'
            else:
                assert False, 'Unsupported size'

    def encode_field_val(self, val, field_number, buf, offset=0):
        buf[offset] = (serialize.WTYPE_FIXED32 if self._n_bytes == 4 else serialize.WTYPE_FIXED64) | field_number << 3
        struct.pack_into('<' + self._s, buf, offset + 1, val)
        return offset + self._n_bytes + 1

    def encode_field_arr(self, arr, field_number, buf, offset=0):
        buf[offset] = serialize.WTYPE_LEN_DELIM | field_number << 3
        size = len(arr) * self._n_bytes
        offset = serialize.write_varint(size, buf, offset + 1)
        struct.pack_into('<' + str(len(arr)) + self._s, buf, offset, *arr)
        return offset + size

    def decode_buf(self, buf, offset=0, end=None):
        if end is None:
            end = offset + self._n_bytes
            return (struct.unpack('<' + self._s, buf[offset:end])[0], end)
        else:
            length = end - offset
            if length % self._n_bytes != 0:
                raise DecodeError('Not a valid packed fixed field')
            n = length // self._n_bytes
            return list(struct.unpack('<' + str(n) + self._s, buf[offset:end]))

class MBytes:
    @classmethod
    def encode_buf(cls, val, buf, offset):
        end = offset + len(val)
        buf[offset:end] = val
        return end

    @classmethod
    def decode_buf(cls, buf, offset, end):
        return buf[offset:end]

class MString:
    @classmethod
    def encode_buf(cls, val, buf, offset):
        encoded = val.encode('UTF-8')
        end = offset + len(encoded)
        buf[offset:end] = encoded
        return end

    @classmethod
    def decode_buf(cls, buf, offset, end=None):
        if end is None:
            raise DecodeError('Strings need to be length delimited!')
        try:
            return buf[offset:end].decode('UTF-8')
        except UnicodeDecodeError as e:
            raise DecodeError(e.reason)

class MStruct:
    _mfields_ = {}
    __slots__ = []

    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)

    def encode_buf(self, buf, offset=0):
        for k, v in self._mfields_.items():
            name, typehandler, is_array = v
            if not hasattr(self, name):
                continue
            val = getattr(self, name)

            if is_array:
                if len(val) == 0:
                    # no need to encode empty arrays
                    continue

                if isinstance(typehandler, MInteger):
                    # use packed encoding
                    buf[offset] = serialize.WTYPE_LEN_DELIM | k << 3
                    offset = self._encode_buf_val_len_delim(val, serialize.write_packed_varint, buf, offset+1)
                elif isinstance(typehandler, MBasicFixed):
                    # use packed encoding
                    offset = typehandler.encode_field_arr(val, k, buf, offset)
                else:
                    # non-packed encoding
                    for item in val:
                        buf[offset] = serialize.WTYPE_LEN_DELIM  | k << 3
                        offset = self._encode_buf_val_len_delim(item, typehandler.encode_buf, buf, offset+1)
            else:
                if isinstance(typehandler, MInteger):
                    buf[offset] = serialize.WTYPE_VARINT | k << 3
                    offset = serialize.write_varint(val, buf, offset+1)
                elif isinstance(typehandler, MBasicFixed):
                    offset = typehandler.encode_field_val(val, k, buf, offset)
                else:
                    buf[offset] = serialize.WTYPE_LEN_DELIM | k << 3
                    offset = self._encode_buf_val_len_delim(val, typehandler.encode_buf, buf, offset+1)
        return offset

    def _encode_buf_val_len_delim(self, val, writer, buf, offset):
        start = offset + 10
        after = writer(val, buf, start)
        length = after - start
        offset = serialize.write_varint(length, buf, offset)
        buf[offset:offset+length] = buf[start:after]
        return offset + length

    @classmethod
    def decode_buf(cls, buf, offset=0, end=None):
        if end is None:
            end = len(buf)

        ret = cls()
        for k,v in cls._mfields_.items():
            if v[2]: setattr(ret, v[0], [])

        while offset < end:
            a = buf[offset]
            field_number = a >> 3
            wtype = a & 7

            our = cls._mfields_.get(field_number, None)
            if our is None:
                raise DecodeError('No field definition for type {0!r} slot {1} wire type {2}'.format(cls.__name__, field_number, wtype))
            name, typehandler, is_array = our

            if wtype == serialize.WTYPE_LEN_DELIM:
                length, offset = serialize.read_varint(buf, offset+1)
                val = typehandler.decode_buf(buf, offset, end=offset+length)
                offset += length
            elif wtype == serialize.WTYPE_VARINT:
                val, offset = typehandler.decode_buf(buf, offset+1)
            elif wtype == serialize.WTYPE_FIXED32:
                val, offset = typehandler.decode_buf(buf, offset+1)
            elif wtype == serialize.WTYPE_FIXED64:
                val, offset = typehandler.decode_buf(buf, offset+1)
            else:
                raise DecodeError('Unhandled wire type {0}'.format(wtype))

            if is_array:
                if isinstance(val, list):
                    getattr(ret, name).extend(val)
                else:
                    getattr(ret, name).append(val)
            else:
                if hasattr(ret, name):
                    raise DecodeError('Duplicated slot for non-array type')
                setattr(ret, name, val)
        return ret

    def __repr__(self):
        fields = ('{0}={1!r}'.format(name,getattr(self,name)) for name in self.__slots__ if hasattr(self, name))
        clsname = self.__class__.__name__
        return '{0}({1})'.format(clsname, ','.join(fields))
