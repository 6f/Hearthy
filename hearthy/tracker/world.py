from hearthy import exceptions
from hearthy.protocol.enums import GameTag
from hearthy.protocol.utils import format_tag_value
from hearthy.tracker.entity import Entity, MutableEntity, MutableView

class WorldTransaction:
    def __init__(self, world, generation):
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
        self._generation = 0
        self._watchers = []

    def __contains__(self, eid):
        return eid in self._e

    def __getitem__(self, eid):
        e = self._e.get(eid, None)
        if e is None:
            raise exceptions.EntityNotFound(eid)
        return e

    def transaction(self):
        return WorldTransaction(self, self._generation)

    def _apply(self, transaction):
        # XXX: Remove all debug code
        print('== Transaction Start ==')
        for entity in transaction._e.values():
            if isinstance(entity, MutableView):
                for key, val in entity._tags.items():
                    oldval = entity._e[key]
                    if oldval:
                        print('{0} tag {1}:{2} {3} -> {4}'.format(
                            entity,
                            key,
                            GameTag.reverse.get(key, '?'),
                            format_tag_value(key, oldval),
                            format_tag_value(key, val)))
                    else:
                        print('{0} tag {1}:{2} (unset) -> {3}'.format(
                            entity,
                            key,
                            GameTag.reverse.get(key, '?'),
                            format_tag_value(key, val)))
                entity._e._tags.update(entity._tags)
            else:
                assert entity.id not in self
                print('Added new entity {0}'.format(entity))
                self._e[entity.id] = entity.freeze()
        print('== Transaction End ==')
