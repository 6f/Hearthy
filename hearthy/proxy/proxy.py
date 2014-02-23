"""
Basic tcp proxy server using asyncore.
Relies on SO_ORIGINAL_DST which only works on linux/ipv4.
"""
import asyncore

import struct
from hearthy.proxy.pipe import SimpleBuf, SimplePipe, TcpEndpointProvider, TcpEndpoint
from hearthy.protocol import mtypes
from hearthy.protocol.utils import Splitter
from hearthy.protocol.decoder import decode_packet, encode_packet

class SplitterBuf(SimpleBuf):
    """
    In principle same functionality as hearthy.protocol.utils.Splitter.
    This version has the benefit of correctly handling loop breaks.
    """
    def __init__(self):
        super().__init__()

    def pull_segment(self):
        segment = self.peek_segment()
        if segment is not None:
            self._start += 8 + len(segment[1])
        return segment

    def peek_segment(self):
        used = self.used
        if used < 8:
            return
        
        atype, alen = struct.unpack('<II', self.peek(8))

        if used < alen + 8:
            return

        return (atype, self.peek(alen, offset=8))

MODE_INTERCEPT, MODE_PASSIVE, MODE_LURKING = range(3)
class InterceptingPipe(SimplePipe):
    def __init__(self, a, b):
        super().__init__(a, b)
        self._splitters = [SplitterBuf(), SplitterBuf()]
        self._queued_packet = [None, None]
        self._mode = MODE_LURKING
        self._encode_buf = bytearray(16 * 1024)

    def _on_pull_lurking(self, epid, buf, n_bytes):
        opid = 1 - epid
        splitter = self._splitters[epid]

        if splitter.free < n_bytes:
            print('WARNING: not enough buffer space, going into passive mode')
            self._mode = MODE_PASSIVE
            return

        # Check if we have a full segment
        splitter.append(buf.last(n_bytes))
        segment = splitter.pull_segment()
        if segment is None:
            return

        # Calculate how much of the n_bytes don't belong to the first segment
        remaining = splitter.used
        assert remaining < n_bytes, "We missed the pull that completed the first segment!"

        # Clear splitter
        splitter.clear()

        try:
            decoded = decode_packet(*segment)
            print('Decoded first packet, is of type {0!r}'.format(decoded.__class__))
            
            if isinstance(decoded, mtypes.AuroraHandshake):
                print('Is an aurora handshake - going into full intercept mode.')
                self._mode = MODE_INTERCEPT
                self._on_pull_intercept(epid, buf, remaining)
            else:
                print('WARNING: first packet was not aurora handshake - going into passive mode')
                self._mode = MODE_PASSIVE
        except Exception as e:
            print('WARNING: Got exception {0!r} while trying to decode packet'.format(e))
            self._mode = MODE_PASSIVE

    def _on_pull_intercept(self, epid, buf, n_bytes):
        opid = 1 - epid
        splitter = self._splitters[epid]

        # steal data
        if n_bytes > 0:
            splitter.append(buf.last(n_bytes))
            buf._end -= n_bytes

        # decode and forward data
        while True:
            segment = splitter.pull_segment()
            if segment is None:
                break

            decoded = decode_packet(*segment)

#            if isinstance(decoded, mtypes.AllOptions):
#                print('Found AllOptions packet')
#                if len(decoded.Options) == 1 and decoded.Options[0].Type == 2:
#                    print('Only Option is End-Of-Turn!')
#                    
#                    # only play option is end turn
#                    choose = mtypes.ChooseOption(Id=decoded.Id, Index=0, Target=0, SubOption=-1, Position=0)
#                    offset = encode_packet(choose, self._encode_buf)
#
#                    # send option response to the endpoint
#                    self._bufs[epid].append(self._encode_buf[:offset])

            # default action: forward identically
            offset = encode_packet(decoded, self._encode_buf)

            # forward packet (hopefully everything fits into the buffer)
            buf.append(self._encode_buf[:offset])
        
    def _on_pull(self, epid, buf, n_bytes):
        if n_bytes == 0:
            return
        if self._mode == MODE_INTERCEPT:
            return self._on_pull_intercept(epid, buf, n_bytes)
        elif self._mode == MODE_LURKING:
            return self._on_pull_lurking(epid, buf, n_bytes)
        # otherwise we are in passive mode and do nothing

class Proxy:
    def __init__(self, listen):
        provider = TcpEndpointProvider(listen)
        provider.cb = self._on_connection

    def _on_connection(self, provider, ev_type, ev_data):
        """ Called when a connection to the proxy has been established. """
        addr_orig, ep = ev_data

        remote = TcpEndpoint.from_connect(addr_orig)
        pipe = InterceptingPipe(ep, remote)

if __name__ == '__main__':
    p = Proxy(('0.0.0.0', 5412))
    asyncore.loop()
