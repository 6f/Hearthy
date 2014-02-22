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

class MBytes:
    @classmethod
    def encode_buf(cls, val, buf, offset):
        end = offset = len(val)
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
    def decode_buf(cls, buf, offset, end):
        try:
            return buf[offset:end].decode('UTF-8')
        except UnicodeDecodeError as e:
            raise DecodeError(e.reason)

class MStruct:
    _mfields_ = {}
    __slots__ = []

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
                else:
                    for item in val:
                        buf[offset] = serialize.WTYPE_LEN_DELIM  | k << 3
                        offset = self._encode_buf_val_len_delim(item, typehandler.encode_buf, buf, offset+1)
            else:
                if isinstance(typehandler, MInteger):
                    buf[offset] = serialize.WTYPE_VARINT | k << 3
                    offset = serialize.write_varint(val, buf, offset+1)
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
                raise DecodeError('No field definition for slot {0}'.format(field_number))
            name, typehandler, is_array = our

            if wtype == serialize.WTYPE_LEN_DELIM:
                length, offset = serialize.read_varint(buf, offset + 1)
                val = typehandler.decode_buf(buf, offset, end=offset+length)
                offset += length
            else:
                val, offset = typehandler.decode_buf(buf, offset+1)

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
