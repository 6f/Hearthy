"""
Hearthstone Protocol Decoder.
"""

from . import mtypes
from .enums import PacketType

_packet_type_handlers = {
    PacketType.POWER_HISTORY: mtypes.PowerHistory,
    PacketType.USER_UI: mtypes.UserUI,
    PacketType.TURN_TIMER: mtypes.TurnTimer,
    PacketType.START_GAME_STATE: mtypes.StartGameState,
    PacketType.PRE_LOAD: mtypes.PreLoad,
    PacketType.PRE_CAST: mtypes.PreCast,
    PacketType.NOTIFICATION: mtypes.Notification,
    PacketType.NACK_OPTION: mtypes.NAckOption,
    PacketType.GIVE_UP: mtypes.GiveUp,
    PacketType.GET_GAME_STATE: mtypes.GetGameState,
    PacketType.GAME_SETUP: mtypes.GameSetup,
    PacketType.GAME_CANCELLED: mtypes.GameCancelled,
    PacketType.FINISH_GAME_STATE: mtypes.FinishGameState,
    PacketType.ENTITY_CHOICE: mtypes.EntityChoice,
    PacketType.DEBUG_MESSAGE: mtypes.DebugMessage,
    PacketType.CLIENT_PACKET: mtypes.ClientPacket,
    PacketType.CHOOSE_OPTION: mtypes.ChooseOption,
    PacketType.CHOOSE_ENTITIES: mtypes.ChooseEntities,
    PacketType.ALL_OPTIONS: mtypes.AllOptions,
    PacketType.BEGIN_PLAYING: mtypes.BeginPlaying,
    PacketType.AURORA_HANDSHAKE: mtypes.AuroraHandshake,
    PacketType.GAME_STARTING: mtypes.GameStarting
}

def decode_packet(packet_type, buf):
    handler = _packet_type_handlers.get(packet_type, None)
    if handler is None:
        raise DecodeError('No handler for packet type {0}'.format(packet_type))

    return handler.decode_buf(buf)

if __name__ == '__main__':
    import sys
    from .utils import Splitter

    if len(sys.argv) < 2:
        print('Usage: {0} <raw dump file>'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], 'rb'):
        s = Splitter()
        while True:
            buf = f.read(8*1024)
            if len(buf) == 0:
                break
            for atype, buf in s.feed(buf):
                print(decode_packet(atype, buf))
