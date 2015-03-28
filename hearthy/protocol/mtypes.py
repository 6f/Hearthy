#!/usr/bin/env python3
"""
Hearthstone Message Types
"""

from hearthy.protocol import mstruct

_enum = mstruct.MInteger(64, True)
_bool = mstruct.MInteger(64, True)

_int32 = mstruct.MInteger(32, True)
_uint32 = mstruct.MInteger(32, False)

_int64 = mstruct.MInteger(64, True)
_uint64 = mstruct.MInteger(64, False)

_fixed32 = mstruct.MBasicFixed(False, 32, False)
_fixed64 = mstruct.MBasicFixed(False, 64, False)
_float = mstruct.MBasicFixed(True, 32)

_basic_typehandler = {
    'enum': _enum,
    'int': _int32,
    'bool': _int32,
    'int32': _int32,
    'uint32': _uint32,
    'int64': _int64,
    'uint64': _uint64,
    'fixed32': _fixed32,
    'fixed64': _fixed64,
    'float': _float,
    'bytes': mstruct.MBytes,
    'string': mstruct.MString
}

_types_to_build = []
def _deftype(name, fields):
    _types_to_build.append((name, fields))

def _build_docstring(name, fields):
    header = 'Automatically generated class "{0}"\n\nField Definitions:'.format(name)
    fields = '\n'.join('[{0:2}] {2:10} {1}'.format(*x) for x in fields)
    return header + '\n' + fields

def _build_types():
    update = {}
    for name, fields in _types_to_build:
        newtype = type(name, (mstruct.MStruct,),
                       {'__slots__':[x[1] for x in fields],
                        '__doc__': _build_docstring(name, fields),
                        '_mfields_':{}})

        assert name not in update, 'No duplicated definitions'
        update[name] = newtype

    for name, fields in _types_to_build:
        mfields = {}
        for field in fields:
            is_array = False
            tname = field[2]
            if tname.endswith('[]'):
                is_array = True
                tname = tname[:-2]

            # find type handler
            typehandler = _basic_typehandler.get(tname, None)
            if typehandler is None:
                typehandler = update.get(tname, None)
                assert typehandler is not None, 'No typehandler for {0!r} found'.format(tname)

            mfields[field[0]] = (field[1], typehandler, is_array)

        update[name]._mfields_.update(mfields)

    # finally put them into the module namespace
    globals().update(update)

_deftype('PowerHistory', [
    (1, 'List', 'PowerHistoryData[]'),
])

_deftype('PowerHistoryData', [
    (1, 'FullEntity', 'PowerHistoryEntity'),
    (2, 'ShowEntity', 'PowerHistoryEntity'),
    (3, 'HideEntity', 'PowerHistoryHide'),
    (4, 'TagChange',  'PowerHistoryTagChange'),
    (5, 'CreateGame', 'PowerHistoryCreateGame'),
    (6, 'PowerStart', 'PowerHistoryStart'),
    (7, 'PowerEnd',   'PowerHistoryEnd'),
    (8, 'MetaData',   'PowerHistoryMetaData')
])

_deftype('PowerHistoryStart', [
    (1, 'Type',   'enum'),  # PowSubType
    (2, 'Index',  'int32'),
    (3, 'Source', 'int32'),
    (4, 'Target', 'int32')
])

_deftype('PowerHistoryEnd', [])

_deftype('PowerHistoryMetaData', [
    (2, 'Info',     'int[]'),
    (3, 'MetaType', 'int'),
    (4, 'Data',     'int')
])

_deftype('ClientPacket', [
    (1, 'Packet', 'bytes')
])

_deftype('DebugMessage', [
    (1, 'Message', 'string')
])

_deftype('Entity', [
    (1, 'Id',   'int32'),
    (2, 'Tags', 'Tag[]')
])

_deftype('EntityChoice', [
    (1, 'Id',          'int32'),
    (2, 'ChoiceType',  'int32'),
    (3, 'Cancelable',  'bool'),
    (4, 'CountMin',    'int32'),
    (5, 'CountMax',    'int32'),
    (6, 'Entities',    'int32[]'),
    (7, 'SourceField', 'int32')
])

