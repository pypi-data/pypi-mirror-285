class Class:
    self._symbolic = False

    def method(self, symbolic=None, values=None):
        if self._symbolic and values is not None:
            a, b, c = values.items()
        elif self._symbolic:
            pass
