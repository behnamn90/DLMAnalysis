import matplotlib.path as mpath

class Crossover:
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
        self._index_on_staple = index_on_staple
    # end def

    ### Getters ###
    @property
    def is_long(self):
        return self._is_long
    # end def

    @property
    def cadnano_path(self):
        return self._cadnano_path    
    # end def

    @property
    def domain_5p(self):
        return self._domain_5p
    @property
    def d2(self):
        return self._domain_5p
    # end def

    @property
    def domain_3p(self):
        return self._domain_3p
    @property
    def d1(self):
        return self._domain_3p
    # end def

    @property
    def staple(self):
        return self._staple
    # end def

    @property
    def index_on_staple(self):
        return self._index_on_staple
    @property
    def s_index(self):
        return self._index_on_staple
    # end def

    @property
    def index(self):
        return self._index
    @property
    def ind(self):
        return self._index
    # end def

    @property
    def v1(self):
        return self.d1.v2
    # end def

    @property
    def v2(self):
        return self.d2.v1
    # end def

    @property
    def n1(self):
        return self.d1.n2
    # end def

    @property
    def n2(self):
        return self.d2.n1
    # end def

    @property
    def idx1(self):
        return self.d1.idx5p
    # end def

    @property
    def idx2(self):
        return self.d2.idx3p
    # end def

    @property
    def type(self):
        return self._type
    # end def

    ### Setters ###
    def set_domain_5p(self, d5p):
        self._domain_5p = d5p
    # end def

    def set_domain_3p(self, d3p):
        self._domain_3p = d3p
    # end def

    def set_domains(self, d5p, d3p):
        self.set_domain_5p(d5p)
        self.set_domain_3p(d3p)
    # end def
        
    def set_staple(self, staple):
        self._staple = staple
    # end def
        
    def set_index(self, index):
        self._index = index
    # end def
        
    def set_index_on_staple(self, index_on_staple):
        self._index_on_staple = index_on_staple
        
    def set_type(self, value):
        #if self.is_long and value != 'l':
            #raise ValueError(f'Crossover is long but setting {value} type.')
        #else:
        self._type = value
    # end def

