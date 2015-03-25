import struct
from hearthy.proxy.pipe import SimpleBuf, SimplePipe
from hearthy.protocol import decoder, mtypes

MODE_INTERCEPT, MODE_PASSIVE, MODE_LURKING = range(3)
INTERCEPT_REJECT, INTERCEPT_ACCEPT = range(2)

class SplitterBuf(SimpleBuf):
    """
    In principle same functionality as hearthy.protocol.utils.Splitter.
    This version has the benefit of correctly handling loop breaks.
    """
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

class InterceptPipe(SimplePipe):
    def __init__(self, a, b, handler):
        super().__init__(a, b)
        self._splitters = [SplitterBuf(), SplitterBuf()]
        self._mode = MODE_LURKING
        self._encode_buf = bytearray(16 * 1024)
        self._handler = handler

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
            decoded = decoder.decode_packet(*segment)
            print('Decoded first packet, is of type {0!r}'.format(decoded.__class__))
            
            if isinstance(decoded, mtypes.AuroraHandshake):
                print('Is an aurora handshake - going into full intercept mode.')
                self._mode = MODE_INTERCEPT
                self._handler.on_start_intercept(decoded)
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
        handler = self._handler

        # steal data
        if n_bytes > 0:
            splitter.append(buf.last(n_bytes))
            buf._end -= n_bytes

        # decode and forward data
        while True:
            segment = splitter.pull_segment()
            if segment is None:
                break

            decoded = decoder.decode_packet(*segment)
            action = handler.on_packet(epid, decoded)

            if action == INTERCEPT_REJECT:
                # nothing to do in this case
                pass
            elif action == INTERCEPT_ACCEPT:
                offset = decoder.encode_packet(decoded, self._encode_buf)

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

class InterceptProxyHandler:
    def __init__(self, intercept_handler, *args, **kwargs):
        self._handler_factory = intercept_handler
        self._args = args
        self._kwargs = kwargs

    def connect(self, ep0, ep1):
        handler = self._handler_factory(*self._args, **self._kwargs)
        InterceptPipe(ep0, ep1, handler=handler)

class InterceptHandler:
    def __init__(self):
        self._interceptor = None

    @property
    def interceptor(self):
        return self._interceptor

    @interceptor.setter
    def interceptor(self, value):
        self._interceptor = value

    def on_packet(self, epid, packet):
        return INTERCEPT_ACCEPT

    def on_start_intercept(self, first):
        pass
