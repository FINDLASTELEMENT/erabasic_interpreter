class RandomList:
    def __init__(self):
        self._container = []

    def __getitem__(self, item):
        return self._container[item]

    def __setitem__(self, key, value):
        if len(self._container) <= value:
            self._container += [0 for _ in range(key - len(self._container) + 1)]
        self._container[key] = value

    def __len__(self):
        return len(self._container)
