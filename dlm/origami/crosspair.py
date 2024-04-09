class CrossPair:
    def __init__(self, index, cross1, cross2):
        self._index = index
        self._cross1 = cross1
        self._cross2 = cross2
        self._type = self.cross1.type

    ### Getters ###
    @property
    def index(self):
        return self._index
    @property
    def ind(self):
        return self._index
    # end def

    @property
    def cross1(self):
        return self._cross1
    # end def

    @property
    def cross2(self):
        return self._cross2
    # end def

    @property
    def type(self):
        return self._type
    # end def
