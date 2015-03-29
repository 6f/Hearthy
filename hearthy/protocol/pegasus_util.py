from hearthy.protocol.type_builder import Builder
from hearthy.protocol import game_utilities, mtypes

def _anon():
    builder = Builder()

    builder.add('AssetsVersionResponse', [
        (1, 'version', 'int32')
    ])

    builder.add('UpdateLogin', [
        (1, 'reply_required', 'bool')
    ])

    builder.add('UpdateLoginComplete', [])

    builder.add('SetProgress', [
        (1, 'value', 'int64[]')
    ])

    builder.add('SetProgressResponse', [
        (1, 'result', 'enum'),
        (2, 'progress', 'int64')
    ])

    builder.build(globals(), __name__)

_anon()

AssetsVersionResponse.packet_id = 0x130
UpdateLogin.packet_id = 0xcd
UpdateLoginComplete.packet_id = 0x133
SetProgress.packet_id = 230
SetProgressResponse.packet_id = 0x128

def to_client_response(packet):
    buf = bytearray(1024)
    end = packet.encode_buf(buf)

    packet_id = packet.packet_id

    return game_utilities.ClientResponse(attributes=[
        mtypes.Attribute(name='?',value=mtypes.BnetVariant(intval=packet_id)),
        mtypes.Attribute(name='?',value=mtypes.BnetVariant(blobval=bytes(buf[:end])))
    ])
