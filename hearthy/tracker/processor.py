import logging
from hearthy.protocol import mtypes
from hearthy.protocol.enums import GameTag
from hearthy.tracker.world import World
from hearthy.protocol.utils import format_tag_value
from hearthy.tracker.entity import Entity, TAG_CUSTOM_NAME, TAG_POWER_NAME

logger = logging.getLogger(__name__)

class Processor:
    def __init__(self):
        self._world = World()
        self.logger = logger

    def process(self, who, what):
        with self._world.transaction() as t:
            self._process(who, what, t)

    def _process(self, who, what, t):
        if isinstance(what, mtypes.StartGameState):
            self._process_create_game(what, t)
        elif isinstance(what, mtypes.PowerHistory):
            for power in what.List:
                self._process_power(power, t)
        else:
            self.logger.info('Ignoring packet of type {0}'.format(what.__class__.__name__))

    def _process_create_game(self, what, t):
        eid, taglist = (what.GameEntity.Id,
                        [(t.Name, t.Value) for t in what.GameEntity.Tags])
        if eid in t:
            print('INFO: Game Entity already exists, ignoring "create game" event')
            return

        logging.debug('Got game entity: {0!r}'.format(what.GameEntity))
        taglist.append((TAG_CUSTOM_NAME, 'TheGame'))
        t.add(Entity(eid, taglist))

        for player in what.Players:
            eid, taglist = (player.Entity.Id,
                            [(t.Name, t.Value) for t in player.Entity.Tags])

            # TODO: are we interested in the battlenet id?
            logging.debug('Found Player {0}: {1!r}'.format(player.Id, player))
            taglist.append((TAG_CUSTOM_NAME, 'Player{0}'.format(player.Id)))
            t.add(Entity(eid, taglist))

    def _process_power(self, power, t):
        if hasattr(power, 'FullEntity'):
            e = power.FullEntity
            taglist = [(e.Name, e.Value) for e in e.Tags]
            taglist.append((TAG_POWER_NAME, e.Name))
            new_entity = Entity(e.Entity, taglist)
            t.add(new_entity)

            # logging
            logger.info('Adding new entity: {0}'.format(new_entity))
            logger.debug('With tags: \n' + '\n'.join(
                '\ttag {0}:{1} {2}'.format(tag_id,
                                          GameTag.reverse.get(tag_id, '?'),
                                          format_tag_value(tag_id, tag_val))
                for tag_id, tag_val in taglist))
        if hasattr(power, 'ShowEntity'):
            e = power.ShowEntity
            mut = t.get_mutable(e.Entity)
            mut[TAG_POWER_NAME] = e.Name

            for tag in e.Tags:
                mut[tag.Name] = tag.Value

            logger.info('Revealing entity: {0}'.format(mut))
        if hasattr(power, 'HideEntity'):
            pass
        if hasattr(power, 'TagChange'):
            change = power.TagChange
            e = t.get_mutable(change.Entity)

            logger.info('Tag change for {0}: {1} from {2} to {3}'.format(
                Entity.__str__(e),
                GameTag.reverse.get(change.Tag, change.Tag),
                format_tag_value(change.Tag, e[change.Tag]) if e[change.Tag] is not None else '(unset)',
                format_tag_value(change.Tag, change.Value)))

            e[change.Tag] = change.Value
        if hasattr(power, 'CreateGame'):
            self._process_create_game(power.CreateGame, t)
