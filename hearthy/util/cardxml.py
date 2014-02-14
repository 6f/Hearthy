import os
import xml.etree.ElementTree as ET

class CardxmlException(Exception):
    pass


class Card:
    __slots__ = ['id', 'name']
    def __init__(self, id, name):
        self.id = id
        self.name = name

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
    if len(sys.argv) < 2:
        print('Usage: {0} <dir | file>'.format(sys.argv[0]))
        sys.exit(1)

    if os.path.isdir(sys.argv[1]):
        parse_cardxml_dir(sys.argv[1])
    else:
        parse_cardxml(sys.argv[1])
