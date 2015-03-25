"""
Implementation of blizzards SRP (Secure Remote Password) protocol
http://en.wikipedia.org/wiki/Secure_Remote_Password_protocol
"""

import random
from hashlib import sha256

SYSTEM_RANDOM = random.SystemRandom()

# A large (128 byte) safe prime (N = 2q+1 where q is prime)
N = 94558736629309251206436488916623864910444695865064772352148093707798675228170106115630190094901096401883540229236016599430725894430734991444298272129143681820273859470730877741629279425748927230996376833577406570089078823475120723855492588316592686203439138514838131581023312004481906611790561347740748686507

# A generator modulo N
g = 2

"""
Multiplier Parameter (SRP6-a)
Calculated as follows:

m = sha256()
m.update(N.to_bytes(128, 'little'))
m.update(g.to_bytes(1, 'little'))
d = m.digest()
k = int.from_bytes(d, 'little')
"""
k = 17879285710963087638853830310718479296574472666120682269760345478387347372653

def to_little_bytes(n):
    """
    Encodes a non-negative integer n with least significant byte first (little endian).
    """
    return n.to_bytes((n.bit_length() + 7) // 8, 'little')

def hash_number(n):
    """
    Hashes a binary representation of a non-negative number n.
    """
    return sha256(to_little_bytes(n)).digest()

def xor_bytes(a, b):
    """
    Returns bytestring b of length min(len(a), len(b))
    such that b[i] = a[i] XOR b[i].
    """
    return bytes(x ^ y for x,y in zip(a,b))

def sha256_derive_key(b):
    """
    Derives a 64 byte key from given buffer b.
    """
    K = bytearray(64)
    
    K[::2] = sha256(b[::2]).digest()
    K[1::2] = sha256(b[1::2]).digest()

    return K

def _xor_hash_two_numbers(a, b):
    return xor_bytes(hash_number(a), hash_number(b))

_H_N_xor_H_g = _xor_hash_two_numbers(N, g)

# TODO: XXX: second (thumbprint?) challenge/proof is not supported yet
SECOND_CHALLENGE = bytes([0x5B,0xE8,0xF1,0x95,0x54,0x3C,0x1E,0xD2,0xA2,0x2D,0x84,0x88,0xB0,0x60,0xA3,0x94,
                          0x23,0x68,0x65,0xD5,0x00,0xEC,0x62,0x92,0x95,0x82,0xEB,0xA6,0x31,0xEB,0xF5,0x0E,
                          0xFD,0x1E,0x14,0x8E,0x9C,0x55,0x9C,0x62,0x4B,0x31,0x72,0xE8,0x2E,0xD4,0xC2,0x5D,
                          0x0A,0x96,0xF1,0xA5,0xFD,0xE8,0x04,0xDA,0xBE,0x23,0x72,0x97,0x09,0xA6,0xB2,0x92,
                          0xD3,0x67,0xFF,0xD8,0x20,0xC5,0xCB,0xC8,0xF4,0x8D,0x16,0xD7,0xD0,0x12,0xF8,0x48,
                          0xD1,0x05,0xAE,0x03,0xBA,0x58,0x49,0x9C,0x8A,0xB7,0x56,0xAA,0xC8,0xFB,0x18,0x5E,
                          0x7E,0x4E,0x1B,0x2C,0xD0,0x4C,0xDA,0xA3,0xB7,0x52,0xDD,0x89,0x14,0xE2,0x1E,0x73,
                          0xA3,0x98,0x5D,0x5A,0x41,0xE8,0x01,0xDA,0x90,0xCD,0x61,0x9D,0x6E,0xDD,0x41,0x68])

SECOND_PROOF = b'e<\x0b\x16C\x15\x16jk\xb6\x1b\x17j\xd7\xd8th\nK\xe2uOv"\xd6\xbc\x19\x7f\xf1=\xc17x\xa6|\x8c\xf6\xa3&\xf1X\xb2x\xae\xcf\xdd\x01\xb9\x0b\xb0{\xd7!\xf6\xcf\x1c-kF 0*>\x02U\xdc\xe7\xd8\xc1\xc1!\xde\xd6\xe8\x8a\x9c\xcb\x157\xdb\xb7\xc6\xb6-\xa6\xd2\xab\xc4>/R\x8fT%\xcc\xc3\xbe\x10\xf2\xcc\x866\xf2{PI\x99\xf4\x8b\x8b\xc9\xd9\xc4f-\xcbBy\xc8\xd5\x18\x9cQB\xb4\x13\x85\x1a'

# TODO: don't use hardcoded private ephemeral key
# (this is only here for debugging)
EPH = bytes([0x05, 0x01, 0xc2, 0x65, 0xfd, 0x30, 0xa7, 0x89, 0xa3, 0x9d, 0x6d, 0x9c, 0x4d, 0x65, 0x8d, 0x99,
             0xe9, 0x5b, 0xc6, 0xac, 0x9f, 0x96, 0xdc, 0x6c, 0x88, 0x2d, 0xff, 0x83, 0xaf, 0x17, 0xa1, 0xba,
             0x19, 0x48, 0x18, 0x66, 0x30, 0xa5, 0x68, 0xd5, 0x6c, 0x2b, 0xa8, 0x12, 0x06, 0x77, 0x89, 0x2f,
             0xec, 0xb1, 0x9b, 0x19, 0x4b, 0x58, 0x92, 0x23, 0xd8, 0x4c, 0xe2, 0x51, 0x9c, 0x4b, 0x25, 0xca,
             0x3e, 0x6f, 0xde, 0xc4, 0x8d, 0x0b, 0x6c, 0xbe, 0x8a, 0xe4, 0x21, 0x81, 0x1c, 0xfe, 0x02, 0x14,
             0x68, 0xcd, 0x1c, 0xca, 0xfc, 0xdd, 0xe1, 0xc0, 0x7c, 0x0e, 0x42, 0x5b, 0x37, 0xac, 0x86, 0x53,
             0xe0, 0x82, 0xc1, 0x9e, 0x77, 0x08, 0x1b, 0x3d, 0xa1, 0x25, 0x69, 0x5f, 0xc7, 0xeb, 0x08, 0xed,
             0xa6, 0x39, 0x10, 0x51, 0x05, 0xd1, 0x94, 0x2c, 0x75, 0xaa, 0x0a, 0x12, 0x40, 0xd4, 0x45, 0x2a])

class SRP6a:
    def __init__(self, email, password, salt_unused):
        # TODO: XXX: don't use hardcoded salt
        salt = bytes([0x75,0x02,0x6F,0x7E,0x77,0x22,0xE1,0x6A,0xD2,0x85,0x53,0x31,0xDB,0xF0,0x53,0x05,0x1B,0xBD,0xF2,0x9B,0xE6,0x73,0xC7,0x4B,0xEA,0x28,0x98,0xAD,0xA2,0xC6,0xAF,0x3F])
        identity_hash = sha256(email.encode('ascii'))
        credentials = sha256((identity_hash.hexdigest().upper() + ':' + password.upper()).encode('ascii')).digest()
        salted = sha256(salt + credentials).digest()
        x = int.from_bytes(salted, 'little')

        # Compute password verifier
        v = pow(g, x, N)
        
        # TODO: don't use hardcoded private ephemeral key
        #b = SYSTEM_RANDOM.getrandbits(1024)
        b = int.from_bytes(EPH, 'little')
        B = (k * v + pow(g, b, N)) % N

        self.identity = identity_hash.digest()
        self.identity_hex = identity_hash.hexdigest().upper()
        self.salt = salt
        self.B_data = B.to_bytes(128, 'little')
        self.b = b
        self.v = v

    def set_client_ephemeral(self, A_data):
        assert(len(A_data) == 128)
        A = int.from_bytes(A_data, 'little')

        # scrambling paramater, u = H(A,B)
        u = int.from_bytes(sha256(A_data + self.B_data).digest(), 'little')

        # compute session key
        S = pow(A * pow(self.v, u, N), self.b, N)

        self.K = sha256_derive_key(S.to_bytes(128, 'little'))
        self.A_data = A_data

    def verify_client_proof(self, M):
        """
        Must be called after set_client_ephemeral
        """
        M_expected = sha256(_H_N_xor_H_g +
                            sha256(self.identity_hex.encode('ascii')).digest() +
                            self.salt +
                            self.A_data +
                            self.B_data +
                            self.K).digest()
        
        self._proof_server = sha256(self.A_data + M + self.K).digest()
        return M == M_expected

    def get_server_proof(self):
        return b'\x03' + self._proof_server + SECOND_PROOF

    def get_logon_challenge(self):
        return b'\x00' + self.identity + self.salt + self.B_data + SECOND_CHALLENGE

def password_verifier(email, password, salt):
    identity = sha256(email.encode('ascii')).hexdigest()
    credentials = sha256((identity.upper() + ':' + password.upper()).encode('ascii')).digest()
    salted = sha256(salt + credentials).digest()
    x = int.from_bytes(salted, 'little')
    return pow(g, x, N)

def pprint_logon_challenge(buf):
    assert(len(buf) == 321)
    # Command: 1 byte
    # Identity Salt (sha256, 32 byte)
    # Account Salt (32 byte binary)
    # Server public ephemeral value (128 byte)
    # second challenge (128 byte)
    # total: 321 byte-ish?
    return {'command': buf[0],
            'identity_salt': buf[1:33],
            'account_salt': buf[33:65],
            'server_public_ephemeral_value': buf[65:193],
            'second_challenge': buf[193:321]}

def pprint_logon_challenge_response(buf):
    # Command: 1 byte
    # Client ephemeral: 128 byte
    # Client's proof of session key: 32 byte
    # Client second challenge: 128 byte
    # Total: 289 byte
    raise NotImplementedError

