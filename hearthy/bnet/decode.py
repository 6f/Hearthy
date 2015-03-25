import binascii
from hearthy.proxy import pipe
from hearthy.protocol import mtypes, serialize
from hearthy.protocol.utils import hexdump
from hearthy.bnet import utils

#
# TODO: XXX: This file is not used anymore (expect for SplitterBuf)
#

class SplitterBuf(pipe.SimpleBuf):
    def __init__(self):
        super().__init__()
        self._header = None

    def pull_segment(self):
        used = self.used

        # read header size
        if used < 2:
            return

        hi, lo = self.peek(2)
        header_size = (hi << 8) | lo

        header = self._header
        if header is None:
            # read header
            if used < 2 + header_size:
                return
            header = self._header = mtypes.BnetPacketHeader.decode_buf(self.peek(header_size, 2))

        print(header)
        # read body
        if used < 2 + header_size + header.Size:
            return

        body = self.peek(header.Size, 2 + header_size)

        self._header = None
        self.consume(2 + header_size + header.Size)
                     
        return (header, body)

class ServiceMethod:
    __slots__ = ['id', 'name', 'req', 'resp']
    def __init__(self, *args):
        for k, v in zip(self.__slots__, args):
            setattr(self, k, v)

_hash_to_service = {}
def _defservice(name, methods):
    hval = utils.hash(name.encode('ascii'))

    assert hval not in _hash_to_service

    attr = []
    id_to_method = []
        
    for m_name, m_id, req, resp in methods:
        m = ServiceMethod(m_id, m_name, req, resp)
        attr.append((m_name, m))
        id_to_method.append((m_id, m))

    attr.append(('methods', dict(id_to_method)))
    attr.append(('_hash_value_', hval))
    attr.append(('name', name))
    attr.append(('id', len(_hash_to_service) + 1))
    
    t = type(name.split('.')[-1]+'Service', (), dict(attr))
    _hash_to_service[hval] = t
    return t

def get_service_for_hash(hval, defval=None):
    return _hash_to_service.get(hval, defval)

NO_RESPONSE, NOT_IMPLEMENTED = range(2)
_defservice('bnet.protocol.authentication.AuthenticationServer', [
    ('Logon', 1, mtypes.BnetLogonRequest, mtypes.BnetNoData),
    ('ModuleNotify', 2, mtypes.BnetModuleNotification, mtypes.BnetNoData),
    ('ModuleMessage', 3, mtypes.BnetModuleMessageRequest, mtypes.BnetNoData),
    ('SelectGameAccount_DEPRECATED', 4, NOT_IMPLEMENTED, mtypes.BnetNoData),
    ('GenerateTempCookie', 5, NOT_IMPLEMENTED, NOT_IMPLEMENTED),
    ('SelectGameAccount', 6, NOT_IMPLEMENTED, mtypes.BnetNoData),
    ('VerifyWebCredentials', 7, NOT_IMPLEMENTED, mtypes.BnetNoData),
])

ConnectService = _defservice('bnet.protocol.connection.ConnectionService', [
    ('Connect', 1, mtypes.BnetConnectRequest, mtypes.BnetConnectResponse),
    ('Bind', 2, NOT_IMPLEMENTED, NOT_IMPLEMENTED), # BindResponse
    ('Echo', 3, mtypes.BnetEchoRequest, mtypes.BnetEchoResponse),
    ('ForceDisconnect', 4, NOT_IMPLEMENTED, NOT_IMPLEMENTED), # no response
    ('KeepAlive', 5, NOT_IMPLEMENTED, NOT_IMPLEMENTED), # no response
    ('Encrypt', 6, mtypes.BnetEncryptRequest, mtypes.BnetNoData),
    ('RequestDisconnect', 7, NOT_IMPLEMENTED, NOT_IMPLEMENTED) # no response
])

_defservice('bnet.protocol.game_utilities.GameUtilities', [
])

_defservice('bnet.protocol.channel.Channel', [
    ('AddMember'          , 1, NOT_IMPLEMENTED, mtypes.BnetNoData),
    ('RemoveMember'       , 2, NOT_IMPLEMENTED, mtypes.BnetNoData),
    ('SendMessage'        , 3, NOT_IMPLEMENTED, mtypes.BnetNoData),
    ('UpdateChannelState' , 4, NOT_IMPLEMENTED, mtypes.BnetNoData),
    ('UpdateMemberState'  , 5, NOT_IMPLEMENTED, mtypes.BnetNoData),
    ('Dissolve'           , 6, NOT_IMPLEMENTED, mtypes.BnetNoData),
    ('AddMember'          , 7, NOT_IMPLEMENTED, mtypes.BnetNoData),
    ('UnsubscribeMember'  , 8, NOT_IMPLEMENTED, mtypes.BnetNoData)
])

_defservice('bnet.protocol.account.AccountService', [
])

