
class Helix:
    def __init__(self, index, nucs):
        self._index = index
        self._nucs = nucs
        self._domains = []

    def test(self):
        print(str(self.ind)+'\t'+str([dom.ind for dom in self.domains]))
        
    def __str__(self):
        result = 'Helix '+str(self.ind)
        return result

    ### Getters ###
    @property
    def ind(self):
        return self._index
    # end def

    @property
    def nucs(self):
        return self._nucs
    # end def

    @property
    def domains(self):
        return self._domains
    # end def