_deftype('PowerHistoryCreateGame', [
    (1, 'GameEntity', 'Entity'),
    (2, 'Players',    'Player[]')
])

_deftype('BeginPlaying', [
    (1, 'Mode', 'enum')
])

_deftype('Platform', [
    (1, 'OS',     'int32'),
    (2, 'Screen', 'int32'),
    (3, 'Name',   'string')
])

_deftype('AuroraHandshake', [
    (1, 'GameHandle',   'int32'),
    (2, 'Password',     'string'),
    (3, 'ClientHandle', 'int64'),
    (4, 'Mission',      'int32'),
    (5, 'Version',      'string'),
    (6, 'OldPlatform',  'int32'),
    (7, 'Platform',     'Platform')
])

_deftype('AutoLogin', [
    (1, 'User',      'string'),
    (2, 'Pwd',       'string'),
    (3, 'BuildId',   'int32'),
    (4, 'DebugName', 'string'),
    (5, 'Source',    'int32')
])

_deftype('BnetId', [
    (1, 'Lo', 'uint64'),
    (2, 'Hi', 'uint64')
])

_deftype('Player', [
    (1, 'Id',            'int32'),
    (2, 'GameAccountId', 'BnetId'),
    (3, 'CardBack',      'int32'),
    (4, 'Entity',        'Entity')
])

_deftype('PowerHistoryHide', [
    (1, 'Entity', 'int32'),
    (2, 'Zone',   'int32')
])

_deftype('PowerHistoryTagChange', [
    (1, 'Entity', 'int'),
    (2, 'Tag',    'int'),
    (3, 'Value',  'int')
])

_deftype('PowerHistoryEntity', [
    (1, 'Entity', 'int32'),
    (2, 'Name',   'string'),
    (3, 'Tags',   'Tag[]')
])

_deftype('Tag', [
    (1, 'Name',  'int'),
    (2, 'Value', 'int')
])

_deftype('MouseInfo', [
    (1, 'ArrowOrigin', 'int'),
    (2, 'HeldCard',    'int'),
    (3, 'OverCard',    'int'),
    (4, 'X',           'int'),
    (5, 'Y',           'int')
])

_deftype('UserUI', [
    (1, 'MouseInfo', 'MouseInfo'),
    (2, 'Emote',     'int')
])

_deftype('TurnTimer', [
    (1, 'Seconds', 'int'),
    (2, 'Turn',    'int'),
    (3, 'Show',    'bool')
])

# Type Enum: PASS = 1, END_TURN, POWER
_deftype('Option', [
    (1, 'Type',       'enum'),
    (2, 'MainOption', 'SubOption'),
    (3, 'SubOptions', 'SubOption[]')
])

_deftype('SpectatorHandshake', [
    (1, 'GameHandle', 'uint32'),
    (2, 'Password', 'string'),
    (3, 'Version', 'string'),
    (4, 'Platform', 'Platform'),
    (5, 'GameAccountId', 'BnetId')
])

_deftype('SpectatorChange', [
    (1, 'GameAccountId', 'BnetId'),
    (2, 'IsRemoved', 'bool')
])

_deftype('SpectatorRemoved', [
    (1, 'ReasonCode', 'int32')
])

_deftype('SpectatorNotify', [
    (1, 'PlayerId', 'int32'),
    (2, 'ChooseOption', 'ChooseOption'),
    (3, 'ChooseEntities', 'ChooseEntities'),
    (4, 'SpectatorChange', 'SpectatorChange[]'),
    (5, 'SpectatorPasswordUpdate', 'string'),
    (6, 'SpectatorRemoved', 'SpectatorRemoved')
])

_deftype('InviteToSpectate', [
    (1, 'BnetAccountId', 'BnetId'),
    (2, 'GameAccountId', 'BnetId')
])

_deftype('ForcedEntityChoice', [
    (1, 'Id', 'int32'),
    (2, 'Entities', 'int32')
])

