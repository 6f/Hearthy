import tkinter
from tkinter import ttk

from hearthy.ui.tk.entitybrowser import EntityBrowser
from hearthy.ui.tk.streamlist import StreamList
from hearthy.ui.common import AsyncLogGenerator
from hearthy.datasource import hcapng

class Application(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(expand=True, fill='both')
        self._build_widgets()
        self._streams = StreamList(self._streams_frame)

    def _build_widgets(self):
        self._b_packets = ttk.Button(self, text='View Packets', command=self._on_log_view)
        self._b_entities = ttk.Button(self, text='Entity Browser', command=self._on_entity_browser)
        self._streams_frame = ttk.LabelFrame(self, text='Stream List')

        self._streams_frame.grid(columnspan=2, row=0, column=0, sticky='nsew')
        self._b_packets.grid(row=1, column=0, sticky='nsew')
        self._b_entities.grid(row=1, column=1, sticky='nsew')

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _on_entity_browser(self):
        self._streams.open_entity_browser()

    def _on_log_view(self):
        self._streams.open_stream_view()

    def process_event(self, stream_id, event):
        if event[0] == 'packet':
            self._streams.on_packet(stream_id, *event[1:])
        elif event[0] == 'create':
            self._streams.on_create(stream_id, *event[1:])
        elif event[0] == 'close':
            self._streams.on_close(stream_id, *event[1:])
        elif event[0] == 'basets':
            self._streams.on_basets(event[1]*1000)

if __name__ == '__main__':
    import sys
    import os

    if len(sys.argv) < 2:
        print('Usage: {0} <hcap file>'.format(sys.argv[0]))
        sys.exit(1)

    root = tkinter.Tk()
    root.geometry('800x300')
    root.wm_title('MainWindow')

    parser = hcapng.AsyncParser()
    log_generator = AsyncLogGenerator()
    
    app = Application(master=root)
    
    fd = os.open(sys.argv[1], os.O_NONBLOCK | os.O_RDONLY)

    def read_cb(fd, mask):
        buf = os.read(fd, 1024)
        
        if len(buf) == 0:
            # end of file (hopefully)
            root.tk.deletefilehandler(fd)
            return
        
        try:
            for ts, event in parser.feed_buf(buf):
                for packet_event in log_generator.process_event(ts, event):
                    app.process_event(*packet_event)
        except:
            root.tk.deletefilehandler(fd)
            raise

    root.tk.createfilehandler(fd, tkinter.READABLE, read_cb)
    root.mainloop()

    os.close(fd)
