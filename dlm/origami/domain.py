import matplotlib.path as mpath

class Domain:
    def __init__(self, cadnano_path, index_on_staple):
        assert all(x[0] == cadnano_path[0][0] for x in cadnano_path), 'All virtual helix must be the same.'
        self._cadnano_path = cadnano_path # list of tuples from 5' to 3' on staple
        self._index_on_staple = index_on_staple
        self._cadnano_col_low = min((self._cadnano_path[0][1], self._cadnano_path[-1][1])) # the left idx from cadnano
        self._cadnano_col_high = max((self._cadnano_path[0][1], self._cadnano_path[-1][1])) # the right idx from cadnano
        
        self._nuc_5p, self._nuc_3p = None, None # these are staple polarities
        self._index_on_scaffold = None
        self._length = None
        self._domain_type = 'b' # (e)dge, (s)eam , (b)ody  [seam includes broken seams]
        self._is_at_seam = None # whether the domain is at a seam (includes broken seams)
        self._is_at_edge = None

        self._is_seam = None  # Only true if the domain is at a seam and not broken
        self._actual_type = ''

        self.v1 = None # done
        self.v2 = None # done
        self.cr3p = None # done
        self.cr5p = None # done
        self.crLong = None # done
        self.staple = None # done
        self.cols = []
        self.alpha = 1
        #self.test()
    def __eq__(self, other):
        if isinstance(other, Domain):
            if self.n1 == other.n1 and self.n2 == other.n2: return True
            elif self.n2 == other.n1 and self.n1 == other.n2: return True
            else: return False
        return False
    def __str__(self):
        result = 'Domain '+str(self.ind)+': '
        result+= str(self.n1)+'->'+str(self.n2)
        result+= ' ('+str(self.length)+')'
        result+= ' '+self.actual_type
        return result
    def test(self):
        print(str(self.ind)+'\t'+str(self.n1)+'-'+str(self.n2)+'\t'+str(self.v1.ind)+'-'+str(self.v2.ind)+'\t',end='')
        print(str(self.staple.ind),end='\t')
        print(str(self.vh)+'\t'+str(self.cols),end='\t')
        #print(str(self.cr3p.ind)+','+str(self.cr5p.ind)+','+str(self.crLong.ind)+'\t'+
        print(self.type+'\t'+str(self.is_seam)+'\t'+str(self.is_edge))
    def add_path(self):
        path_data = []
        path_data.append((mpath.Path.MOVETO,self.rpos.r1))
        path_data.append((mpath.Path.LINETO,self.rpos.r2))
        codes, verts = zip(*path_data)
        self.rpath = mpath.Path(verts, codes)
        path_data = []
        path_data.append((mpath.Path.MOVETO,self.cpos.r1))
        path_data.append((mpath.Path.LINETO,self.cpos.r2))
        codes, verts = zip(*path_data)
        self.cpath = mpath.Path(verts, codes)


    ### Getters ###
    @property
    def cadnano_path(self):
        return self._cadnano_path    
    
    @property
    def idx3p(self):
        return self._cadnano_path[-1][1]
    # end def

    @property
    def idx5p(self):
        return self._cadnano_path[0][1]
    # end def

    @property
    def idxLow(self):
        return self._cadnano_col_low
    # end def

    @property
    def idxHigh(self):
        return self._cadnano_col_high
    # end def    
    
    @property
    def vh(self):
        return self._cadnano_path[0][0]
    # end def

    @property
    def s_index(self):
        return self._index_on_staple
    # end def

    @property
    def ind(self):
        return self._index_on_scaffold
    # end def

    @property
    def index_on_scaffold(self):
        return self._index_on_scaffold

    @property
    def n1(self):
        return self._nuc_3p
    # end def

    @property
    def n2(self):
        return self._nuc_5p
    # end def

    @property
    def nuc_5p(self):
        return self._nuc_5p
    
    @property
    def nuc_3p(self):
        return self._nuc_3p

    @property
    def length(self):
        return self._length
    # end def

    @property
    def is_seam(self):
        return self._is_seam
    # end def

    @property
    def is_at_seam(self):
        return self._is_at_seam
    # end def

    @property
    def is_edge(self):
        return self._is_at_edge
    # end def

    @property
    def is_at_edge(self):
        return self._is_at_edge
    # end def

    @property
    def actual_type(self):
        return self._actual_type
    # end def

    @property
    def domain_type(self):
        return self._domain_type
    # end def

    @property
    def type(self):
        return self._domain_type

    ### Setters ###
    def set_nucs(self, n5p, n3p):
        self._nuc_5p = n5p
        self._nuc_3p = n3p
    # end def
        
    def set_length(self, value):
        self._length = value
    # end def

    def set_domain_type(self, value):
        self._domain_type = value
        if value == 's':
            self.set_is_at_seam(True)
        elif value == 'e':
            self.set_is_edge(True)
        elif value == 'b':
            self.set_is_at_seam(False)
            self.set_is_edge(False)
        else:
            raise ValueError('Invalid domain type.')
        
    def set_is_edge(self, value):
        self._is_at_edge = value
    # end def
        
    def set_is_at_seam(self, value):
        self._is_at_seam = value
    # end def
        
    def set_index_on_scaffold(self, value):
        self._index_on_scaffold = value
    # end def
    
    def set_is_seam(self, value):
        self._is_seam = value
    # end def

    def set_actual_type(self,value):
        self._actual_type = value
        if value == 's':
            self.set_is_seam(True)
        elif value == 'e':
            self.set_is_edge(True)
        elif value == 'b':
            self.set_is_seam(False)
            self.set_is_edge(False)
        else:
            raise ValueError('Invalid actual type.')
    # end def

    
    