_deftype('AllOptions', [
    (1, 'Id',      'int32'),
    (2, 'Options', 'Option[]')
])

_deftype('ChooseEntities', [
    (1, 'Id',       'int32'),
    (2, 'Entities', 'int32[]')
])

_deftype('ChooseOption', [
    (1, 'Id',         'int32'),
    (2, 'Index',      'int32'),
    (3, 'Target',     'int32'),
    (4, 'SubOption',  'int32'),
    (5, 'Position',   'int32'),
    (6, 'OldPlatform','int32'),
    (7, 'Platform',   'Platform')
])

_deftype('ServerResult', [
    (1, 'ResultCode', 'int32'),
    (2, 'RetryDelaySeconds', 'float')
])

_deftype('Ping', [])
_deftype('Pong', [])

_deftype('Notification', [
    (1, 'Type', 'int'), #  IN_HAND_CARD_CAP = 1, MANA_CAP
])

_deftype('NAckOption', [
    (1, 'Id', 'int')
])

_deftype('GameStarting', [
    (1, 'GameHandle', 'int32')
])

_deftype('FinishGameState', [])

_deftype('GameCancelled', [
    (1, 'Reason', 'int') # OPPONENT_TIMEOUT = 1
])

_deftype('GameSetup', [
    (1, 'Board',                      'int32'),
    (2, 'MaxSecretsPerPlayer',        'int32'),
    (3, 'MaxFriendlyMinionPerPlayer', 'int32'),
    (4, 'KeepAliveFrequency',         'int32')
])

_deftype('GetGameState', [])

_deftype('GiveUp', [
    (1, 'OldPlatform','int32'),
    (2, 'Platform',   'Platform')
])

_deftype('SubOption', [
    (1, 'Id',      'int32'),
    (3, 'Targets', 'int32[]')
])

_deftype('StartGameState', [
    (1, 'GameEntity', 'Entity'),
    (2, 'Players',    'Player[]')
])

_deftype('PreLoad', [
    (1, 'Cards', 'int[]')
])

_deftype('PreCast', [
    (1, 'Entity', 'int')
])

_deftype('DebugConsoleCommand', [
    (1, 'Command', 'string')
])

_deftype('DebugConsoleResponse', [
    (1, 'Response', 'string'),
    (2, 'ResponseType', 'enum') # CONSOLE_OUTPUT, LOG_MESSAGE
])

_deftype('BnetBoundService', [
    (1, 'Hash', 'fixed32'),
    (2, 'Id', 'uint32')
])

_deftype('BnetBindRequest', [
    (1, 'ImportedServiceHash', 'fixed32[]'),
    (2, 'ExportedService', 'BnetBoundService[]')
])

_deftype('BnetConnectRequest', [
    (1, 'ClientId', 'BnetProcessId'),
    (2, 'BindRequest', 'BnetBindRequest')
])

_deftype('BnetContentHandle', [
    (1, 'region', 'fixed32'),
    (2, 'usage', 'fixed32'),
    (3, 'hash', 'bytes'),
    (4, 'proto_url', 'string')
])

_deftype('BnetContentMeteringContentHandles', [
    (1, 'List', 'BnetContentHandle[]')
])

_deftype('BnetBindResponse', [
    (1, 'ImportedServices', 'uint32[]')
])

_deftype('BnetConnectResponse', [
    (1, 'ServerId', 'BnetProcessId'),
    (2, 'ClientId', 'BnetProcessId'),
    (3, 'BindResult', 'uint32'),
    (4, 'BindResponse', 'BnetBindResponse'),
    (5, 'ContentHandleArray', 'BnetContentMeteringContentHandles'),
    (6, 'ServerTime', 'uint64')
])

_deftype('BnetNoData', [
])

