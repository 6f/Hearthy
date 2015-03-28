from hearthy.protocol.type_builder import Builder
from hearthy.protocol import mtypes

def _anon():
    builder = Builder()

    builder.add('ClientResponse', [
        (1, 'attributes', [mtypes.Attribute])
    ])

    builder.add('ClientRequest', [
        (1, 'attributes', [mtypes.Attribute]),
        (2, 'host', mtypes.BnetProcessId),
        (3, 'bnet_account_id', mtypes.EntityId),
        (4, 'game_account_id', mtypes.EntityId)
    ])

    builder.build(globals(), __name__)

_anon()
