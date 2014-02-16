class DecodeError(Exception):
    pass

class CardNotFound(Exception):
    pass

class EntityNotFound(Exception):
    def __init__(self, eid):
        super().__init__('Could not find entity with id={0}'.format(eid))

class UnexpectedEof(Exception):
    def __init__(self):
        super().__init__('Encountered an unepxected end of file')

class BufferFullException(Exception):
    pass
