import matplotlib.path as mpath

class Staple:
    def __init__(self, index, cadnano_path):
        self._index = index
        self._cadnano_path = cadnano_path # from 5p on staple to 3p on staple
        # these are set by create_staples_domains_crossovers() 
        self._domains = list() # from 3' to 5' on staple because of legacy
        self._crossovers = list() # from 3' to 5' on staple because of legacy

    def test(self):
        print(self.ind, end='\t')
        print(str([dom.ind for dom in self.domains]),end='\t')
        print(str([dom.ind for dom in self.crossovers]),end='\n')
    def add_colour(self):
        #don't use
        colour = 'blue'
        if len(self.domains)==1: colour = 'red'
        elif len(self.domains)==2: colour = 'blue'
        elif len(self.domains)==3: colour = 'purple'
        self.colour = colour
        return colour
    def add_path(self):
        # This assumes domains are ordered from 3' to 5' on the staple
        path_data = []
        dom = self.domains[0]
        path_data.append((mpath.Path.MOVETO, dom.rpos.r1))
        path_data.append((mpath.Path.LINETO, dom.rpos.r2))
        codes, verts = zip(*path_data)
        self.rpath = mpath.Path(verts, codes)
        for i, dom in enumerate(self.domains[1:]):
            prevdom = self.domains[i]
            if abs(dom.vh-prevdom.vh)>1:
                midx = abs(prevdom.rpos.r1[0] - prevdom.rpos.r2[0]) + max([prevdom.rpos.r1[0], prevdom.rpos.r2[0]])
                midy = (prevdom.rpos.r1[1] + dom.rpos.r1[1]) / 2
                midpoint = [midx, midy]
                path_data.append((mpath.Path.CURVE3, midpoint))
                path_data.append((mpath.Path.CURVE3, dom.rpos.r1))
            else:
                path_data.append((mpath.Path.LINETO,dom.rpos.r1))
            path_data.append((mpath.Path.LINETO,dom.rpos.r2))
            codes, verts = zip(*path_data)
            self.rpath = mpath.Path(verts, codes)
        path_data = []
        for i, dom in enumerate(self.domains):
            if i == 0: path_data.append((mpath.Path.MOVETO,dom.cpos.r1))
            else: path_data.append((mpath.Path.LINETO,dom.cpos.r1))
            path_data.append((mpath.Path.LINETO,dom.cpos.r2))
            codes, verts = zip(*path_data)
            self.cpath = mpath.Path(verts, codes)
    def __str__(self):
        result = 'Staple '+str(self.ind)+': '
        for dom in self.domains: result+= str(dom.ind)+' '
        return result

    ### Getters ###
    @property
    def index(self):
        return self._index
    @property
    def ind(self):
        return self._index
    # end def

    @property
    def domains(self):
        return self._domains
    # end def

    @property
    def crossovers(self):
        return self._crossovers
    # end def

    @property
    def cadnano_path(self):
        return self._cadnano_path
    # end def

    ### Setters ###
    def add_domain(self, domain):
        self._domains.append(domain)

    def add_crossover(self, crossover):
        self._crossovers.append(crossover)

    def set_index(self, index):
        self._index = index