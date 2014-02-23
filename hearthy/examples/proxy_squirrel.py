import asyncore

from hearthy.proxy import intercept
from hearthy.protocol import mtypes, enums

class SquirrelHandler(intercept.InterceptHandler):
    def __init__(self, use_premium=False):
        super().__init__()
        self._use_premium = use_premium

    def on_packet(self, epid, packet):
        if isinstance(packet, mtypes.PowerHistory):
            for entry in packet.List:
                if hasattr(entry, 'ShowEntity'):
                    entry.ShowEntity.Name = 'EX1_tk28' # squirrel
                
                    if self._use_premium:
                        new_tags = [x for x in entry.ShowEntity.Tags if x.Name != enums.GameTag.PREMIUM]
                        new_tags.append(mtypes.Tag(Name=enums.GameTag.PREMIUM, Value=1))
                        entry.ShowEntity.Tags = new_tags

        return intercept.INTERCEPT_ACCEPT

if __name__ == '__main__':
    import argparse
    from hearthy.proxy.proxy import Proxy
    
    parser = argparse.ArgumentParser(description='Transform all cards into squirrels')
    parser.add_argument('--premium', action='store_const', default=False, const=True,
                        help='Make the squirrels premium')
    parser.add_argument('--port', type=int, default=5412)
    parser.add_argument('--host', default='0.0.0.0')
    
    args = parser.parse_args()
    
    proxy_handler = intercept.InterceptProxyHandler(SquirrelHandler,
                                                    use_premium=args.premium)
    proxy = Proxy((args.host, args.port), handler=proxy_handler)
    
    asyncore.loop()
