import logging
import time
from hearthy.protocol import mtypes
from hearthy.bnet import rpcdef, rpc, auth, utils
from hearthy.proxy import pipe
from hearthy.bnet.decode import SplitterBuf
from hearthy.protocol.utils import hexdump

EPOCH = 0xAFFE
SERVER_ID = mtypes.BnetProcessId(Label=0xABCD, Epoch=EPOCH)
CLIENT_ID = mtypes.BnetProcessId(Label=0xB0FF, Epoch=EPOCH)

class DummyServer(rpc.ServiceServer):
    def __init__(self, hval):
        super().__init__()
        self.service = rpc.Service('dummy')
        self.service.hval = hval
        
    def _handle_packet(self, header, body):
        self.logger.warn('Ignoring packet for unknown service with hash 0x%08x. Header %s', self.service.hval, header)

class ConnectService(rpcdef.ConnectService.Server):
    def __init__(self):
        super().__init__()
        
    def Connect(self, req):
        import_id = []
        for i, hval in enumerate(req.BindRequest.ImportedServiceHash):
            try:
                server = self.broker.get_export_by_hash(hval)
            except KeyError:
                self.logger.warn('Client requested import of non-exported service with hash 0x%08x', hval)
                server = self.broker.add_export(DummyServer(hval))

            self.logger.info('Client imported %r with id %d', server.service, server.id)
            import_id.append(server.id)

        for item in req.BindRequest.ExportedService:
            imported_service = self.broker._imported_services.get(item.Hash, None)
            if imported_service is None:
                self.logger.warn('Ignoring client export with hash 0x%08x', item.Hash)
            else:
                self.logger.debug('Binding %r to id %s', imported_service, item.Id)
                imported_service.id = item.Id

        # TODO: check that all imported services have been bound

        # Send bind response
        bind_response = mtypes.BnetBindResponse(ImportedServices=import_id)

        resp = mtypes.BnetConnectResponse(
            ServerId=mtypes.BnetProcessId(Label=3868510373,Epoch=int(time.time())),
            ClientId=mtypes.BnetProcessId(Label=1255760,Epoch=int(time.time())),
            BindResult=0,
            BindResponse=bind_response,
            ServerTime=int(time.time()*1000))

        return resp

class AuthenticationServer(rpcdef.AuthenticationServer.Server):
    def __init__(self, auth_client):
        super().__init__()
        self._auth_client = auth_client

        # Module Management
        self._load_queue = []
        self._id_to_module = {}

    def send_message(self, from_module, message):
        self._auth_client.ModuleMessage(ModuleId=from_module, Message=message)

    def add_module(self, module):
        self._load_queue.append(module)
        module.manager = self
        load_request = module.get_load_request()
        self._auth_client.ModuleLoad(load_request)

    def ModuleNotify(self, req):
        if len(self._load_queue) == 0:
            self.logger.warn('Received module notification but load queue is empty')
        else:
            module = self._load_queue.pop(0)
            module_id = req.ModuleId
            result = req.Result

            # TODO: cleaner checks
            assert result == 0
            assert module_id not in self._id_to_module

            self._id_to_module[module_id] = module
            module.id = module_id
            module.manager = self
            module.on_loaded()

    def ModuleMessage(self, req):
        module_id = req.ModuleId
        module = self._id_to_module[module_id]
        module.on_message(req.Message)
        
    def Logon(self, req):
        yield mtypes.BnetNoData()
        
        # self._auth_client.LogonQueueUpdate(
        #      Position=1,
        #      EstimatedTime=int(time.time())+100000,
        #      EtaDeviationInSec=0)
        # self._auth_client.LogonQueueEnd()

        # #self.add_module(auth.ThumbprintModule())
        # #self.add_module(auth.PasswordAuthenticator('waifu@blizzard.com', 'pass'))
        # self._auth_client.LogonUpdate(error_code=0)
        self._auth_client.LogonComplete(
            error_code=0,
            account=mtypes.EntityId(high=0xdead, low=0xbeef),
            game_account=[mtypes.EntityId(high=0x1CEB00DA, low=0xBAADF00D)],
            email='email',
            available_region=[0],
            connected_region=0,
            battle_tag='bt',
            geoip_country='country')

class PresenceServiceServer(rpcdef.PresenceService.Server):
    pass

class FriendsServiceServer(rpcdef.FriendsService.Server):
    def subscribe_to_friends(self, req):
        # you have no friends :(
        response = mtypes.SubscribeToFriendsResponse(
            max_friends=10,
            max_received_invitations=5,
            max_sent_invitations=5)
        return response

class ResourcesServiceServer(rpcdef.ResourcesService.Server):
    def get_content_handle(self, req):
        program = utils.decode_fourcc(req.program_id)
        stream = utils.decode_fourcc(req.stream_id)
        locale = utils.decode_fourcc(req.locale)
        self.logger.info('get_content_handle for program=%s, stream=%s and locale=%s', program, stream, locale)

        handle = mtypes.BnetContentHandle(
            region=utils.encode_fourcc('REGI'),
            usage=utils.encode_fourcc('USAG'),
            hash=b'\x00'*32
        )
        return handle

class AccountServiceServer(rpcdef.AccountService.Server):
    def get_account_state(self, req):
        account_level_info = mtypes.AccountLevelInfo(
            preferred_region=0xDEADD00D,
            country='Equestria'
        )
        state = mtypes.AccountState(account_level_info=account_level_info)
        return mtypes.GetAccountStateResponse(state=state)

class ChannelInvitationServiceServer(rpcdef.ChannelInvitationService.Server):
    pass

class ClientHandler(rpc.RpcBroker):
    def __init__(self, server, ep):
        super().__init__()
        self._server = server
        self._ep = ep
        self._splitter = SplitterBuf()
        self._send_buf = pipe.SimpleBuf()
        
        ep.cb = self._ep_cb

        ep.want_pull(True)
        ep.want_push(False)

        auth_client = rpcdef.AuthenticationClient.build_client_proxy()
        self.add_export(ConnectService())
        self.add_export(AuthenticationServer(self.add_import(auth_client)))
        self.add_export(FriendsServiceServer())
        self.add_export(ChannelInvitationServiceServer())
        self.add_export(ResourcesServiceServer())
        self.add_export(AccountServiceServer())
        self.add_export(PresenceServiceServer())

    def send_data(self, buf):
        self._send_buf.append(buf)
        self._ep.want_push(True)

    def _ep_cb(self, ep, ev_type, ev_data):
        if ev_type == 'may_pull':
            self._ep.pull(self._splitter)
            while True:
                segment = self._splitter.pull_segment()
                if segment is None:
                    break
                self.handle_packet(segment[0], segment[1])
        elif ev_type == 'may_push':
            if self._send_buf.used > 0:
                self._ep.push(self._send_buf)
            self._ep.want_push(self._send_buf.used)
        elif ev_type == 'closed':
            self.logger.info('Connection closed')

class Server:
    def __init__(self, listen):
        provider = pipe.TcpEndpointProvider(listen)
        provider.cb = self._on_connection

    def _on_connection(self, provider, ev_type, ev_data):
        if ev_type == 'accepted':
            addr_orig, ep = ev_data
            ClientHandler(self, ep)

if __name__ == '__main__':
    import asyncore
    import logging
    logging.basicConfig(level=logging.DEBUG)

    server = Server(('0.0.0.0', 52525))
    asyncore.loop()
