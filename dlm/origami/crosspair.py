class CrossPair:
    """
    Represents a pair of crossovers that are adjacent in origami.

    Attributes:
        index (int): The index of the crossover pair.
        cross1 (Cross): The first crossover in the pair.
        cross2 (Cross): The second crossover in the pair.
        type (str): The type of the crossover pair.
    """

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

    @property
    def cross1(self):
        return self._cross1

    @property
    def cross2(self):
        return self._cross2

    @property
    def type(self):
        return self._type
