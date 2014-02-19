import tkinter
from tkinter import ttk

from datetime import datetime

from hearthy.ui.tk.streamview import StreamView

class Stream:
    def __init__(self, stream_id, basets, start, source, dest):
        self.id = stream_id
        self.basets = basets
        self.source = source
        self.dest = dest
        self.packet_count = 0
        self.node = None
        self.status = 'open'
        self.start = start
        self.end = None
        self.packets = []

    def get_values(self):
        source = '{0}:{1}'.format(*self.source)
        dest = '{0}:{1}'.format(*self.dest)
        start = end = ''

        if self.start is not None:
            start = datetime.fromtimestamp((self.start+self.basets)//1000).strftime('%Y.%m.%d %H:%M:%S')
        if self.end is not None:
            end = datetime.fromtimestamp((self.end+self.basets)//1000).strftime('%Y.%m.%d %H:%M:%S')
            
        return (self.packet_count, source, dest,
                start, end, self.status)

class StreamList:
    def __init__(self, container):
        self._streams = {}
        self._container = container
        self._basets = 0
        self._build_widgets()
        self._stream_views = {}

    def _streamview_cb(self, sv, event):
        if event == 'destroy':
            for l in self._stream_views.values():
                if sv in l:
                    l.remove(sv)

    def open_stream_view(self):
        sid = self.get_selected()
        if sid is None:
            return
        
        stream = self._streams[sid]
        sv = StreamView(stream.id, stream.start)
        sv.cb = self._streamview_cb
        
        l = self._stream_views.get(sid, None)
        if l is None:
            l = self._stream_views[sid] = []
        l.append(sv)

        for packet in stream.packets:
            sv.process_packet(*packet)

    def get_selected(self):
        s = self._view.selection()
        if s:
            sid = int(self._view.item(s[0], 'text').split(' ')[1])
            return sid

    def _build_widgets(self):
        view = ttk.Treeview(self._container,
                            columns=('n', 'Source', 'Dest', 'Start', 'End', 'Status'))
        view.heading('#0', text='Name', anchor='w')
        view.heading('#1', text='N', anchor='w')
        view.heading('#2', text='Source', anchor='w')
        view.heading('#3', text='Dest', anchor='w')
        view.heading('#4', text='Start', anchor='w')
        view.heading('#5', text='End', anchor='w')
        view.heading('#6', text='Status', anchor='w')
        
        view.pack(fill='both', expand=True)

        self._view = view

    def on_create(self, stream_id, source, dest, ts):
        assert stream_id not in self._streams
        self._streams[stream_id] = Stream(stream_id, self._basets, ts, source, dest)

    def on_basets(self, ts):
        self._basets = ts

    def on_packet(self, stream_id, packet, who, ts):
        stream = self._streams.get(stream_id, None)
        assert stream is not None
        stream.packet_count += 1
        stream.packets.append((packet, who, ts))

        if stream.node is None:
            stream.node = self._view.insert('', 'end',
                                            text='Stream {0}'.format(stream.id),
                                            values=stream.get_values())
        else:
            self._view.item(stream.node, values=stream.get_values())

        for sv in self._stream_views.get(stream_id, []):
            sv.process_packet(packet, who, ts)

    def on_close(self, stream_id, ts):
        stream = self._streams.get(stream_id, None)
        assert stream is not None
        stream.status = 'closed'
        stream.end = ts
        if stream.node is not None:
            self._view.item(stream.node, values=stream.get_values())
