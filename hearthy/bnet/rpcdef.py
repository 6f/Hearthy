from hearthy.protocol import mtypes, game_utilities
from hearthy.bnet import rpc

NOT_IMPLEMENTED = None
NO_RESPONSE = None

NotificationListener = rpc.defservice('bnet.protocol.notification.NotificationListener', [
    ('on_notification_received', 1, mtypes.BnetNotification, NO_RESPONSE)
])

FriendsService = rpc.defservice('bnet.protocol.friends.FriendsService', [
    ('subscribe_to_friends', 1, mtypes.SubscribeToFriendsRequest, mtypes.SubscribeToFriendsResponse)
])

ChannelInvitationService = rpc.defservice('bnet.protocol.channel_invitation.ChannelInvitationService', [
    ('subscribe', 1, mtypes.SubscribeChannelInvitationRequest, mtypes.SubscribeChannelInvitationResponse)
])

ResourcesService = rpc.defservice('bnet.protocol.resources.Resources', [
    ('get_content_handle', 1, mtypes.ContentHandleRequest, mtypes.BnetContentHandle)
])

AccountService = rpc.defservice('bnet.protocol.account.AccountService', [
    ('get_account_state', 30, mtypes.GetAccountStateRequest, mtypes.GetAccountStateResponse)
])

PresenceService = rpc.defservice('bnet.protocol.presence.PresenceService', [
    ('subscribe', 1, mtypes.BnetPresenceSubscribeRequest, mtypes.BnetNoData),
    ('Unsubscribe', 2, mtypes.BnetPresenceUnsubscribeRequest, mtypes.BnetNoData),
    ('Update', 3, mtypes.BnetPresenceUpdateRequest, mtypes.BnetNoData),
    ('Query', 4, mtypes.BnetPresenceQueryRequest, mtypes.BnetPresenceQueryResponse)
])

AuthenticationServer = rpc.defservice('bnet.protocol.authentication.AuthenticationServer', [
    ('Logon', 1, mtypes.BnetLogonRequest, mtypes.BnetNoData),
    ('ModuleNotify', 2, mtypes.BnetModuleNotification, mtypes.BnetNoData),
    ('ModuleMessage', 3, mtypes.BnetModuleMessageRequest, mtypes.BnetNoData),
    ('SelectGameAccount_DEPRECATED', 4, mtypes.EntityId, mtypes.BnetNoData),
    ('GenerateTempCookie', 5, NOT_IMPLEMENTED, NOT_IMPLEMENTED),
    ('SelectGameAccount', 6, NOT_IMPLEMENTED, mtypes.BnetNoData),
    ('VerifyWebCredentials', 7, NOT_IMPLEMENTED, mtypes.BnetNoData),
])

ConnectService = rpc.defservice('bnet.protocol.connection.ConnectionService', [
    ('Connect', 1, mtypes.BnetConnectRequest, mtypes.BnetConnectResponse),
    ('Bind', 2, NOT_IMPLEMENTED, NOT_IMPLEMENTED), # BindResponse
    ('Echo', 3, mtypes.BnetEchoRequest, mtypes.BnetEchoResponse),
    ('ForceDisconnect', 4, NOT_IMPLEMENTED, NO_RESPONSE), # no response
    ('KeepAlive', 5, mtypes.BnetNoData, NO_RESPONSE),
    ('Encrypt', 6, mtypes.BnetEncryptRequest, mtypes.BnetNoData),
    ('RequestDisconnect', 7, mtypes.BnetDisconnectRequest, NO_RESPONSE) # no response
])

AuthenticationClient = rpc.defservice('bnet.protocol.authentication.AuthenticationClient', [
    ('ModuleLoad',          1,  mtypes.BnetModuleLoadRequest, NO_RESPONSE), 
    ('ModuleMessage',       2,  mtypes.BnetModuleMessageRequest, mtypes.BnetNoData), 
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

GameUtilities = rpc.defservice('bnet.protocol.game_utilities.GameUtilities', [
    ('process_client_request', 1, game_utilities.ClientRequest, game_utilities.ClientResponse),
    ('presence_channel_created', 2, NOT_IMPLEMENTED, NOT_IMPLEMENTED),
    ('get_player_variables', 3, NOT_IMPLEMENTED, NOT_IMPLEMENTED),
    ('get_load', 5, NOT_IMPLEMENTED, NOT_IMPLEMENTED),
    ('process_server_request', 6, NOT_IMPLEMENTED, NOT_IMPLEMENTED),
    ('notify_game_account_online', 7, NOT_IMPLEMENTED, NOT_IMPLEMENTED),
    ('notify_game_account_offline', 8, NOT_IMPLEMENTED, NOT_IMPLEMENTED),
])