_deftype('BnetLogonRequest', [
    (1, 'program', 'string'),
    (2, 'platform', 'string'),
    (3, 'locale', 'string'),
    (4, 'email', 'string'),
    (5, 'version', 'string'),
    (6, 'application_version', 'int32'),
    (7, 'public_computer', 'bool'),
    (8, 'sso_id', 'bytes'),
    (9, 'disconnect_on_cookie_fail', 'bool'),
    (10, 'allow_logon_queue_notifications', 'bool'),
    (11, 'web_client_verification', 'bool'),
    (12, 'cached_web_credentials', 'bytes'),
    (14, 'user_agent', 'string')
])

_deftype('EntityId', [
    (1, 'high', 'fixed64'),
    (2, 'low', 'fixed64')
])

_deftype('Attribute', [
    (1, 'name', 'string'),
    (2, 'value', 'BnetVariant')
])

_deftype('Friend', [
    (1, 'id', 'EntityId'),
    (2, 'atttribute', 'Attribute[]'),
    (3, 'role', 'uint32[]'),
    (4, 'privileges', 'uint64'),
    (5, 'attributes_epoch', 'uint64'),
    (6, 'full_name', 'string'),
    (7, 'battle_tag', 'string')
])

_deftype('Identity', [
    (1, 'account_id', 'EntityId'),
    (2, 'game_account_id', 'EntityId')
])

_deftype('Role', [
    (1, 'id', 'uint32'),
    (2, 'name', 'string'),
    (3, 'priviledge', 'string[]'),
    (4, 'assignable_role', 'uint32[]'),
    (5, 'required', 'bool'),
    (6, 'unique', 'bool'),
    (7, 'relegation_role', 'uint32'),
    (8, 'attribute', 'Attribute[]')
])

_deftype('Invitation', [
    (1, 'id', 'fixed64'),
    (2, 'inviter_identity', 'Identity'),
    (3, 'invitee_identity', 'Identity'),
    (4, 'inviter_name', 'string'),
    (5, 'invitee_name', 'string'),
    (6, 'invitation_message', 'string'),
    (7, 'creation_time', 'uint64'),
    (8, 'expiration_time', 'uint64')
])

_deftype('SubscribeToFriendsRequest', [
    (1, 'agent_id', 'EntityId'),
    (2, 'object_id', 'uint64')
])

_deftype('SubscribeToFriendsResponse', [
    (1, 'max_friends', 'uint32'),
    (2, 'max_received_invitations', 'uint32'),
    (3, 'max_sent_invitations', 'uint32'),
    (4, 'role', 'Role[]'),
    (5, 'friends', 'Friend[]'),
    (6, 'sent_invitations', 'Invitation[]'),
    (7, 'received_invitations', 'Invitation[]')
])

_deftype('BnetPresenceSubscribeRequest', [
    (1, 'agent_id', 'EntityId'),
    (2, 'entity_id', 'EntityId'),
    (3, 'object_id', 'uint64'),
    (4, 'program_id', 'fixed32[]')
])

_deftype('BnetPresenceUnsubscribeRequest', [
    (1, 'agent_id', 'EntityId'),
    (2, 'entity_id', 'EntityId')
])

_deftype('PresenceFieldKey', [
    (1, 'program', 'uint32'),
    (2, 'group', 'uint32'),
    (3, 'field', 'uint32'),
    (4, 'index', 'uint64')
])

_deftype('PresenceField', [
    (1, 'key', 'PresenceFieldKey'),
    (2, 'value', 'BnetVariant')
])

_deftype('PresenceFieldOperation', [
    (1, 'field', 'PresenceField'),
    (2, 'operation', 'enum')
])

_deftype('BnetPresenceUpdateRequest', [
    (1, 'entity_id', 'EntityId'),
    (2, 'field_operation', 'PresenceFieldOperation[]')
])

_deftype('BnetPresenceQueryRequest', [
    (1, 'entity_id', 'EntityId'),
    (2, 'key', 'PresenceFieldKey')
])

_deftype('BnetPresenceQueryResponse', [
    (2, 'field', 'PresenceField[]')
])

_deftype('BnetVariant', [
    (2, 'boolval', 'bool'),
    (3, 'intval', 'int64'),
    (4, 'floatval', 'float'),
    (5, 'stringva', 'string'),
    (6, 'blobval', 'bytes'),
    (7, 'messageval', 'bytes'),
    (8, 'fourccval', 'string'),
    (9, 'uintval', 'uint64'),
    (10, 'entityidval', 'EntityId')
])

