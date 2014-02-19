import tkinter
from tkinter import ttk

from hearthy.protocol import utils
from hearthy.protocol.enums import GameTag
from hearthy.tracker.entity import MutableView

ALL_TAGS = sorted([x.capitalize() for x in GameTag.reverse.values()])

class EntityFilter:
    def __init__(self, filter_frame):
        self.tag = tkinter.StringVar()
        self.test = tkinter.StringVar()
        self.value = tkinter.StringVar()
        
        self.ctag = ttk.Combobox(filter_frame, textvariable=self.tag, state='readonly')
        self.ctag['values'] = ALL_TAGS
        self.ctag.bind('<<ComboboxSelected>>', self._on_tag_change)

        self.ftest = ttk.Combobox(filter_frame, textvariable=self.test, state='readonly')
        self.ftest['values'] = ('Exists', 'Not Exists', 'Equals', 'Not Equals')

        self.fvalue = ttk.Combobox(filter_frame, textvariable=self.value)

    def _on_tag_change(self, val):
        tagval = self.tag.get()
        numeric = GameTag.__dict__.get(tagval.upper(), None)

        if numeric is None:
            return

        enum = utils._gametag_to_enum.get(numeric, None)
        if enum is None:
            return

        self.fvalue['values'] = sorted([x.capitalize() for x in enum.reverse.values()])

    def set_grid_row(self, row):
        self.ctag.grid(row=row, column=0, sticky='nsew')
        self.ftest.grid(row=row, column=1, sticky='nsew')
        self.fvalue.grid(row=row, column=2, sticky='nsew')

class EntityTree:
    def __init__(self, container):
        self._build_widgets(container)
        self._world = None

    def _build_widgets(self, container):
        tree = ttk.Treeview(container, columns=('Info','Value'))
        tree.heading('#0', text='Name', anchor='w')
        tree.heading('#1', text='Info', anchor='w')
        tree.heading('#2', text='Value', anchor='w')

        vsb = ttk.Scrollbar(container, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')

        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        self._tree = tree

    def _add_entity(self, entity):
        name = 'Entity {0}'.format(entity.id)
        node = self._tree.insert('', 'end', str(entity.id), text=name,
                                 value=(str(entity), ''))

        pre = str(entity.id) + '.'
        for tag, value in entity._tags.items():
            self._tree.insert(node, 'end', pre + str(tag),
                              text=str(tag),
                              value=(GameTag.reverse.get(tag, ''),
                                     utils.format_tag_value(tag, value)))

    def _change_entity(self, eview):
        pre = str(eview.id) + '.'
        update_parent = False
        for tag, value in eview._tags.items():
            if tag < 0 or tag == 49 or tag == 50:
                update_parent = True
            if eview._e[tag] is None:
                # add tag
                self._tree.insert(str(eview.id), 'end', pre + str(tag),
                                  text=tag,
                                  value=(GameTag.reverse.get(tag, ''),
                                         utils.format_tag_value(tag, value)))
            else:
                # change tag
                self._tree.item(pre + str(tag),
                                value=(GameTag.reverse.get(tag, ''),
                                       utils.format_tag_value(tag, value)))

        if update_parent:
            self._tree.item(str(eview.id),
                            value=(str(eview), ''))

    def set_world(self, world):
        # clear tree
        dellist = list(self._tree.get_children())
        map(self._tree.delete, dellist)

        # rebuild tree
        for entity in world:
            self._add_entity(entity)

        self._world = world

    def apply_transaction(self, transaction):
        tree = self._tree

        for entity in transaction._e.values():
            if isinstance(entity, MutableView):
                # Entity Changes
                self._change_entity(entity)
            else:
                # New Entity
                self._add_entity(entity)
                
class EntityBrowser:
    def __init__(self):
        self._build_widgets()
        self._filters = []
        self.cb = None

    def _on_destroy(self):
        if self.cb is not None:
            self.cb(self, 'destroy')
        self._window.destroy()

    def _build_widgets(self):
        self._window = parent = tkinter.Toplevel()
        parent.protocol('WM_DELETE_WINDOW', self._on_destroy)

        browser_frame = ttk.Labelframe(parent, text='Entity Browser')
        browser_frame.grid(row=0, column=0, sticky='nsew')

        tree = EntityTree(browser_frame)
        
        filter_frame = ttk.Labelframe(parent, text='Entity Filter')
        filter_frame.grid(row=1, column=0, sticky='nsew')

        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

        b_add = ttk.Button(filter_frame, text='Add Filter', command=self._add_filter)
        b_add.grid(row=0, column=2, sticky='e')

        filter_frame.columnconfigure(0, weight=1)
        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(2, weight=1)

        self._tree = tree
        self._filter_frame = filter_frame
        self._b_add = b_add

    def _add_filter(self):
        efilter = EntityFilter(self._filter_frame)
        efilter.set_grid_row(len(self._filters))

        self._filters.append(efilter)
        self._b_add.grid(row=len(self._filters), column=2, sticky='e')

    def set_world(self, world):
        self._tree.set_world(world)

    def apply_transaction(self, transaction):
        self._tree.apply_transaction(transaction)
