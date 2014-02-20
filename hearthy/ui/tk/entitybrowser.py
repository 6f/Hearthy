import tkinter
from tkinter import ttk

from hearthy.protocol import utils
from hearthy.protocol.enums import GameTag
from hearthy.tracker.entity import MutableView

ALL_TAGS = sorted([x.capitalize() for x in GameTag.reverse.values()])

class EntityFilter(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.tag = tkinter.StringVar()
        self.test = tkinter.StringVar()
        self.value = tkinter.StringVar()

        ctag = ttk.Combobox(self, textvariable=self.tag, state='readonly')
        ctag['values'] = ALL_TAGS
        ctag.bind('<<ComboboxSelected>>', self._on_tag_change)

        ftest = ttk.Combobox(self, textvariable=self.test, state='readonly')
        ftest['values'] = ('Exists', 'Not Exists', 'Equals', 'Not Equals')

        fvalue = ttk.Combobox(self, textvariable=self.value)
        b_remove = ttk.Button(self, text='Remove', command=self._on_remove)

        ctag.grid(row=0, column=0, sticky='nsew')
        ftest.grid(row=0, column=1, sticky='nsew')
        fvalue.grid(row=0, column=2, sticky='nsew')
        b_remove.grid(row=0, column=3, sticky='nsew')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self._fvalue = fvalue

        self.cb = None

    def get_filter_string(self):
        tag = self.tag.get()
        test = self.test.get()
        value = self.value.get()

        tag = GameTag.__dict__.get(tag.upper(), tag)
        try:
            tag = int(tag)
        except ValueError:
            print('Err: {0!r} is not numeric'.format(tag))
            return

        if test == 'Exists':
            return '(x[{0}] is not None)'.format(tag)
        elif test == 'Not Exists':
            return '(x[{0}] is None)'.format(tag)

        enum = utils._gametag_to_enum.get(tag, None)
        if enum is not None:
            value = enum.__dict__.get(value.upper(), value)

        try:
            value = int(value)
        except ValueError:
            print('Err: {0!r} is not numeric'.format(value))
            return

        if test == 'Equals':
            return '(x[{0}] == {1})'.format(tag, value)
        elif test == 'Not Equals':
            return '(x[{0}] != {1})'.format(tag, value)

    def _on_remove(self):
        if self.cb is not None:
            self.cb(self, 'remove')
    
    def _on_tag_change(self, val):
        tagval = self.tag.get()
        numeric = GameTag.__dict__.get(tagval.upper(), None)

        if numeric is None:
            return

        enum = utils._gametag_to_enum.get(numeric, None)
        if enum is None:
            return

        self._fvalue['values'] = sorted([x.capitalize() for x in enum.reverse.values()])

class EntityTree:
    def __init__(self, container):
        self._build_widgets(container)
        self._world = None
        self._filter_fun = lambda x:True

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

        
        in_tree = self._tree.exists(str(eview.id))
        does_pass = self._filter_fun(eview)

        if not does_pass:
            if in_tree:
                self._tree.delete(str(eview.id))
            return
        else:
            if not in_tree:
                self._add_entity(eview._e)

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

    def set_filter(self, fun):
        self._filter_fun = fun
        if self._world is not None:
            self.set_world(self._world)

    def set_world(self, world):
        # clear tree
        dellist = list(self._tree.get_children())
        for item in dellist:
            self._tree.delete(item)

        # rebuild tree
        for entity in world:
            if self._filter_fun(entity):
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
                if self._filter_fun(entity):
                    self._add_entity(entity)

class EntityBrowser:
    def __init__(self):
        self._build_widgets()
        self._filters = []
        self.cb = None
        self._f = lambda x:True

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

        button_frame = ttk.Frame(filter_frame)
        button_frame.pack(fill='x')
        
        b_apply = ttk.Button(button_frame, text='Apply Filter', command=self._apply_filter)
        b_apply.pack(side='left', expand=True, fill='x')

        b_add = ttk.Button(button_frame, text='Add Filter', command=self._add_filter)
        b_add.pack(side='left', expand=True, fill='x')

        self._tree = tree
        self._filter_frame = filter_frame
        self._button_frame = button_frame

    def _apply_filter(self):
        full = ' and '.join(filter(None, [ef.get_filter_string() for ef in self._filters]))
        if full:
            f = eval('lambda x: ' + full)
        else:
            f = lambda x:True
        self._tree.set_filter(f)
        
    def _remove_filter(self, ef, event):
        self._filters.remove(ef)
        ef.destroy()

    def _add_filter(self):
        efilter = EntityFilter(self._filter_frame)
        efilter.pack(expand=True, fill='x')
        efilter.cb = self._remove_filter

        self._filters.append(efilter)
        self._button_frame.pack_forget()
        self._button_frame.pack(fill='x')

    def set_world(self, world):
        self._tree.set_world(world)

    def apply_transaction(self, transaction):
        self._tree.apply_transaction(transaction)
