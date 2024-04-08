import matplotlib.path as mpath

class Crossover:
    def __init__(self, cadnano_path, index_on_staple, is_long=False):
        self._cadnano_path = cadnano_path # from 5p on staple to 3p on staple
        self._index_on_staple = index_on_staple
        self._is_long = is_long
        self._index = None
        self._domain_5p_staple = None
        self._domain_3p_staple = None
        self.n1 = None #self._domain_3p_staple.n2 # n1 to n2 is defined as 3p to 5p due to legacy
        self.n2 = None #self._domain_5p_staple.n1
        self.v1 = None # done
        self.v2 = None # done
        self.staple = None # done
        self.type = None # (i)nside, (o)utside, (l)ong, (s)eam
        self.idx1 = None # done
        self.idx2 = None # done
        self.alpha = 1
        #self.test()
    def __eq__(self, other):
        if isinstance(other, Crossover):
            if self.n1 == other.n1 and self.n2 == other.n2: return True
            elif self.n2 == other.n1 and self.n1 == other.n2: return True
            else: return False
        return False
    def test(self):
        print(str(self.ind)+'\t'+str(self.n1)+'-'+str(self.n2),end='\t')
        print(str(self.d1.ind)+'-'+str(self.d2.ind),end='\t')
        print(str(self.v1.ind)+'-'+str(self.v2.ind),end='\t')
        print(str(self.staple.ind)+'\t'+str(self.type),end='\n')
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


    ### Getters ###
    @property
    def ind(self):
        return self._index
    # end def

    @property
    def d1(self):
        return self._domain_3p_staple
    # end def

    @property
    def d2(self):
        return self._domain_5p_staple
    # end def

    @property
    def cadnano_path(self):
        return self._cadnano_path

