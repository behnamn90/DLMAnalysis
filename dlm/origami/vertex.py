
class Vertex:
    def __init__(self, domain3p, domain5p):
        # all of the following are staple polarities
        self._domain5p, self._domain3p = domain5p, domain3p
        self._type = self.set_type() # (e)dge, (s)eam , (b)ody ! needs domain_is_at_edge and domain_is_at_seam

    def __eq__(self, other):
        if isinstance(other, Vertex):
            if self.n3p == other.n3p and self.n5p == other.n5p:
                return True
            else:
                return False
        return False

    def __str__(self):
        result = 'Vertex ' + str(self.ind) + ': '
        #result += 'dom3p: '+str(self.domain3p.ind)+ '(' +str(self.domain3p.n1)+ '->' +str(self.domain3p.n2)+ ') '
        #result += 'dom5p: '+str(self.domain5p.ind)+ '(' +str(self.domain5p.n1)+ '->' +str(self.domain5p.n2)+ ') '
        result += 'idx3->5: (' + str(self.idx3p) + '->' + str(self.idx5p) + ') '
        result += 'hel3->5: (' + str(self.hel3p) + '->' + str(self.hel5p) + ') '
        result += 'cr3->5: (' + str(self.cr3p) + '->' + str(self.cr5p) + ') '
        result += 'crL3->5: (' + str(self.cr3pL) + '->' + str(self.cr5pL) + ') '
        return result
    
    ### Getters ###
    @property
    def domain5p(self):
        return self._domain5p
    # end def

    @property
    def domain3p(self):
        return self._domain3p
    # end def

    @property
    def index(self):
        return self.domain5p.ind
    @property
    def ind(self):
        return self.domain5p.ind
    # end def

    @property
    def hel3p(self):
        return self.domain3p.vh
    # end def

    @property
    def hel5p(self):
        return self.domain5p.vh
    
    @property
    def idx3p(self):
        return self.domain3p.idx5p
    # end def

    @property
    def idx5p(self):
        return self.domain5p.idx3p
    # end def

    @property
    def n3p(self):
        return self.domain3p.n2
    # end def

    @property
    def n5p(self):
        return self.domain5p.n1
    # end def

    @property
    def cr3p(self):
        return self.domain3p.cr5p
    # end def

    @property
    def cr5p(self):
        return self.domain5p.cr3p
    # end def

    @property
    def cr3pL(self):
        return self.domain3p.crLong
    # end def

    @property
    def cr5pL(self):
        return self.domain5p.crLong
    # end def

    @property
    def type(self):
        return self._type

    ### Setters ###
    def set_type(self):
        if self.domain3p.is_edge and self.domain5p.is_edge:
            return 'e'
        elif self.domain3p.is_seam and self.domain5p.is_seam:
            return 's'
        else:
            return 'b'