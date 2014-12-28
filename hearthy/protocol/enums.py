#!/usr/bin/env python3

def _enum(name, definition):
    next_id = 0
    mapping = []
    for entry in definition:
        if isinstance(entry, tuple):
            next_id = entry[1] + 1
            mapping.append(entry)
        else:
            mapping.append((entry, next_id))
            next_id += 1
    forward = dict(mapping)
    assert 'reverse' not in forward
    forward['reverse'] = dict((v,k) for k,v in forward.items())
    return type(name, (), forward)

GameTag = _enum('GameTag', [
    ('IGNORE_DAMAGE',                       1),
    ('MISSION_EVENT',                       6),
    ('TIMEOUT',                             7),
    ('TURN_START',                          8),
    ('TURN_TIMER_SLUSH',                    9),
    ('PREMIUM',                             12),
    ('GOLD_REWARD_STATE',                   13),
    ('PLAYSTATE',                           17),
    ('LAST_AFFECTED_BY',                    18),
    ('STEP',                                19),
    ('TURN',                                20),
    ('FATIGUE',                             22),
    ('CURRENT_PLAYER',                      23),
    ('FIRST_PLAYER',                        24),
    ('RESOURCES_USED',                      25),
    ('RESOURCES',                           26),
    ('HERO_ENTITY',                         27),
    ('MAXHANDSIZE',                         28),
    ('STARTHANDSIZE',                       29),
    ('PLAYER_ID',                           30),
    ('TEAM_ID',                             31),
    ('TRIGGER_VISUAL',                      32),
    ('RECENTLY_ARRIVED',                    33),
    ('PROTECTING',                          34),
    ('PROTECTED',                           35),
    ('DEFENDING',                           36),
    ('PROPOSED_DEFENDER',                   37),
    ('ATTACKING',                           38),
    ('PROPOSED_ATTACKER',                   39),
    ('ATTACHED',                            40),
    ('EXHAUSTED',                           43),
    ('DAMAGE',                              44),
    ('HEALTH',                              45),
    ('ATK',                                 47),
    ('COST',                                48),
    ('ZONE',                                49),
    ('CONTROLLER',                          50),
    ('OWNER',                               51),
    ('DEFINITION',                          52),
    ('ENTITY_ID',                           53),
    ('ELITE',                               114),
    ('MAXRESOURCES',                        176),
    ('CARD_SET',                            183),
    ('CARDTEXT_INHAND',                     184),
    ('CARDNAME',                            185),
    ('CARD_ID',                             186),
    ('DURABILITY',                          187),
    ('SILENCED',                            188),
    ('WINDFURY',                            189),
    ('TAUNT',                               190),
    ('STEALTH',                             191),
    ('SPELLPOWER',                          192),
    ('DIVINE_SHIELD',                       194),
    ('CHARGE',                              197),
    ('NEXT_STEP',                           198),
    ('CLASS',                               199),
    ('CARDRACE',                            200),
    ('FACTION',                             201),
    ('CARDTYPE',                            202),
    ('RARITY',                              203),
    ('STATE',                               204),
    ('SUMMONED',                            205),
    ('FREEZE',                              208),
    ('ENRAGED',                             212),
    ('RECALL',                              215),
    ('LOYALTY',                             216),
    ('DEATHRATTLE',                         217),
    ('BATTLECRY',                           218),
    ('SECRET',                              219),
    ('COMBO',                               220),
    ('CANT_HEAL',                           221),
    ('CANT_DAMAGE',                         222),
    ('CANT_SET_ASIDE',                      223),
    ('CANT_REMOVE_FROM_GAME',               224),
    ('CANT_READY',                          225),
    ('CANT_EXHAUST',                        226),
    ('CANT_ATTACK',                         227),
    ('CANT_TARGET',                         228),
    ('CANT_DESTROY',                        229),
    ('CANT_DISCARD',                        230),
    ('CANT_PLAY',                           231),
    ('CANT_DRAW',                           232),
    ('INCOMING_HEALING_MULTIPLIER',         233),
    ('INCOMING_HEALING_ADJUSTMENT',         234),
    ('INCOMING_HEALING_CAP',                235),
    ('INCOMING_DAMAGE_MULTIPLIER',          236),
    ('INCOMING_DAMAGE_ADJUSTMENT',          237),
    ('INCOMING_DAMAGE_CAP',                 238),
    ('CANT_BE_HEALED',                      239),
    ('CANT_BE_DAMAGED',                     240),
    ('CANT_BE_SET_ASIDE',                   241),
    ('CANT_BE_REMOVED_FROM_GAME',           242),
    ('CANT_BE_READIED',                     243),
    ('CANT_BE_EXHAUSTED',                   244),
    ('CANT_BE_ATTACKED',                    245),
    ('CANT_BE_TARGETED',                    246),
    ('CANT_BE_DESTROYED',                   247),
    ('CANT_BE_SUMMONING_SICK',              253),
    ('FROZEN',                              260),
    ('JUST_PLAYED',                         261),
    ('LINKEDCARD',                          262),
    ('ZONE_POSITION',                       263),
    ('CANT_BE_FROZEN',                      264),
    ('COMBO_ACTIVE',                        266),
    ('CARD_TARGET',                         267),
    ('NUM_CARDS_PLAYED_THIS_TURN',          269),
    ('CANT_BE_TARGETED_BY_OPPONENTS',       270),
    ('NUM_TURNS_IN_PLAY',                   271),
    ('NUM_TURNS_LEFT',                      272),
    ('OUTGOING_DAMAGE_CAP',                 273),
    ('OUTGOING_DAMAGE_ADJUSTMENT',          274),
    ('OUTGOING_DAMAGE_MULTIPLIER',          275),
    ('OUTGOING_HEALING_CAP',                276),
    ('OUTGOING_HEALING_ADJUSTMENT',         277),
    ('OUTGOING_HEALING_MULTIPLIER',         278),
    ('INCOMING_ABILITY_DAMAGE_ADJUSTMENT',  279),
    ('INCOMING_COMBAT_DAMAGE_ADJUSTMENT',   280),
    ('OUTGOING_ABILITY_DAMAGE_ADJUSTMENT',  281),
    ('OUTGOING_COMBAT_DAMAGE_ADJUSTMENT',   282),
    ('OUTGOING_ABILITY_DAMAGE_MULTIPLIER',  283),
    ('OUTGOING_ABILITY_DAMAGE_CAP',         284),
    ('INCOMING_ABILITY_DAMAGE_MULTIPLIER',  285),
    ('INCOMING_ABILITY_DAMAGE_CAP',         286),
    ('OUTGOING_COMBAT_DAMAGE_MULTIPLIER',   287),
    ('OUTGOING_COMBAT_DAMAGE_CAP',          288),
    ('INCOMING_COMBAT_DAMAGE_MULTIPLIER',   289),
    ('INCOMING_COMBAT_DAMAGE_CAP',          290),
    ('CURRENT_SPELLPOWER',                  291),
    ('ARMOR',                               292),
    ('MORPH',                               293),
    ('IS_MORPHED',                          294),
    ('TEMP_RESOURCES',                      295),
    ('RECALL_OWED',                         296),
    ('NUM_ATTACKS_THIS_TURN',               297),
    ('NEXT_ALLY_BUFF',                      302),
    ('MAGNET',                              303),
    ('FIRST_CARD_PLAYED_THIS_TURN',         304),
    ('MULLIGAN_STATE',                      305),
    ('TAUNT_READY',                         306),
    ('STEALTH_READY',                       307),
    ('CHARGE_READY',                        308),
    ('CANT_BE_TARGETED_BY_ABILITIES',       311),
    ('SHOULDEXITCOMBAT',                    312),
    ('CREATOR',                             313),
    ('CANT_BE_DISPELLED',                   314),
    ('PARENT_CARD',                         316),
    ('NUM_MINIONS_PLAYED_THIS_TURN',        317),
    ('PREDAMAGE',                           318),
    ('TARGETING_ARROW_TEXT',                325),
    ('ENCHANTMENT_BIRTH_VISUAL',            330),
    ('ENCHANTMENT_IDLE_VISUAL',             331),
    ('CANT_BE_TARGETED_BY_HERO_POWERS',     332),
    ('HEALTH_MINIMUM',                      337),
    ('SILENCE',                             339),
    ('COUNTER',                             340),
    ('ARTISTNAME',                          342),
    ('HAND_REVEALED',                       348),
    ('ADJACENT_BUFF',                       350),
    ('FLAVORTEXT',                          351),
    ('FORCED_PLAY',                         352),
    ('LOW_HEALTH_THRESHOLD',                353),
    ('IGNORE_DAMAGE_OFF',                   354),
    ('SPELLPOWER_DOUBLE',                   356),
    ('HEALING_DOUBLE',                      357),
    ('NUM_OPTIONS_PLAYED_THIS_TURN',        358),
    ('NUM_OPTIONS',                         359),
    ('TO_BE_DESTROYED',                     360),
    ('AURA',                                362),
    ('POISONOUS',                           363),
    ('HOW_TO_EARN',                         364),
    ('HOW_TO_EARN_GOLDEN',                  365),
    ('TAG_HERO_POWER_DOUBLE',               366),
    ('TAG_AI_MUST_PLAY',                    367),
    ('NUM_MINIONS_PLAYER_KILLED_THIS_TURN', 368),
    ('NUM_MINIONS_KILLED_THIS_TURN',        369),
    ('AFFECTED_BY_SPELL_POWER',             370),
    ('EXTRA_DEATHRATTLES',                  371),
    ('START_WITH_1_HEALTH',                 372),
    ('IMMUNE_WHILE_ATTACKING',              373),
    ('MULTIPLY_HERO_DAMAGE',                374),
    ('MULTIPLY_BUFF_VALUE',                 375),
    ('CUSTOM_KEYWORD_EFFECT',               376),
    ('TOPDECK',                             377),
    ('CANT_BE_TARGETED_BY_BATTLECRIES',     379),
    ('OVERKILL',                            380),
    ('DEATHRATTLE_SENDS_BACK_TO_DECK',      382),
    ('STEADY_SHOT_CAN_TARGET',              383),
    ('DISPLAYED_CREATOR',                   385),
    ('POWERED_UP',                          386),
    ('SPARE_PART',                          388),
    ('FORGETFUL',                           389),
    ('CAN_SUMMON_MAXPLUSONE_MINION',        390)
])

