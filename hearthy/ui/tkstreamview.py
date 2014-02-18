import queue
import threading

import tkinter
from tkinter import ttk

from hearthy.datasource import hcapng
from hearthy.protocol.mstruct import MStruct
from hearthy.protocol.utils import Splitter
from hearthy.protocol.decoder import decode_packet

CALLBACK_PERIOD = 100 # ms
MAX_QUEUE = 1000

class Connection:
    __slots__ = ['p', '_s']
    """
    Represent a connection between two endpoints source and dest.
    Decodes packet in the connection
    """
    def __init__(self, source, dest):
        self.p = [source, dest]
        self._s = [Splitter(), Splitter()]

    def feed(self, who, buf):
        for atype, abuf in self._s[who].feed(buf):
            decoded = decode_packet(atype, abuf)
            yield decoded

    def __repr__(self):
        print('<Connection source={0!r} dest={1!r}'.format(
            self.p[0], self.p[1]))

def hcap_generate_logs(f):
    generator = hcapng.parse(f)
    header = next(generator)

    conns = {}

    for ts, event in generator:
        if isinstance(event, hcapng.EvNewConnection):
            conns[event.stream_id] = Connection(event.source, event.dest)
        elif event.stream_id in conns:
            if isinstance(event, hcapng.EvClose):
                yield (event.stream_id, ('close', ts))
                del conns[event.stream_id]
            elif isinstance(event, hcapng.EvData):
                try:
                    for packet in conns[event.stream_id].feed(event.who, event.data):
                        yield (event.stream_id, ('packet', packet, event.who, ts))
                except Exception as e:
                    del conns[event.stream_id]
                    yield (event.stream_id, ('exception', e))

class LogGenerationThread(threading.Thread):
    def __init__(self, fn):
        super().__init__()
        self._fn = fn
        self.queue = queue.Queue(MAX_QUEUE)

    def run(self):
        with open(self._fn, 'rb') as f:
            for event in hcap_generate_logs(f):
                self.queue.put(event, block=True)

class StreamView:
    def __init__(self):
        self._build_widgets()
        self._n_packets = 0

    def _build_widgets(self):
        parent = tkinter.Toplevel()
        parent.title('StreamView')

        tree = ttk.Treeview(parent, columns=('Name', 'Value', 'Time'))
        tree.heading('#0', text='Name', anchor='w')
        tree.heading('#1', text='Value', anchor='w')
        tree.heading('#2', text='Time', anchor='w')

        tree.column('#0', stretch=True, width=400)
        tree.column('#1', stretch=False, width=200)
        tree.column('#2', stretch=False, width=100)

        tree.tag_configure(0, background='#F0A57D')
        tree.tag_configure(1, background='#7DC8F0')

        vsb = ttk.Scrollbar(parent, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')

        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        self._tree = tree

    def _append_node(self, tree, node, key, value):
        if isinstance(value, str):
            tree.insert(node, 'end', text=key, value=(value, ''))
        elif isinstance(value, int):
            tree.insert(node, 'end', text=key, value=(value, ''))
        elif isinstance(value, list):
            subnode = tree.insert(node, 'end', text=key, value=('{0} Element{1}'.format(len(value), '' if len(value) == 1 else 's'), ''))
            for i, entry in enumerate(value):
                self._append_node(tree, subnode, '[{0}]'.format(i), entry)
        elif isinstance(value, MStruct):
            subnode = tree.insert(node, 'end', text=key, value=(value.__class__.__name__, ''))
            for slot in value.__slots__:
                if not hasattr(value, slot):
                    continue
                slotvalue = getattr(value, slot)

                self._append_node(tree, subnode, slot, slotvalue)

    def process_packet(self, packet, who, ts):
        node = self._tree.insert('', 'end',
                                 text='Packet {0}'.format(self._n_packets),
                                 value=(packet.__class__.__name__, '{0:0.2f}s'.format(ts/1000)),
                                 tags=(who,))
        self._n_packets += 1

        for slot in packet.__slots__:
            if not hasattr(packet, slot):
                continue
            value = getattr(packet, slot)
            self._append_node(self._tree, node, slot, value)

class Application(ttk.Frame):
    def __init__(self, fn, master=None):
        super().__init__(master)

        self._streams = {}
        self._list_dirty = False

        self._build_widgets(master)

        self.lgt = LogGenerationThread(fn)
        self.lgt.start()

    def _build_widgets(self, master):
        text = ttk.Label(text='TODO: add an actual main window')
        text.pack()

        b = ttk.Button(text='Quit', command=self.master.destroy)
        b.pack()
        self.pack(expand=True, fill='both')

    def process_events(self):
        try:
            self._process_events()
        except queue.Empty:
            pass
        self.master.after(CALLBACK_PERIOD, self.process_events)

    def _process_events(self):
        for i in range(100):
            stream_id, event = self.lgt.queue.get(block=False)
            stream = self._streams.get(stream_id, None)

            if event[0] == 'packet':
                if stream is None:
                    stream = self._streams[stream_id] = StreamView()
                stream.process_packet(event[1], event[2], event[3])

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('Usage: {0} <hcap file>'.format(sys.argv[0]))
        sys.exit(1)

    root = tkinter.Tk()
    root.wm_title('MainWindow')

    app = Application(sys.argv[1], master=root)

    app.process_events()
    root.mainloop()
