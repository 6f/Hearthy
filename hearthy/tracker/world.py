from hearthy import exceptions
from hearthy.protocol.enums import GameTag
from hearthy.protocol.utils import format_tag_value
from hearthy.tracker.entity import Entity, MutableEntity, MutableView

class WorldTransaction:
    def __init__(self, world):
        self._world = world
        self._e = {}

    def add(self, entity):
        if isinstance(entity, Entity):
            assert entity.id not in self

            # New entities may be modified until transaction
            # completes
            entity.__class__ = MutableEntity

        self._e[entity.id] = entity

    def __contains__(self, eid):
        return eid in self._e or eid in self._world

    def get_mutable(self, eid):
        e = self._e.get(eid, None)
        if e is None:
            e = self._e[eid] = MutableView(self._world[eid])
        return e

    def __getitem__(self, eid):
        e = self._e.get(eid, None)
        if e is None:
            return self._world[eid]
        return e

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None and exc_value is None and traceback is None:
            # TODO: overkill checking all three?
            self._world._apply(self)

class World:
    """
    Container for all in-game entities.
    """
    def __init__(self):
        self._e = {}
        self._watchers = []
        self.cb = None

    def __contains__(self, eid):
        return eid in self._e

    def __getitem__(self, eid):
        e = self._e.get(eid, None)
        if e is None:
            raise exceptions.EntityNotFound(eid)
        return e

    def __iter__(self):
        for entity in self._e.values():
            yield entity

    def transaction(self):
        return WorldTransaction(self)

    def _apply(self, transaction):
        self.cb(self, 'pre_apply', transaction)
        
        for entity in transaction._e.values():
            if GameTag.TURN in entity._tags:
                print("== Turn {0} ==".format(entity._tags[GameTag.TURN]))

            if isinstance(entity, MutableView):
                print('{0}'.format(entity))
                entity._e._tags.update(entity._tags)
            else:
                assert entity.id not in self
                print('Added new entity {0}'.format(entity))
                self._e[entity.id] = entity.freeze()
