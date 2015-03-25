_FNV_OFFSET_BASIS = 2166136261
_FNV_PRIME = 16777619
def hash(s):
    """
    Hashes bytes in s using 32 bit FNV hash.
    
    Refernce: http://en.wikipedia.org/wiki/Fowler_Noll_Vo_hash
    """
    h = _FNV_OFFSET_BASIS
    for b in s:
        h ^= b
        h = (h * _FNV_PRIME) & 0xFFFFFFFF

    return h

def encode_fourcc(s):
    return int.from_bytes(s.encode('ascii'), 'big')

def decode_fourcc(v):
    return (chr(v >> 24 & 0xff) +
            chr(v >> 16 & 0xff) +
            chr(v >>  8 & 0xff) +
            chr(v       & 0xff)).lstrip('\x00')
