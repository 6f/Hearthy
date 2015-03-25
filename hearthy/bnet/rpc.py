import logging
import re
import types

from hearthy.bnet import utils
from hearthy.protocol import mtypes

class ServiceMethod:
    __slots__ = ['id', 'name', 'req', 'resp']
    def __init__(self, *args):
        for k,v in zip(self.__slots__, args):
            setattr(self, k, v)

class ServiceServer:
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ':' + self.__class__.__name__)
        self.broker = None
        
    def _handle_packet(self, header, body):
        method_id = header.MethodId
        method = self.service.get_method_by_id(method_id)
        self.logger.info('Request for %s', method.name)
        request = method.req.decode_buf(body)
        self.logger.debug('Decoded request %r', request)

        # dispatch
        handler = getattr(self, method.name, None)
        if handler is None:
            self.logger.info('No handler found, ignoring request')
            if method.resp is not None:
                self.broker.send_response(header, method.resp())
            return

        result = handler(request)
        if isinstance(result, types.GeneratorType):
            for response in result:
                self.broker.send_response(header, response)
        elif method.resp is not None:
            self.broker.send_response(header, result)

class ClientProxyMethod:
    def __init__(self, client_proxy, service_method):
        self._client_proxy = client_proxy
        self.id = service_method.id
        self.req_type = service_method.req

    def __call__(self, _full=None, **kwargs):
        header = mtypes.BnetPacketHeader(
            ServiceId=self._client_proxy.id,
            MethodId=self.id)

        if _full is not None:
            body = _full
        else:
            body = self.req_type(**kwargs)

        self._client_proxy.broker.send_request(header, body)

class ClientProxy:
    __slots__ = ['id', 'broker', 'service']
    def __init__(self, service):
        self.service = service
        self.id = None
        self.broker = None
        
    def __getattr__(self, name):
        return ClientProxyMethod(self, self.service._method_by_name[name])

    def __repr__(self):
        if self.id is None:
            return '<Unbound ClientProxy for {0}>'.format(self.service.name)
        else:
            return '<Bound ClientProxy for {0} with id {1}>'.format(self.service.name, self.id)

def _client_proxy_method(method):
    def inner(self, req):
        self.broker
    return inner

class Service:
    def __init__(self, name):
        self.name = name
        self.hval = utils.hash(name.encode('ascii'))
        self._id_to_method = {}
        self._method_by_name = {}

    def get_method_by_id(self, method_id):
        return self._id_to_method[method_id]
        
    def add_method(self, service_method):
        self._id_to_method[service_method.id] = service_method
        self._method_by_name[service_method.name] = service_method

    def _build_server(self):
        d = {'service':self}
        t = type(self.name.split('.')[-1], (ServiceServer,), d)
        self.Server = t

    def build_client_proxy(self):
        c = ClientProxy(self)
        return c
        
    def _build_client_proxy(self):
        self.Client = None

_hash_to_service = {}
def defservice(name, methods):
    service = Service(name)
    
    for m_name, m_id, m_req, m_resp in methods:
        method = ServiceMethod(m_id, m_name, m_req, m_resp)
        service.add_method(method)

    service._build_client_proxy()
    service._build_server()

    _hash_to_service[service.hval] = service
    return service

class RpcBroker:
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ':' + self.__class__.__name__)
        self._imported_services = {}
        self._exported_services = []
        self._pending_responses = {}
        self._hash_to_export = {}

        # The token to be used in the next request
        self._next_token = 0

    def _get_token(self):
        cur = self._next_token
        self._next_token += 1
        return cur

    def send_response(self, header, resp):
        self.logger.debug('send_response(%r,%r)', header, resp)
        header = mtypes.BnetPacketHeader(ServiceId=254,
                                         Status=0,
                                         Token=header.Token)
        self.send_packet(header, resp)

    def send_request(self, header, req):
        self.logger.debug('send_request(%r,%r)', header, req)
        header.Token = self._get_token()
        self.send_packet(header, req)
        
    def send_data(self, buf):
        raise NotImplementedError

    def send_packet(self, header, body):
        buf = bytearray(1024)
        if body is not None:
            body_size = body.encode_buf(buf)
            body = bytes(buf[:body_size])
        else:
            body_size = 0
        header.Size = body_size
        
        header_end = header.encode_buf(buf, 2)
        header_size = header_end - 2
        
        buf[0] = (header_size >> 8) & 0xFF
        buf[1] = header_size & 0xFF
        
        if body is not None:
            buf[header_end:header_end+body_size] = body
        
        self.send_data(buf[:header_end+body_size])

    def handle_packet(self, header, body):
        self.logger.debug('handle_packet(%r,%r)', header, body)

        service_id = header.ServiceId
        if service_id == 254:
            # is a response
            pass
        else:
            # is a request - dispatch to service
            method_id = header.MethodId
            service = self.get_exported_service(service_id)
            service._handle_packet(header, body)

    def get_export_by_hash(self, hval):
        return self._hash_to_export[hval]

    def get_exported_service(self, export_id):
        return self._exported_services[export_id]

    def get_response_by_token_id(self, token_id):
        return self._pending_responses[token_id]

    def add_import(self, client):
        self._imported_services[client.service.hval] = client
        client.broker = self
        return client
    
    def add_export(self, server):        
        server.id = len(self._exported_services)
        self._exported_services.append(server)
        self._hash_to_export[server.service.hval] = server
        server.broker = self
        return server
