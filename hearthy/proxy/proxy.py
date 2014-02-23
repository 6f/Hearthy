"""
Basic tcp proxy server using asyncore.
Relies on SO_ORIGINAL_DST which only works on linux/ipv4.
"""
from hearthy.proxy import pipe

class BasicProxyHandler:
    @classmethod
    def connect(self, ep0, ep1):
        pipe.SimplePipe(ep0, ep1)

class Proxy:
    def __init__(self, listen, handler):
        provider = pipe.TcpEndpointProvider(listen)
        provider.cb = self._on_connection
        self._handler = handler

    def _on_connection(self, provider, ev_type, ev_data):
        """ Called when a connection to the proxy has been established. """
        addr_orig, ep = ev_data

        remote = pipe.TcpEndpoint.from_connect(addr_orig)
        self._handler.connect(ep, remote)

if __name__ == '__main__':
    import asyncore
    p = Proxy(('0.0.0.0', 5412), handler=BasicProxyHandler)
    asyncore.loop()
