"""
Hearthstone Protocol Decoder.
"""

import struct
from hearthy.protocol import mtypes
from hearthy.protocol.enums import PacketType
from hearthy.exceptions import DecodeError, EncodeError

_packet_type_map = [
    (PacketType.POWER_HISTORY, mtypes.PowerHistory),
    (PacketType.USER_UI, mtypes.UserUI),
    (PacketType.TURN_TIMER, mtypes.TurnTimer),
    (PacketType.START_GAME_STATE, mtypes.StartGameState),
    (PacketType.PRE_LOAD, mtypes.PreLoad),
    (PacketType.PRE_CAST, mtypes.PreCast),
    (PacketType.NOTIFICATION, mtypes.Notification),
    (PacketType.NACK_OPTION, mtypes.NAckOption),
    (PacketType.GIVE_UP, mtypes.GiveUp),
    (PacketType.GET_GAME_STATE, mtypes.GetGameState),
    (PacketType.GAME_SETUP, mtypes.GameSetup),
    (PacketType.GAME_CANCELLED, mtypes.GameCancelled),
    (PacketType.FINISH_GAME_STATE, mtypes.FinishGameState),
    (PacketType.ENTITY_CHOICE, mtypes.EntityChoice),
    (PacketType.DEBUG_MESSAGE, mtypes.DebugMessage),
    (PacketType.CLIENT_PACKET, mtypes.ClientPacket),
    (PacketType.CHOOSE_OPTION, mtypes.ChooseOption),
    (PacketType.CHOOSE_ENTITIES, mtypes.ChooseEntities),
    (PacketType.ALL_OPTIONS, mtypes.AllOptions),
    (PacketType.BEGIN_PLAYING, mtypes.BeginPlaying),
    (PacketType.AURORA_HANDSHAKE, mtypes.AuroraHandshake),
    (PacketType.GAME_STARTING, mtypes.GameStarting),
    (PacketType.DEBUG_CONSOLE_COMMAND, mtypes.DebugConsoleCommand),
    (PacketType.DEBUG_CONSOLE_RESPONSE, mtypes.DebugConsoleResponse),
    (PacketType.PING, mtypes.Ping),
    (PacketType.PONG, mtypes.Pong),
    (PacketType.FORCED_ENTITY_CHOICE, mtypes.ForcedEntityChoice),
    (PacketType.SERVER_RESULT, mtypes.ServerResult),
    (PacketType.SPECTATOR_NOTIFY, mtypes.SpectatorNotify),
    (PacketType.SPECTATOR_HANDSHAKE, mtypes.SpectatorHandshake),
    (PacketType.INVITE_TO_SPECTATE, mtypes.InviteToSpectate)
]

_packet_type_handlers = dict(_packet_type_map)
_packet_type_id = dict((y,x) for x,y in _packet_type_map)

def encode_packet(packet, buf, offset=0):
    end = packet.encode_buf(buf, offset + 8)
    packet_type = _packet_type_id.get(packet.__class__, None)
    
    if packet_type is None:
        raise EncodeError('No packet type for class {0}'.format(packet.__class__))
    
    buf[offset:offset+8] = struct.pack('<II', packet_type, end - offset - 8)
    return end

def decode_packet(packet_type, buf):
    handler = _packet_type_handlers.get(packet_type, None)
    if handler is None:
        import pdb; pdb.set_trace()
        raise DecodeError('No handler for packet type {0}'.format(packet_type))

    return handler.decode_buf(buf)

if __name__ == '__main__':
    import sys
    from .utils import Splitter

    if len(sys.argv) < 2:
        print('Usage: {0} <raw dump file>'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], 'rb') as f:
        s = Splitter()
        while True:
            buf = f.read(8*1024)
            if len(buf) == 0:
                break
            for atype, buf in s.feed(buf):
                print(decode_packet(atype, buf))
