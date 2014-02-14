from . import serialize
from hearthy.exceptions import DecodeError

class MStruct:
    _mfields_ = {}
    __slots__ = []

    @classmethod
    def decode_buf(cls, buf, offset=0, end=None):
        if end is None:
            end = len(buf)
        fields = serialize.read_fields(buf, offset, end)
        return cls.decode_fields(fields)

    @classmethod
    def decode_fields(cls, fields):
        a = cls()

        for k,v in cls._mfields_.items():
            if v[2]: setattr(a, v[0], [])

        for k,v in fields:
            our = cls._mfields_.get(k, None)
            if our is None:
                raise DecodeError('No field definition for slot {0}'.format(k))

            name, typehandler, is_array = our

            if isinstance(typehandler, str):
                if typehandler == 'string':
                    assert isinstance(v, bytes)
                    v = v.decode('UTF-8')
                elif typehandler == 'bytes':
                    assert isinstance(v, bytes)
                elif typehandler.startswith('int') or typehandler.startswith('uint'):
                    if isinstance(v, bytes):
                        # packet int detected
                        v = serialize.read_packed_varint(v)
                    else:
                        assert isinstance(v, int)
            else:
                v = typehandler.decode_buf(v)

            if is_array:
                if isinstance(v, list):
                    getattr(a, name).extend(v)
                else:
                    getattr(a, name).append(v)
            else:
                if hasattr(a, name):
                    raise DecodeError('Duplucated slot for non-array type')
                setattr(a, name, v)
        return a

    def __repr__(self):
        fields = ('{0}={1!r}'.format(name,getattr(self,name)) for name in self.__slots__ if hasattr(self, name))
        clsname = self.__class__.__name__
        return '{0}({1})'.format(clsname, ','.join(fields))
