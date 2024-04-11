import matplotlib.path as mpath

class Crossover:
    """
    Represents a crossover in a DNA origami structure.

    Attributes:
    - cadnano_path: The path of the crossover in the cadnano format.
    - index_on_staple: The index of the crossover on the staple strand.
    - is_long: A boolean indicating if the crossover is a long crossover.
    - domain_5p: The domain on the 5' side of the staple.
    - domain_3p: The domain on the 3' side of the staple.
    - staple: The staple strand that the crossover belongs to.
    - index: The index of the crossover in the structure.
    - type: The type of the crossover (inside, outside, long, seam).

    Methods:
    - add_path(): Adds a path to the crossover.
    - set_index_on_staple(index_on_staple): Sets the index of the crossover on the staple strand.
    - is_long(): Returns True if the crossover is a long crossover, False otherwise.
    - cadnano_path(): Returns the cadnano path of the crossover.
    - domain_5p(): Returns the domain on the 5' side of the staple.
    - domain_3p(): Returns the domain on the 3' side of the staple.
    - staple(): Returns the staple strand that the crossover belongs to.
    - index_on_staple(): Returns the index of the crossover on the staple strand.
    - index(): Returns the index of the crossover in the structure.
    - v1(): Returns the vertex on the 5' side of the crossover.
    - v2(): Returns the vertex on the 3' side of the crossover.
    - n1(): Returns the neighbor on the 5' side of the crossover.
    - n2(): Returns the neighbor on the 3' side of the crossover.
    - idx1(): Returns the index of the 5' domain of the crossover.
    - idx2(): Returns the index of the 3' domain of the crossover.
    - type(): Returns the type of the crossover.
    - set_domain_5p(d5p): Sets the domain on the 5' side of the staple.
    - set_domain_3p(d3p): Sets the domain on the 3' side of the staple.
    - set_domains(d5p, d3p): Sets the domains on both sides of the staple.
    - set_staple(staple): Sets the staple strand that the crossover belongs to.
    - set_index(index): Sets the index of the crossover in the structure.
    - set_index_on_staple(index_on_staple): Sets the index of the crossover on the staple strand.
    - set_type(value): Sets the type of the crossover.
    """
    def __init__(self, cadnano_path, index_on_staple, is_long=False):
        self._cadnano_path = cadnano_path # from 5p on staple to 3p on staple
        self._index_on_staple = index_on_staple # from 3p to 5p (legacy) then long
        self._is_long = is_long

        # these are set by link_staples_domains_crossovers()
        self._domain_5p = None # domain on the 5' side of the staple
        self._domain_3p = None # domain on the 3' side of the staple
        self._staple = None
        
        # these are set by reorder_domains_staples_crossovers()
        self._index = None

        # these are set by fill_crossover_types()
        self._type = '' # (i)nside, (o)utside, (l)ong, (s)eam ! needs to be set from pool
        
        self.alpha = 1

    def __eq__(self, other):
        if isinstance(other, Crossover):
            if self.n1 == other.n1 and self.n2 == other.n2: return True
            elif self.n2 == other.n1 and self.n1 == other.n2: return True
            else: return False
        return False
    # end def

    def add_path(self):
        """
        Adds a path to the crossover for drawing purposes. 
        The rpos and cpos are set by the drawing function outside of the class.
        """
        path_data = []
        path_data.append((mpath.Path.MOVETO,self.rpos.r1))
        if abs(self.d1.vh-self.d2.vh)>1:
            midx = abs(self.d1.rpos.r1[0]-self.d1.rpos.r2[0])+max([self.d1.rpos.r1[0],self.d1.rpos.r2[0]])
            midy = (self.d1.rpos.r1[1]+self.d2.rpos.r1[1])/2
            midpoint = [midx,midy]
            #points = [self.d1.rpos.r1,self.d1.rpos.r2,self.d2.rpos.r1,self.d2.rpos.r2]
            #midpoint = [sum(y) / len(y) for y in zip(*points)]
            path_data.append((mpath.Path.CURVE3,midpoint))
            path_data.append((mpath.Path.CURVE3,self.rpos.r2))
            self.linestyle = '-'#':'
            #self.alpha = 0.8
        else:
            path_data.append((mpath.Path.LINETO,self.rpos.r2))
            self.linestyle = '-'
            #self.alpha = 1
        codes, verts = zip(*path_data)
        self.rpath = mpath.Path(verts, codes)
        path_data = []
        path_data.append((mpath.Path.MOVETO,self.cpos.r1))
        #points = [self.d1.cpos.r1,self.d1.cpos.r2,self.d2.cpos.r1,self.d2.cpos.r2,(0,0)]
        #points = [self.cpos.r1,self.cpos.r2,(0,0)]
        points = [self.d1.cpos.r1,self.d1.cpos.r2,self.d2.cpos.r1,self.d2.cpos.r2,(0,0),(0,0)]
        midpoint = [sum(y) / len(y) for y in zip(*points)]
        path_data.append((mpath.Path.CURVE3,midpoint))
        path_data.append((mpath.Path.CURVE3,self.cpos.r2))
        codes, verts = zip(*path_data)
        self.cpath = mpath.Path(verts, codes)
    # end def

    ### Setters ###
    def set_index_on_staple(self, index_on_staple):
        """
        Sets the index of the crossover on the staple strand.

        Parameters:
        - index_on_staple: The index of the crossover on the staple strand.
        """
        self._index_on_staple = index_on_staple
    # end def

    ### Getters ###
    @property
    def is_long(self):
        """
        Returns True if the crossover is a long crossover, False otherwise.
        """
        return self._is_long
    # end def

    @property
    def cadnano_path(self):
        """
        Returns the cadnano path of the crossover.
        """
        return self._cadnano_path    
    # end def

    @property
    def domain_5p(self):
        """
        Returns the domain on the 5' side of the staple.
        """
        return self._domain_5p
    @property
    def d2(self):
        """
        Returns the domain on the 5' side of the staple.
        """
        return self._domain_5p
    # end def

    @property
    def domain_3p(self):
        """
        Returns the domain on the 3' side of the staple.
        """
        return self._domain_3p
    @property
    def d1(self):
        """
        Returns the domain on the 3' side of the staple.
        """
        return self._domain_3p
    # end def

    @property
    def staple(self):
        """
        Returns the staple strand that the crossover belongs to.
        """
        return self._staple
    # end def

    @property
    def index_on_staple(self):
        """
        Returns the index of the crossover on the staple strand.
        """
        return self._index_on_staple
    @property
    def s_index(self):
        """
        Returns the index of the crossover on the staple strand.
        """
        return self._index_on_staple
    # end def

    @property
    def index(self):
        """
        Returns the index of the crossover in the structure.
        """
        return self._index
    @property
    def ind(self):
        """
        Returns the index of the crossover in the structure.
        """
        return self._index
    # end def

    @property
    def v1(self):
        """
        Returns the vertex on the 5' side of the crossover.
        """
        return self.d1.v2
    # end def

    @property
    def v2(self):
        """
        Returns the vertex on the 3' side of the crossover.
        """
        return self.d2.v1
    # end def

    @property
    def n1(self):
        """
        Returns the neighbor on the 5' side of the crossover.
        """
        return self.d1.n2
    # end def

    @property
    def n2(self):
        """
        Returns the neighbor on the 3' side of the crossover.
        """
        return self.d2.n1
    # end def

    @property
    def idx1(self):
        """
        Returns the index of the 5' domain of the crossover.
        """
        return self.d1.idx5p
    # end def

    @property
    def idx2(self):
        """
        Returns the index of the 3' domain of the crossover.
        """
        return self.d2.idx3p
    # end def

    @property
    def type(self):
        """
        Returns the type of the crossover.
        """
        return self._type
    # end def

    ### Setters ###
    def set_domain_5p(self, d5p):
        """
        Sets the domain on the 5' side of the staple.

        Parameters:
        - d5p: The domain on the 5' side of the staple.
        """
        self._domain_5p = d5p
    # end def

    def set_domain_3p(self, d3p):
        """
        Sets the domain on the 3' side of the staple.

        Parameters:
        - d3p: The domain on the 3' side of the staple.
        """
        self._domain_3p = d3p
    # end def

    def set_domains(self, d5p, d3p):
        """
        Sets the domains on both sides of the staple.

        Parameters:
        - d5p: The domain on the 5' side of the staple.
        - d3p: The domain on the 3' side of the staple.
        """
        self.set_domain_5p(d5p)
        self.set_domain_3p(d3p)
    # end def
        
    def set_staple(self, staple):
        """
        Sets the staple strand that the crossover belongs to.

        Parameters:
        - staple: The staple strand that the crossover belongs to.
        """
        self._staple = staple
    # end def
        
    def set_index(self, index):
        """
        Sets the index of the crossover in the structure.

        Parameters:
        - index: The index of the crossover in the structure.
        """
        self._index = index
    # end def
        
    def set_index_on_staple(self, index_on_staple):
        """
        Sets the index of the crossover on the staple strand.

        Parameters:
        - index_on_staple: The index of the crossover on the staple strand.
        """
        self._index_on_staple = index_on_staple
        
    def set_type(self, value):
        """
        Sets the type of the crossover.

        Parameters:
        - value: The type of the crossover.
        """
        #if self.is_long and value != 'l':
            #raise ValueError(f'Crossover is long but setting {value} type.')
        #else:
        self._type = value
    # end def

