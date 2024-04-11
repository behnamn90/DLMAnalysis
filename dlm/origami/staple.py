import matplotlib.path as mpath

class Staple:
    def __init__(self, index, cadnano_path):
        """
        Initializes a Staple object.

        Args:
            index (int): The index of the staple.
            cadnano_path (str): The cadnano path of the staple.

        Returns:
            None
        """
        self._index = index
        self._cadnano_path = cadnano_path # from 5p on staple to 3p on staple
        # these are set by create_staples_domains_crossovers() in pool.py
        self._domains = list() # from 3' to 5' on staple because of legacy
        self._crossovers = list() # from 3' to 5' on staple because of legacy
    # end def

    def add_colour(self):
        """
        Adds a color to the staple based on the number of domains.

        Returns:
            str: The color of the staple.
        """
        #don't use
        colour = 'blue'
        if len(self.domains)==1: colour = 'red'
        elif len(self.domains)==2: colour = 'blue'
        elif len(self.domains)==3: colour = 'purple'
        self.colour = colour
        return colour
    # end def
    
    def add_path(self):
        """
        Adds a path to the staple for drawing purposes.
        The domain and crossover positions must be set prior to calling this method.

        Returns:
            None
        """
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
    # end def
            
    def __str__(self):
        """
        Returns a string representation of the Staple object.

        Returns:
            str: The string representation of the Staple object.
        """
        result = 'Staple '+str(self.ind)+': '
        for dom in self.domains: result+= str(dom.ind)+' '
        return result
    # end def

    ### Getters ###
    
    @property
    def index(self):
        """
        Gets the index of the staple.

        Returns:
            int: The index of the staple.
        """
        return self._index
    @property
    def ind(self):
        """
        Gets the index of the staple.

        Returns:
            int: The index of the staple.
        """
        return self._index
    # end def

    @property
    def domains(self):
        """
        Gets the domains of the staple.

        Returns:
            list: The list of domains in the staple.
        """
        return self._domains
    # end def

    @property
    def crossovers(self):
        """
        Gets the crossovers of the staple.

        Returns:
            list: The list of crossovers in the staple.
        """
        return self._crossovers
    # end def

    @property
    def cadnano_path(self):
        """
        Gets the cadnano path of the staple.

        Returns:
            str: The cadnano path of the staple.
        """
        return self._cadnano_path
    # end def

    ### Setters ###

    def add_domain(self, domain):
        """
        Adds a domain to the staple.

        Args:
            domain (Domain): The domain to be added.

        Returns:
            None
        """
        self._domains.append(domain)
    # end def

    def add_crossover(self, crossover):
        """
        Adds a crossover to the staple.

        Args:
            crossover (Crossover): The crossover to be added.

        Returns:
            None
        """
        self._crossovers.append(crossover)
    # end def

    def set_index(self, index):
        """
        Sets the index of the staple.

        Args:
            index (int): The index to be set.

        Returns:
            None
        """
        self._index = index
    # end def