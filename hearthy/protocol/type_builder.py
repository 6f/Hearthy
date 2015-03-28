from hearthy.protocol import mstruct

_enum = mstruct.MInteger(64, True)
_bool = mstruct.MInteger(64, True)

_int32 = mstruct.MInteger(32, True)
_uint32 = mstruct.MInteger(32, False)

_int64 = mstruct.MInteger(64, True)
_uint64 = mstruct.MInteger(64, False)

_fixed32 = mstruct.MBasicFixed(False, 32, False)
_fixed64 = mstruct.MBasicFixed(False, 64, False)
_float = mstruct.MBasicFixed(True, 32)

_basic_typehandler = {
    'enum': _enum,
    'int': _int32,
    'bool': _int32,
    'int32': _int32,
    'uint32': _uint32,
    'int64': _int64,
    'uint64': _uint64,
    'fixed32': _fixed32,
    'fixed64': _fixed64,
    'float': _float,
    'bytes': mstruct.MBytes,
    'string': mstruct.MString
}

def _build_docstring(name, fields):
    import pdb; pdb.set_trace()
    header = 'Automatically generated class "{0}"\n\nField Definitions:'.format(name)
    fields = '\n'.join('[{0:2}] {2:10} {1}'.format(*x) for x in fields)
    return header + '\n' + fields

class Builder:
    def __init__(self):
        self.types_to_build = []

    def add(self, name, fields):
        self.types_to_build.append((name, fields))

    def build(self, namespace, module):
        update = {}
        for name, fields in self.types_to_build:
            newtype = type(name,
                           (mstruct.MStruct,),
                           {'__slots__': [x[1] for x in fields],
                            '__module__': module,
                            '_mfields_': {}})
                           
            update[name] = newtype

        for name, fields in self.types_to_build:
            mfields = {}
            for field in fields:
                is_array = False
                tname = field[2]

                if isinstance(tname, list):
                    assert len(tname) == 1
                    is_array = True
                    typehandler = tname[0]
                elif isinstance(tname, str):
                    if tname.endswith('[]'):
                        is_array = True
                        tname = tname[:-2]

                    # find type handler
                    typehandler = _basic_typehandler.get(tname, None)
                    if typehandler is None:
                        typehandler = update.get(tname, None)
                        assert typehandler is not None, 'No typehandler for {0!r} found'.format(tname)
                else:
                    typehandler = tname

                mfields[field[0]] = (field[1], typehandler, is_array)

            update[name]._mfields_.update(mfields)

        namespace.update(update)
