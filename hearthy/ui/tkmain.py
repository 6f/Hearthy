import queue

import tkinter
from tkinter import ttk

from hearthy.ui.tk.streamlist import StreamList
from hearthy.ui.tk.streamview import StreamView
from hearthy.ui.common import LogGenerationThread

CALLBACK_PERIOD = 100 # ms
MAX_QUEUE = 1000

class Application(ttk.Frame):
    def __init__(self, fn, master=None):
        super().__init__(master)
        self.pack(expand=True, fill='both')
        self._build_widgets()
        self._streams = StreamList(self._streams_frame)

        self._lgt = LogGenerationThread(fn)
        self._lgt.start()

    def _build_widgets(self):
        self._b_packets = ttk.Button(self, text='View Packets', command=self._on_log_view)
        self._streams_frame = ttk.LabelFrame(self, text='Stream List')

        self._streams_frame.pack(expand=True, fill='both')
        self._b_packets.pack()

    def _on_log_view(self):
        self._streams.open_stream_view()

    def process_events(self):
        try:
            self._process_events()
        except queue.Empty:
            pass
        self.master.after(CALLBACK_PERIOD, self.process_events)

    def _process_events(self):
        for i in range(100):
            stream_id, event = self._lgt.queue.get(block=False)

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

    if len(sys.argv) < 2:
        print('Usage: {0} <hcap file>'.format(sys.argv[0]))
        sys.exit(1)

    root = tkinter.Tk()
    root.geometry('500x500')
    root.wm_title('MainWindow')

    app = Application(sys.argv[1], master=root)
    app.process_events()
    
    root.mainloop()