MetaType = _enum('MetaType', [
    ('TARGET',  1),
    ('DAMAGE',  2),
    ('HEALING', 3)
])

CardSet = _enum('CardSet', [
    ('INVALID',        0),
    ('TEST_TEMPORARY', 1),
    ('CORE',           2),
    ('EXPERT1',        3),
    ('REWARD',         4),
    ('MISSIONS',       5),
    ('DEMO',           6),
    ('NONE',           7),
    ('CHEAT',          8),
    ('BLANK',          9),
    ('DEBUG_SP',       10),
    ('PROMO',          11),
    ('FP1',            12),
    ('PE1',            13),
    ('FP2',            14),
    ('PE2',            15),
    ('CREDITS',        16)
])

BeginPlayingMode = _enum('BeginPlayingMode', [
    ('COUNTDOWN', 1),
    ('READY',     2)
])

CardRarity = _enum('CardRarity', [
    'INVALID', 'COMMON', 'FREE', 'RARE', 'EPIC', 'LEGENDARY'
])

Step = _enum('Step', [
    'INVALID', 'BEGIN_FIRST', 'BEGIN_SHUFFLE', 'BEGIN_DRAW', 'BEGIN_MULLIGAN',
    'MAIN_BEGIN', 'MAIN_READY', 'MAIN_RESOURCE', 'MAIN_DRAW', 'MAIN_START',
    'MAIN_ACTION', 'MAIN_COMBAT', 'MAIN_END', 'MAIN_NEXT', 'FINAL_WRAPUP',
    'FINAL_GAMEOVER', 'MAIN_CLEANUP', 'MAIN_START_TRIGGERS'
])

