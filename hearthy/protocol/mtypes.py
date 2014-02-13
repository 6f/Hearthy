#!/usr/bin/env python3
"""
Hearhstone Message Types
"""

from . import mstruct

_types_to_build = []
def _deftype(name, fields):
    _types_to_build.append((name, fields))

def _build_types():
    update = {}
    for name, fields in _types_to_build:
        newtype = type(name, (mstruct.MStruct,),
                       {'__slots__':[x[1] for x in fields],
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
            mfields[field[0]] = (field[1], update.get(tname, tname), is_array)
        update[name]._mfields_.update(mfields)

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

# Type: ATTACK=1, CONTINOUS, DEATHS, FATIGUE, PLAY, POWER, SCRIPT, TRIGGER
_deftype('PowerHistoryStart', [
    (1, 'Type',   'enum'),
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

_deftype('AuroraHandshake', [
    (1, 'GameHandle',   'int32'),
    (2, 'Password',     'string'),
    (3, 'ClientHandle', 'int64')
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
    (1, 'Id',            'int'),
    (2, 'GameAccountId', 'BnetId'),
    (4, 'Entity',        'Entity')
])

_deftype('PowerHistoryHide', [
    (1, 'Entity', 'int'),
    (2, 'Zone',   'int')
])

_deftype('PowerHistoryTagChange', [
    (1, 'Entity', 'int'),
    (2, 'Tag',    'int'),
    (3, 'Value',  'int')
])

_deftype('PowerHistoryEntity', [
    (1, 'Entity', 'int'),
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

_deftype('AllOptions', [
    (1, 'Id',      'int32'),
    (2, 'Options', 'Option[]')
])

_deftype('ChooseEntities', [
    (1, 'Id',       'int32'),
    (2, 'Entities', 'int32[]')
])

_deftype('ChooseOption', [
    (1, 'Id',        'int32'),
    (2, 'Index',     'int32'),
    (3, 'Target',    'int32'),
    (4, 'SubOption', 'int32'),
    (5, 'Position',  'int32')
])

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

_deftype('ClientInfo', [
    (1, 'Pieces',   'int32[]'),
    (2, 'CardBack', 'int32')
])

_deftype('GameSetup', [
    (1, 'Board',                      'string'),
    (2, 'Clients',                    'ClientInfo[]'),
    (3, 'MaxSecretsPerPlayer',        'int'),
    (4, 'MaxFriendlyMinionPerPlayer', 'int')
])

_deftype('GetGameState', [])

_deftype('GiveUp', [])

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

_build_types()
