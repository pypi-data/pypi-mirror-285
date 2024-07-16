class DummyManager:

    def __init__(self):
        pass

    @staticmethod
    def Lock():
        return None

    @staticmethod
    def dict():
        return {}

    @staticmethod
    def Value(arg, value):
        return DummyValue(value)

    @staticmethod
    def Queue():
        return DummyQueue()


class DummyQueue:
    def __init__(self):
        self._queue = []

    def put(self, item):
        self._queue.append(item)

    def get(self):
        if len(self._queue) == 0:
            return None
        return self._queue.pop(0)

    def empty(self):
        return len(self._queue) == 0


class DummyValue:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