Zone = _enum('Zone', [
    'INVALID', 'PLAY', 'DECK', 'HAND', 'GRAVEYARD', 'REMOVEDFROMGAME',
    'SETASIDE', 'SECRET'
])

CardType = _enum('CardType', [
    'INVALID', 'GAME', 'PLAYER', 'HERO', 'MINION', 'ABILITY', 'ENCHANTMENT',
    'WEAPON', 'ITEM', 'TOKEN', 'HERO_POWER'
])

PlayState = _enum('PlayState', [
    'INVALID', 'PLAYING', 'WINNING', 'LOSING', 'WON', 'LOST', 'TIED',
    'DISCONNECTED', 'QUIT'
])

MulliganState = _enum('MulliganState', [
    'INVALID', 'INPUT', 'DEALING', 'WAITING', 'DONE'
])

PowSubType = _enum('PowSubType', [
    ('ATTACK',    1),
    ('CONTINOUS', 2),
    ('POWER',     3),
    ('SCRIPT',    4),
    ('TRIGGER',   5),
    ('DEATHS',    6),
    ('PLAY',      7),
    ('FATIGUE',   8)
])

PacketType = _enum('PacketType', [
    ('GET_GAME_STATE',    1),
    ('CHOOSE_OPTION',     2),
    ('CHOOSE_ENTITIES',   3),
    ('PRE_CAST',          4),
    ('DEBUG_MESSAGE',     5),
    ('CLIENT_PACKET',     6),
    ('START_GAME_STATE',  7),
    ('FINISH_GAME_STATE', 8),
    ('TURN_TIMER',        9),
    ('NACK_OPTION',       10),
    ('GIVE_UP',           11),
    ('GAME_CANCELLED',    12),
    ('FORCED_ENTITY_CHOICE', 13),
    ('ALL_OPTIONS',       14),
    ('USER_UI',           15),
    ('GAME_SETUP',        16),
    ('ENTITY_CHOICE',     17),
    ('PRE_LOAD',          18),
    ('POWER_HISTORY',     19),
    ('NOTIFICATION',      21),
    ('SPECTATOR_HANDSHAKE', 22),
    ('SERVER_RESULT', 23),
    ('SPECTATOR_NOTIFY', 24),
    ('INVITE_TO_SPECTATE', 25),
    ('REMOVE_SPECTATORS', 26),
    # GAP
    ('AUTO_LOGIN',       103),
    ('BEGIN_PLAYING',    113),
    ('DEBUG_CONSOLE_COMMAND', 123),
    ('DEBUG_CONSOLE_RESPONSE', 124),
    ('GAME_STARTING',    114),
    ('PING', 115),
    ('PONG', 116),
    ('AURORA_HANDSHAKE', 168),
])

TagState = _enum('TagState', ['INVALID', 'LOADING', 'RUNNING', 'COMPLETE'])

Faction = _enum('Faction', ['INVALID', 'HORDE', 'ALLIANCE', 'NEUTRAL'])

Race = _enum('Race', [
    'INVALID', 'BLOODELF', 'DRAENEI', 'DWARF', 'GNOME', 'GOBLIN', 'HUMAN',
    'NIGHTELF', 'ORC', 'TAUREN', 'TROLL', 'UNDEAD', 'WORGEN', 'GOBLIN2',
    'MURLOC', 'DEMON', 'SCOURGE', 'MECHANICAL', 'ELEMENTAL', 'OGRE', 'PET',
    'TOTEM', 'NERUBIAN', 'PIRATE', 'DRAGON'
])

# Enum for mtypes.Option.Type
OptionType = _enum('OptionType', [('PASS', 1), 'END_TURN', 'POWER'])

GoldRewardState = _enum('GoldRewardState', [
    'INVALID', 'ELIGIBLE', 'WRONG_GAME_TYPE', 'ALREADY_CAPPED', 'BAD_RATING',
    'SHORT_GAME'
])