_deftype('BnetLogonUpdateRequest', [
    (1, 'error_code', 'uint32')
])

_deftype('BnetLogonResult', [
    (1, 'error_code', 'uint32'),
    (2, 'account', 'EntityId'),
    (3, 'game_account', 'EntityId[]'),
    (4, 'email', 'string'),
    (5, 'available_region', 'uint32[]'),
    (6, 'connected_region', 'uint32'),
    (7, 'battle_tag', 'string'),
    (8, 'geoip_country', 'string')
])

_deftype('BnetEchoRequest', [
    (1, 'time', 'fixed64'),
    (2, 'network_only', 'bool'),
    (3, 'payload', 'bytes')
])

_deftype('BnetEchoResponse', [
    (1, 'time', 'fixed64'),
    (2, 'payload', 'bytes')
])

_deftype('BnetProcessId', [
    (1, 'Label', 'uint32'),
    (2, 'Epoch', 'uint32')
])

_deftype('BnetObjectAddress', [
    (1, 'Host', 'BnetProcessId'),
    (2, 'ObjectId', 'uint64')
])

_deftype('BnetErrorInfo', [
    (1, 'ObjectAddress', 'BnetObjectAddress'),
    (2, 'Status', 'uint32'),
    (3, 'ServiceHash', 'uint32'),
    (4, 'MethodId', 'uint32')
])

_deftype('BnetModuleLoadRequest', [
    (1, 'ModuleHandle', 'BnetContentHandle'),
    (2, 'Message', 'bytes')
])

_deftype('BnetEncryptRequest', [
])

_deftype('BnetModuleMessageRequest', [
    (1, 'ModuleId', 'int32'),
    (2, 'Message', 'bytes')
])

_deftype('BnetModuleNotification', [
    (2, 'ModuleId', 'int32'),
    (3, 'Result', 'uint32')
])

_deftype('BnetDisconnectRequest', [
    (1, 'error_code', 'uint32')
])

_deftype('BnetLogonQueueUpdateRequest', [
    (1, 'Position', 'uint32'),
    (2, 'EstimatedTime', 'uint64'),
    (3, 'EtaDeviationInSec', 'uint64')
])

_deftype('BnetPacketHeader', [
    (1, 'ServiceId', 'uint32'),
    (2, 'MethodId', 'uint32'),
    (3, 'Token', 'uint32'),
    (4, 'ObjectId', 'uint32'),
    (5, 'Size', 'uint32'),
    (6, 'Status', 'uint32'),
    (7, 'Error', 'BnetErrorInfo[]'),
    (8, 'Timeout', 'uint64')
])

# == Notification ==
_deftype('BnetNotification', [
    (1, 'sender_id', 'EntityId'),
    (2, 'target_id', 'EntityId'),
    (3, 'type', 'string'),
    (4, 'attribute', 'Attribute[]'),
    (5, 'sender_account_id', 'EntityId'),
    (6, 'target_account_id', 'EntityId'),
    (7, 'sender_battle_tag', 'string')
])

# === Resource Service ===
_deftype('ContentHandleRequest', [
    (1, 'program_id', 'fixed32'),
    (2, 'stream_id', 'fixed32'),
    (3, 'locale', 'fixed32')
])

# === Account Service ===
_deftype('PrivacyInfo', [
    (3, 'is_using_rid', 'bool'),
    (4, 'real_id_visible_for_view_friends', 'bool'),
    (5, 'is_hidden_from_friend_finder', 'bool'),
    # (PRIVACY_ME, PRIVACY_FRIENDS, PRIVACY_EVERYONE)
    (6, 'game_info_privacy', 'enum')
])

_deftype('ParentalControlInfo', [
    (3, 'timezone', 'string'),
    (4, 'minutes_per_day', 'uint32'),
    (5, 'minutes_per_week', 'uint32'),
    (6, 'can_receive_voice', 'bool'),
    (7, 'can_send_voice', 'bool'),
    (8, 'play_schedule', 'bool[]')
])

