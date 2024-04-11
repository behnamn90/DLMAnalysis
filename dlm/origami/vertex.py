
class Vertex:
    """
    Represents a vertex in a DNA origami structure.
    """
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
        """
        Gets the 5' domain of the vertex.

        Returns:
            Domain: The 5' domain of the vertex.
        """
        return self._domain5p

    @property
    def domain3p(self):
        """
        Gets the 3' domain of the vertex.

        Returns:
            Domain: The 3' domain of the vertex.
        """
        return self._domain3p

    @property
    def index(self):
        """
        Gets the index of the vertex.

        Returns:
            int: The index of the vertex.
        """
        return self.domain5p.ind

    @property
    def ind(self):
        """
        Gets the index of the vertex.

        Returns:
            int: The index of the vertex.
        """
        return self.domain5p.ind

    @property
    def hel3p(self):
        """
        Gets the helicity of the 3' domain.

        Returns:
            int: The helicity of the 3' domain.
        """
        return self.domain3p.vh

    @property
    def hel5p(self):
        """
        Gets the helicity of the 5' domain.

        Returns:
            int: The helicity of the 5' domain.
        """
        return self.domain5p.vh

    @property
    def idx3p(self):
        """
        Gets the index of the 3' domain in the 5' domain.

        Returns:
            int: The index of the 3' domain in the 5' domain.
        """
        return self.domain3p.idx5p

    @property
    def idx5p(self):
        """
        Gets the index of the 5' domain in the 3' domain.

        Returns:
            int: The index of the 5' domain in the 3' domain.
        """
        return self.domain5p.idx3p

    @property
    def n3p(self):
        """
        Gets the second node of the 3' domain.

        Returns:
            int: The second node of the 3' domain.
        """
        return self.domain3p.n2

    @property
    def n5p(self):
        """
        Gets the first node of the 5' domain.

        Returns:
            int: The first node of the 5' domain.
        """
        return self.domain5p.n1

    @property
    def cr3p(self):
        """
        Gets the 5' staple polarity of the 3' domain.

        Returns:
            int: The 5' staple polarity of the 3' domain.
        """
        return self.domain3p.cr5p

    @property
    def cr5p(self):
        """
        Gets the 3' staple polarity of the 5' domain.

        Returns:
            int: The 3' staple polarity of the 5' domain.
        """
        return self.domain5p.cr3p

    @property
    def cr3pL(self):
        """
        Gets the long staple polarity of the 3' domain.

        Returns:
            int: The long staple polarity of the 3' domain.
        """
        return self.domain3p.crLong

    @property
    def cr5pL(self):
        """
        Gets the long staple polarity of the 5' domain.

        Returns:
            int: The long staple polarity of the 5' domain.
        """
        return self.domain5p.crLong

    @property
    def type(self):
        """
        Gets the type of the vertex.

        Returns:
            str: The type of the vertex.
        """
        return self._type

    # Setters
    def set_type(self):
        """
        Sets the type of the vertex based on the domains.

        Returns:
            str: The type of the vertex.
        """
        if self.domain3p.is_edge and self.domain5p.is_edge:
            return 'e'
        elif self.domain3p.is_seam and self.domain5p.is_seam:
            return 's'
        else:
            return 'b'