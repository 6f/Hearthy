import asyncore
import socket
import struct

LISTEN_BACKLOG = 10
SO_ORIGINAL_DST = 80
DEFAULT_BUF_SIZE = 64 * 1024

class SimpleBuf:
    def __init__(self, buf_size=DEFAULT_BUF_SIZE):
        self._buf = bytearray(buf_size)
        self._max = buf_size
        self._start = 0
        self._end = 0

    def append(self, data):
        n = len(data)
        assert n <= self.free, 'Not enough buffer space'
        
        if n <= (self._max - self._end):
            end = self._end + n
            self._buf[self._end:end] = data
            self._end = end
        else:
            used = self._end - self._start
            self._buf[:used] = self._buf[self._start:self._end]
            self._start = 0
            end = used + n
            self._buf[used:end] = data
            self._start = 0
            self._end = end

    def clear(self):
        self._start = self._end = 0

    def last(self, n):
        """
        Returns the last n data that have been appended
        to the buffer.
        """
        assert n <= self.used, 'Requested read exceeds avaiable data'
        return bytes(self._buf[self._end-n:self._end])

    def peek(self, n, offset=0):
        """
        Returns the same as read(n) but without consuming
        the data.
        """
        assert n <= self.used, 'Requested read exceeds avaiable data'
        return bytes(self._buf[self._start+offset:self._start+offset+n])

    def read(self, n=None):
        if n is None:
            n = self.used
        end = self._start + n
        buf = bytes(self._buf[self._start:end])
        self._start += n
        return buf

    def consume(self, n):
        self._start += n

    @property
    def free(self):
        return self._max - self.used

    @property
    def used(self):
        return self._end - self._start

    def __repr__(self):
        return '<SimpleBuf free={0} used={1}>'.format(self.free, self.used)

class TcpEndpoint(asyncore.dispatcher):
    def __init__(self):
        self.cb = None
        self._is_writable = False
        self._is_readable = False
        self.closed = False

    @classmethod
    def from_connect(cls, addr):
        a = cls()
        a.connected = False
        asyncore.dispatcher.__init__(a)
        a.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        a.connect(addr)
        return a

    @classmethod
    def from_socket(cls, socket):
        """
        Construct endpoint from a connected socket.
        """
        a = cls()
        asyncore.dispatcher.__init__(a, socket)
        a.connected = True
        return a

    def handle_connect(self):
        print('Yay! Successful connection')
        self.connected = True

    def want_pull(self, value):
        self._is_readable = value

    def want_push(self, value):
        self._is_writable = value

    def handle_read(self):
        self.cb(self, 'may_pull', None)

    def handle_write(self):
        self.cb(self, 'may_push', None)

    def pull(self, buf):
        """
        Tries to receive data from the socket and put it into buf.
        Returns the number of bytes appended to the buffer.
        """
        tmpbuf = self.recv(buf.free)
        buf.append(tmpbuf)
        return len(tmpbuf)

    def push(self, buf):
        """
        Tries to send data from given buffer to the socket.
        """
        sent = self.send(buf._buf[buf._start:buf._end])
        buf.consume(sent)
        return sent

    def close(self, reason='???'):
        self.closed = True
        super().close()
        print('Closing due to: {0}'.format(reason))
        
        if self.cb is not None:
            self.cb(self, 'closed', None)

    def handle_close(self):
        self.close('handle_close called')

    def writable(self):
        return not self.connected or self._is_writable

    def readable(self):
        return not self.connected or self._is_readable

class TcpEndpointProvider(asyncore.dispatcher):
    """
    Listens on specified (host, port) pair, calls callback on each connection.
    """
    def __init__(self, listen):
        super().__init__()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(listen)
        self.listen(LISTEN_BACKLOG)
        print('Started, listening on {0}:{1}'.format(*listen))

        self.cb = None

    def handle_accepted(self, sock, addr):
        print('Received connection from {0!r}'.format(addr))
        buf = sock.getsockopt(socket.SOL_IP, SO_ORIGINAL_DST, 16)
        port, packed_ip = struct.unpack("!2xH4s8x", buf)
        ip = socket.inet_ntoa(packed_ip)
        print('Original Destination: {0}:{1}'.format(ip, port))

        if self.cb is None:
            print('No callback set - closing socket')
            sock.close('no handler')
        else:
            conn = TcpEndpoint.from_socket(sock)
            self.cb(self, 'accepted', ((ip, port), conn))

class SimplePipe:
    def __init__(self, a, b):
        self._ep = [a, b]
        self._bufs = [SimpleBuf(), SimpleBuf()]

        a.want_pull(True)
        b.want_pull(True)

        a.cb = self._on_endpoint_event
        b.cb = self._on_endpoint_event


    def _on_pull(self, epid, buf, n_bytes):
        """
        Called when n_bytes of data have been pulled from the endpoint
        specified by epid. The data is avaiable as the last n_bytes
        of buf.
        """
        # to be implemented by subclasses
        pass

    def _on_push(self, epid):
        """
        Called when some data has been pushed to an endpoint.
        """
        # to be implemented by subclasses
        pass

    def _on_endpoint_event(self, ep, ev_type, ev_data):
        # Careful here! This function has to be reentrant safe!
        # This is due to asyncore behaviour in wich pushes or pulls
        # can result in connection close.
        epid = self._ep.index(ep)
        opid = 1 - epid
        op = self._ep[opid]
                
        if ev_type == 'may_push':
            n = ep.push(self._bufs[epid])
            self._on_push(epid)
            ep.want_push(self._bufs[epid].used > 0)
            op.want_pull(not ep.closed and self._bufs[epid].free > 0)
        elif ev_type == 'may_pull':
            n = ep.pull(self._bufs[opid])
            self._on_pull(epid, self._bufs[opid], n)
            ep.want_pull(self._bufs[opid].free > 0)
            op.want_push(not ep.closed and self._bufs[opid].used > 0)
        elif ev_type == 'closed':
            # This should be called twice - exactly once for each endpoint.
            #
            # When we receive a close event we still try to send
            # any outstanding data to the other client.
            if not op.closed and self._bufs[opid].used == 0:
                # no outstanding data, may close other side
                print('no outstanding data')
                op.close('remote closed')

        if op.closed and not ep.closed and self._bufs[epid].used == 0:
            # No outstanding send data, close other connection!
            ep.close('remote closed')

    def __repr__(self):
        return '<Pipe eps={0!r} closed={1!r} bufs={2!r}>'.format(self._ep, self._closed, self._bufs)

if __name__ == '__main__':
    conns = []
    def cb(sender, ev_type, ev_data):
        if ev_type != 'accepted':
            return
        dst, conn = ev_data
        conns.append(conn)
        if len(conns) == 2:
            a = conns.pop()
            b = conns.pop()
            p = SimplePipe(a, b)

    provider = TcpEndpointProvider(('0.0.0.0', 5432))
    provider.cb = cb

    asyncore.loop()
