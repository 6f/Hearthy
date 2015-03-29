from hearthy.protocol.type_builder import Builder
from hearthy.protocol import mtypes

def _anon():
    builder = Builder()

    builder.add('GameSessionLocation', [
        (1, 'ip_address', 'string'),
        (2, 'country', 'uint32'),
        (3, 'city', 'string')
    ])

    builder.add('GameSessionInfo', [
        (3, 'start_time', 'uint32'),
        (4, 'location', 'GameSessionLocation'),
        (5, 'has_benefactor', 'bool'),
        (6, 'is_using_igr', 'bool'),
        (7, 'parental_control_active', 'bool')
    ])

    builder.add('GetGameSessionInfoResponse', [
        (2, 'session_info', 'GameSessionInfo')
    ])

    builder.add('GetGameSessionInfoRequest', [
        (1, 'entity_id', mtypes.EntityId)
    ])

    builder.build(globals(), __name__)

_anon()