AuthenticationClient = _defservice('bnet.protocol.authentication.AuthenticationClient', [
    ('ModuleLoad',          1,  mtypes.BnetModuleLoadRequest, NO_RESPONSE), 
    ('ModuleMessage',       2,  mtypes.BnetModuleMessageRequest, mtypes.BnetNoData()), 
    ('AccountSettings',     3,  NOT_IMPLEMENTED, NOT_IMPLEMENTED), 
    ('ServerStateChange',   4,  NOT_IMPLEMENTED, NOT_IMPLEMENTED), 
    ('LogonComplete',       5,  mtypes.BnetLogonResult, NOT_IMPLEMENTED), 
    ('MemModuleLoad',       6,  NOT_IMPLEMENTED, NOT_IMPLEMENTED), 
    ('LogonUpdate',         10, mtypes.BnetLogonUpdateRequest, NOT_IMPLEMENTED), 
    ('VesionInfoUpdated',   11, NOT_IMPLEMENTED, NOT_IMPLEMENTED), 
    ('LogonQueueUpdate',    12, mtypes.BnetLogonQueueUpdateRequest, NOT_IMPLEMENTED),
    ('LogonQueueEnd',       13, mtypes.BnetNoData, NOT_IMPLEMENTED), 
    ('GameAccountSelected', 14, NOT_IMPLEMENTED, NOT_IMPLEMENTED), 
])

class Tracker:
    def __init__(self):
        self._req_imports = []
        self._import_bindings = {}
        self._exports = {}
        self._requests = [{}, {}]
        self._splitters = [SplitterBuf(), SplitterBuf()]

    def get_service(self, who, service_id):
        if service_id == 0:
            return ConnectService
        else:
            if who == 0:
                return self._import_bindings.get(service_id, None)
            else:
                return self._exports.get(service_id, None)

    def _handle(self, who, dec):
        if isinstance(dec, mtypes.BnetConnectRequest):
            # learn exported and imported services
            self._req_imports = dec.BindRequest.ImportedServiceHash

            for i, hval in enumerate(dec.BindRequest.ImportedServiceHash):
                service = _hash_to_service.get(hval, None)
                service_name = service.name if service is not None else '?'
                print('Import[{0}] - Hash {1}, name {2}'.format(i, hval, service_name))

            for item in dec.BindRequest.ExportedService:
                service = _hash_to_service.get(item.Hash, None)
                service_name = service.name if service is not None else '?'
                print('Export: Id {0}, Hash {1}, name {2}'.format(item.Id, item.Hash, service_name))

            for item in dec.BindRequest.ExportedService:
                self._exports[item.Id] = _hash_to_service.get(item.Hash, None)

        elif isinstance(dec, mtypes.BnetConnectResponse):
            bind_response = dec.BindResponse

            if hasattr(dec, 'ContentHandleArray'):
                cha = dec.ContentHandleArray
                for handle in cha.List:
                    print('Region: {0}'.format(utils.decode_fourcc(handle.region)))
                    print('Usage: {0}'.format(utils.decode_fourcc(handle.usage)))
                    print('Hash: {0}'.format(binascii.hexlify(handle.hash)))

            assert len(bind_response.ImportedServices) == len(self._req_imports)
            for i, service_id in enumerate(bind_response.ImportedServices):
                print('Mapping {0} <-> {1}'.format(service_id, self._req_imports[i]))
                service = _hash_to_service.get(self._req_imports[i], None)
                if service is not None:
                    print(service_id, service)
                    self._import_bindings[service_id] = service

    def parse(self, who, buf):
        print(who)
        splitter = self._splitters[who]
        splitter.append(buf)

        while True:
            segment = splitter.pull_segment()
            if segment is None:
                break
            self._parse(who, segment[0], segment[1])

    def _parse(self, who, header, body):
        print()
        print('From {0}'.format(who))
        print(header)

        hexdump(body)

        if header.ServiceId != 254:
            # this is a request
            service = self.get_service(who, header.ServiceId)
            if service is None:
                print('Unknown service id {0}'.format(header.ServiceId))
                return

            method = service.methods.get(header.MethodId, None)
            if method is None:
                print('Method id {0} of service {1} now known :('.format(header.MethodId, service.name))
                return

            print('Request for {0}:{1}'.format(service.name, method.name))

            if method.resp is not None:
                self._requests[who][header.Token] = (header.ServiceId, header.MethodId)

            if method.req == NOT_IMPLEMENTED:
                print('Request of {0}:{1} has not been implemented'.format(service.name, method.name))
                print(serialize.read_fields(body))
                return

            dec = method.req.decode_buf(body)
            print(dec)

            self._handle(who, dec)
        else:
            pending = self._requests[1-who].get(header.Token, None)
            if pending is None:
                print('Missing request for token {0}'.format(header.Token))
                return

            service_id, method_id = self._requests[1-who][header.Token]

            service = self.get_service(1-who, service_id)
            method = service.methods[method_id]
            print('Response for {0}:{1}'.format(service.name, method.name))
            print(serialize.read_fields(body))

            if method.resp == NOT_IMPLEMENTED:
                print('not implemented :(')
            else:
                dec = method.resp.decode_buf(body)
                print(dec)
                self._handle(who, dec)

            del self._requests[1-who][header.Token]

#if __name__ == '__main__':
#    import sys
#    t = Tracker()

#    with open(sys.argv[1], 'rb') as f:
#        buf = f.read()
#        t.parse(1, buf)