_deftype('RegionTag', [
    (1, 'region', 'fixed32'),
    (2, 'tag', 'fixed32')
])

_deftype('ProgramTag', [
    (1, 'program', 'fixed32'),
    (2, 'tag', 'fixed32')
])

_deftype('AccountFieldTags', [
    (1, 'account_level_info_tag', 'fixed32'),
    (2, 'privacy_info_tag', 'fixed32'),
    (3, 'parental_control_info_tag', 'fixed32'),
    (4, 'game_level_info_tags', 'ProgramTag[]'),
    (5, 'game_status_tags', 'ProgramTag[]'),
    (6, 'game_account_tags', 'RegionTag[]')
])

_deftype('GameLevelInfo', [
    (3, 'is_started_edition', 'bool'),
    (4, 'is_trial', 'bool'),
    (5, 'is_lifetime', 'bool'),
    (6, 'is_restricted', 'bool'),
    (7, 'is_beta', 'bool'),
    (8, 'name', 'string'),
    (9, 'program', 'fixed32'),
    (10, 'licenses', 'AccountLicense[]'),
    (11, 'has_realm_permissions', 'uint32')
])

_deftype('GameStatus', [
    (4, 'is_suspended', 'bool'),
    (5, 'is_banned', 'bool'),
    (6, 'suspension_expires', 'uint64'),
    (7, 'program', 'fixed32')
])

_deftype('GameAccountHandle', [
    (1, 'id', 'fixed32'),
    (2, 'program', 'fixed32'),
    (3, 'region', 'uint32')
])

_deftype('GameAccountList', [
    (3, 'region', 'uint32'),
    (4, 'handle', 'GameAccountHandle[]')
])

_deftype('AccountLicense', [
    (1, 'id', 'uint32'),
    (2, 'expires', 'uint64')
])

_deftype('AccountLevelInfo', [
    (3, 'licenses', 'AccountLicense[]'),
    (4, 'default_currency', 'fixed32'),
    (5, 'country', 'string'),
    (6, 'preferred_region', 'uint32')
])

_deftype('AccountState', [
    (1, 'account_level_info', 'AccountLevelInfo'),
    (2, 'privacy_info', 'PrivacyInfo'),
    (3, 'parental_control_info', 'ParentalControlInfo'),
    (5, 'game_level_info', 'GameLevelInfo[]'),
    (6, 'game_status', 'GameStatus[]'),
    (7, 'game_accounts', 'GameAccountList[]'),
])

_deftype('AccountFieldOptions', [
    (1, 'all_fields', 'bool'),
    (2, 'field_account_level_info', 'bool'),
    (3, 'field_privacy_info', 'bool'),
    (4, 'field_parental_control_info', 'bool'),
    (6, 'field_game_level_info', 'bool'),
    (7, 'field_game_status', 'bool'),
    (8, 'field_game_accounts', 'bool')
])

_deftype('GetAccountStateRequest', [
    (1, 'entity_id', 'EntityId'),
    (2, 'program', 'uint32'),
    (3, 'region', 'uint32'),
    (10, 'options', 'AccountFieldOptions'),
    (11, 'tags', 'AccountFieldTags'),
])

_deftype('GetAccountStateResponse', [
    (1, 'state', 'AccountState'),
    (2, 'tags', 'AccountFieldTags')
])

# Channel Invitation Service
_deftype('SubscribeChannelInvitationRequest', [
    (1, 'agent_id', 'EntityId'),
    (2, 'object_id', 'uint64')
])

_deftype('InvitationCollection', [
    (1, 'service_type', 'uint32'),
    (2, 'max_received_invitations', 'uint32'),
    (3, 'object_id', 'uint64'),
    (4, 'received_invitation', 'Invitation[]')
])

_deftype('SubscribeChannelInvitationResponse', [
    (1, 'collection', 'InvitationCollection[]'),
    (2, 'received_invitation', 'Invitation[]')
])

_build_types()
