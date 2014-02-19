# Hearthy #
Hearthy is a decoder for the network protocol used by [Hearthstone](http://us.battle.net/hearthstone/en/).
This project is still in early stages of development. Only the game protocol has been implemented so far.


## UI #
Some basic UI tools for exploring protocol dumps are provided.
![tk ui](screenshots/streamview.png?raw=true)
![tk ui](screenshots/entitybrowser.png?raw=true)

## Supported Packets ##
The following packets are currently supported:
Note: S->C means the server sends it to the client

Packet Name     | Dir | Description
--------------- | --- | ----------
PowerHistory    | S>C | State changes
UserUI          | Bi  | UI actions
TurnTimer       | S>C | Seconds left in turn
GetGameState    | C>S | Game state query
StartGameState  | S>C | Game/Player info
FinishGameState | S>C | Sent after StatGameState
GameSetup       | S>C | Game Board and Rules
GameCancelled   | S>C | Game has been cancelled
EntityChoice    | S>C | Used during mulligan
ChooseEntities  | C>S | Response to EntityChoice
AllOptions      | S>S | List of possible client actions
ChooseOption    | C>S | Response to AllOptions
BeginPlaying    | S>C | Playing mode
AuroraHandshake | C>S | Identification
GameStarting    | S>C | Sent after login
PreLoad         | ??? | ???
PreCast         | ??? | ???
Notification    | ??? | ???
NAckOption      | ??? | ???
GiveUp          | ??? | Concede?
DebugMessage    | ??? | ???
ClientPacket    | ??? | ???                                                                                      

For detailed contents of the packets see `protocol.mtypes`.

## Example Usage ##
The usual usage of this package is to use the `protocol.utils.Splitter` class to split a network stream into packets followed by `protocol.decoder.decode_packet` to decode the packets.

```python
from hearthy.protocol.utils import Splitter
from hearthy.protocol.decoder import decode_packet
from hearthy.protocol import mtypes

s = Splitter()

while True:
    buf = network_stream.read(BUFSIZE)
    for message_type, buf in s.feed(buf):
        decoded = decode_packet(message_type, buf)
        # do something with the decoded packet
        # test which packet it is using
        # e.g. isinstance(decoded, mtypes.AuroraHandShake)
```

## Network Capture ##
A tool to automatically record tcp streams has been included in `helper/hcapture.c`. It uses `libnids` which uses `libpcap` to capture network traffic and performs tcp defragmentation and reassembly. The tool looks for tcp connections on port `1119` and saves them to a file. Only linux is currently supported - patches are welcome.

To compile:
```sh
gcc hcapture.c -Wall -lnids -o capture
```

Usage:
```sh
./capture -i mynetworkiface outfile.hcapng
```
Python code to decode the capture file is provided in `datasource/hcapng.py`.

### Example ###
Reads a hcapture capture file and splits the network streams into packets.

```python
import sys
from datetime import datetime

from hearthy.datasource import hcapng
from hearthy import exceptions

class Connection:
    def __init__(self):
        self._s = [Splitter(), Splitter()]

    def feed(self, who, buf):
        for atype, buf in self._s[who].feed(buf):
            # decode and handle packet
            
d = {}
with open(filename, 'rb') as f:
    gen = hcapng.parse(f)

    header = next(gen)
    print('Recording started at {0}'.format(
        datetime.fromtimestamp(header.ts).strftime('%Y.%m.%d %H:%M:%S')))

    for ts, event in gen:
        if isinstance(event, hcapng.EvClose):
            if event.stream_id in d:
                del d[event.stream_id]
        elif isinstance(event, hcapng.EvData):
            if event.stream_id in d:
                try:
                    d[event.stream_id].feed(event.who, event.data)
                except exceptions.BufferFullException:
                    # Usually means that the tcp stream wasn't a game session.
                    del d[event.stream_id]
        elif isinstance(event, hcapng.EvNewConnection):
            d[event.stream_id] = Connection()
```
