import os
import xml.etree.ElementTree as ET

class CardxmlException(Exception):
    pass

class TagMismatch(CardxmlException):
    def __init__(self, expected, found):
        CardxmlException.__init__(self, 'Expected tag {0} but found tag {1}'.format(expected, found))

class Card:
    __slots__ = ['id', 'name']
    def __init__(self, id, name):
        self.id = id
        self.name = name

def assert_tag(el, tag_name):
    if el.tag != tag_name:
        raise TagMismatch(tag_name, el.tag)

def parse_carddefs(name):
    tree = ET.parse(name)
    root = tree.getroot()

    assert_tag(root, 'CardDefs')
    cards = []

    for el_entity in root:
        assert_tag(el_entity, 'Entity')
        card_id = el_entity.get('CardID')

        if card_id is None:
            raise CardxmlExcpetion('Got entity without CardID attribute')

        for el_tag in el_entity:
            if el_tag.tag == 'Tag' and el_tag.get('enumID') == '185':
                cards.append(Card(card_id, el_tag.text))
                break

    return cards

def parse_cardxml(name):
    tree = ET.parse(name)
    root = tree.getroot()

    if root.tag != 'Entity':
        raise CardxmlException('Expected tag {0} but got {1}'.format('Entity', root.tag))

    cardid = root.get('CardID')
    if cardid is None:
        raise CardxmlException('Entity tag has no CardID attribute')

    cardname = None

    for element in root:
        tag = element.tag
        if tag == 'Tag':
            name = element.get('name')
            if name == 'CardName':
                cardname_el = element.find('enUS')
                if cardname_el is None:
                    raise CardxmlException('No "enUS" child find in "CardName" tag')
                cardname = cardname_el.text

    if cardname is None:
        raise Exception('Could not find the cardname')

    return Card(cardid, cardname)

def write_db(cards, f):
    print('_cards = [', file=f)
    for card in cards:
        print('    ({0!r},{1!r}),'.format(card.id, card.name), file=f)
    print(']', file=f)

def parse_cardxml_dir(dirname):
    l = []
    for name in os.listdir(dirname):
        # Sanity check
        if name.startswith('.'):
            print('Skipping {0}'.format(name))
            continue

        fullname = os.path.join(dirname, name)
        print('Parsing {0}'.format(fullname))

        l.append(parse_cardxml(fullname))
    return l

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print('Usage: {0} <dir | file> outfile'.format(sys.argv[0]))
        sys.exit(1)

    cards = []
    if os.path.isdir(sys.argv[1]):
        cards = parse_cardxml_dir(sys.argv[1])
    else:
        cards = parse_carddefs(sys.argv[1])

    write_db(cards, open(sys.argv[2], 'w'))
