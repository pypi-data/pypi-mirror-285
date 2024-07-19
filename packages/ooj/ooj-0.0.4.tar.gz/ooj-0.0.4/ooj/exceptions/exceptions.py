class NotSerializableException(Exception):
    def __init__(self):
        super().__init__('Cannot serialize or deserialize object')


class CyclicFieldError(Exception):
    def __init__(self):
        super().__init__('Cyclic field detected')