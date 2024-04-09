import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from collections import OrderedDict

from dlm.origami.cadnano import Cadnano
from dlm.origami.helix import Helix
from dlm.origami.staple import Staple
from dlm.origami.domain import Domain
from dlm.origami.crossover import Crossover
from dlm.origami.crosspair import CrossPair
from dlm.origami.vertex import Vertex
from dlm.origami.endpoints import Endpoints

from dlm.origami.general import XY_SCALE, op_dict, default_colours, draw
from dlm.common.myfuncs import circ_subtract

def ring_distance(a, b, mod):
    """
    Returns the distance between two indices on a ring.

    Args:
        a (int): The first index.
        b (int): The second index.
        mod (int): The modulus of the ring.

    Returns:
        int: The distance between the two indices.
    """
    assert a >= 0 and b >= 0 and mod > 0, 'All inputs must be positive.'
    assert a < mod and b < mod, 'All inputs must be less than the modulus.'
    mod_distance = abs( (a-b) % mod )
    return min(mod_distance, mod - mod_distance)

def single_OP(myfile,OP_t,name,pool_id,idxs):
    myfile.write('{\n')
    myfile.write('\t'+'OP_t = '+op_dict[OP_t]+'\n')
    myfile.write('\t'+'Name = '+name+'\n')
    myfile.write('\t'+'Pool = '+str(pool_id)+'\n')
    myfile.write('\t'+'Set = [ ')
    for idx in idxs:
        myfile.write(str(idx)+" ")
    myfile.write(']\n')
    myfile.write('}\n')

here_path = os.getcwd()

class Pool:
    """
    Represents a pool of origami structures.

    Args:
        json_file_path (str): The path to the JSON file containing the origami structure.

    Attributes:
        _json_file_path (str): The path of the JSON file associated with this object.
        _cadnano (Cadnano): The Cadnano object representing the origami structure.
        _helices (list): A list of Helix objects representing the helices in the origami structure.
        _staples (list): A list of Staple objects representing the staples in the origami structure.
        _domains (list): A list of Domain objects representing the domains in the origami structure.
        _crossovers (list): A list of Crossover objects representing the crossovers in the origami structure.

    """

    def __init__(self, json_file_path, index=0):
        self._json_file_path = json_file_path
        self._index = index
        self._cadnano = Cadnano.from_json(json_file_path)
        self._staples, self._domains, self._crossovers = list(), list(), list()
        self.create_staples_domains_crossovers()
        self.link_staples_domains_crossovers()
        self.fill_domain_attributes() 
        self.reorder_domains_staples_crossovers() # needs domain nucleotides to be set.
        self._helices = self.create_helices() # needs domains to have idxLow (which they do after initialisation)
        self._vertices = self.create_vertices() # needs domains to be ordered
        self._seam_domains, self._edge_domains = self.fill_actual_edges()
        self.fill_crossover_types()
        self._column_id_to_cadnano_col = {} # maps column id to cadnano column (a,b), where a is beginning of the column and b is the end
        self._edge_column_ids = list() # integer ids of the edge columns
        self._seam_column_ids = list() # integer ids of the seam columns (includes broken seams)
        self.find_column_ids() # sets the above three attributes
        self.add_column_ids_to_domains()
        self._cross_pairs = self.create_cross_pairs()
        self._staple_num_domains = sorted(list(set([len(st.domains) for st in self.staples])))
        self._domain_size_ids = self.get_domain_size_ids() # small, medium, large, xlarge
        self._seam_vhs, self._seam_columns, self._seam_nucs = self.get_seam_vhs_idxs_nucs()
    # end def

    def create_staples_domains_crossovers(self):
        """
        Creates the staples, domains, and crossovers in the pool by following the path of each staple.
        """
        staple_paths = self._cadnano.staple_paths
        # use this to determine the crossover positions
        cross_df = self._cadnano.staple_crossover_df
        # some seam staple path continue at the seam so need to add a crossover location for them.
        seam_df = self._cadnano.seam_df
        # some single-domain staples stop at the seam so need to handle this case.
        is_terminal_location = self._cadnano.staple_df.map(lambda x: -1 in x)
        for staple_index, staple_path in enumerate(staple_paths):
            staple = Staple(staple_index, staple_path)
            cross_positions = [
                pos for pos in staple_path 
                if cross_df.loc[pos] 
                or (seam_df.loc[pos] & (is_terminal_location.loc[pos] == False))]
            cross_position_indices = [staple_path.index(pos) for pos in cross_positions]
            if len(cross_positions) % 2 != 0:
                raise ValueError('The number of crossover positions is not even.')
            if len(cross_positions) > 4:
                raise ValueError('The number of crossover positions is greater than 4.')
            domain_position_indices = [0]+cross_position_indices+[len(staple_path)-1]
            domain_staple_index = 0
            for i in range(0, len(domain_position_indices), 2):
                start, end = (domain_position_indices[i], domain_position_indices[i+1])    
                domain_path = staple_path[start:end+1]
                domain = Domain(domain_path, domain_staple_index)
                domain_staple_index += 1
                self._domains.append(domain)
                staple.add_domain(domain)
            crossover_staple_index = 0
            staple_crossovers = []
            for i in range(0, len(cross_position_indices), 2):
                start, end = (cross_position_indices[i], cross_position_indices[i+1])
                crossover_path = staple_path[start:end+1]
                crossover = Crossover(crossover_path, crossover_staple_index, is_long=False)
                crossover_staple_index += 1
                #self._crossovers.append(crossover)
                #staple.add_crossover(crossover)
                staple_crossovers.append(crossover)
            # for legacy reasons, we will add the crossovers in the order they appear in the staple path from 3' to 5'
            reversed_crossovers = list(reversed(staple_crossovers))
            staple._crossovers = reversed_crossovers
            self._crossovers.extend(reversed_crossovers)
            staple_crossovers = []
            # Now do long crossover
            if len(cross_position_indices) == 4:
                start, end = (cross_position_indices[0], cross_position_indices[3])
                crossover_path = (staple_path[start], staple_path[end])
                crossover = Crossover(crossover_path, crossover_staple_index, is_long=True)
                crossover_staple_index += 1
                #self._crossovers.append(crossover)
                #staple.add_crossover(crossover)
                staple_crossovers.append(crossover)
            reversed_crossovers = list(reversed(staple_crossovers))
            staple._crossovers.extend(reversed_crossovers)
            self._crossovers.extend(reversed_crossovers)
            self._staples.append(staple)
    # end def

    def link_staples_domains_crossovers(self):
        """
        Links the domains to the crossovers in the pool. Also add staples to both.
        """
        for staple in self._staples:
            for domain in staple.domains:
                domain.set_staple(staple)
                for crossover in staple.crossovers:
                    if domain.cadnano_path[-1] == crossover.cadnano_path[0]:
                        crossover.set_domain_5p(domain)
                        if crossover.is_long:
                            domain.set_long_crossover(crossover)
                        else:
                            domain.set_crossover_3p(crossover)
                    if domain.cadnano_path[0] == crossover.cadnano_path[-1]:
                        crossover.set_domain_3p(domain)
                        if crossover.is_long:
                            domain.set_long_crossover(crossover)
                        else:
                            domain.set_crossover_5p(crossover)
        for staple in self._staples:
            for crossover in staple.crossovers:
                crossover.set_staple(staple)
    # end def
                
    def fill_domain_attributes(self):
        """
        Fills the attributes of the domains in the pool.
        Also redorders the domains based on their position of the scaffold.
        """
        nuc_df = self._cadnano.nucleotide_df
        seam_df = self._cadnano.seam_df
        edge_df = self._cadnano.edge_df
        scaffold_length = nuc_df.max().max() + 1
        for domain in self._domains:
            domain_type = 'b'
            pos5p, pos3p = domain.cadnano_path[0], domain.cadnano_path[-1]
            nuc5p, nuc3p = nuc_df.loc[pos5p], nuc_df.loc[pos3p]
            domain_length = ring_distance(nuc5p, nuc3p, scaffold_length)+1
            is_at_seam = any([seam_df.loc[pos5p], seam_df.loc[pos3p]])
            is_edge = any([edge_df.loc[pos5p], edge_df.loc[pos3p]])
            if is_at_seam:
                domain_type = 's'
            if is_edge:
                domain_type = 'e'
            domain.set_nucs(nuc5p, nuc3p)
            domain.set_length(domain_length)
            domain.set_domain_type(domain_type)
    # end def
            
    def reorder_domains_staples_crossovers(self):
        self.domains.sort(key=lambda domain: domain.n1)
        for i, domain in enumerate(self._domains):
            domain.set_index_on_scaffold(i)
        self.staples.sort(key=lambda st: np.min([dom.ind for dom in st.domains]))
        for i, staple in enumerate(self.staples):
            staple.set_index(i)      
        self.crossovers.sort(key=lambda cr: cr.staple.ind)
        for i, crossover in enumerate(self.crossovers):
            crossover.set_index(i)
        #reverse the domains in the staples for backward compatibility
        for staple in self.staples:
            staple.domains.reverse()
            for i, domain in enumerate(staple.domains):
                domain.set_index_on_staple(i)
            for i, crossover in enumerate(staple.crossovers):
                crossover.set_index_on_staple(i)
    # end def
    
    def create_helices(self):
        """
        Adds the helices to the pool.

        Returns:
            list: A list of Helix objects representing the helices in the origami structure.
        """
        helices = []
        nuc_df = self._cadnano.nucleotide_df
        for index, row in nuc_df.iterrows():
            helix = Helix(index, [nuc for nuc in row.tolist() if nuc != -1])
            helix_domains = []
            for domain in self._domains:
                if domain.vh == index:
                    helix_domains.append(domain)
            helix_domains.sort(key=lambda dom: dom.idxLow)
            helix.set_domains(helix_domains)
            helices.append(helix)
        return helices
    # end def

    def create_vertices(self):
        vertices = []
        for domain5p in self.domains:
            domain3p = self.domains[circ_subtract(domain5p.ind,1,len(self.domains))]
            vertex = Vertex(domain3p,domain5p)
            domain5p.set_vertex_3p(vertex)
            domain3p.set_vertex_5p(vertex)
            vertices.append(vertex)
        return vertices
    # end def

    def fill_actual_edges(self):
        dummy = []
        for d1 in self.domains:
            for d2 in self.domains:
                if d1.type == 'e' and d2.type == 'e':
                    if d1.ind != d2.ind:
                        if abs(d1.vh-d2.vh) == 1:
                            dummy.append((d1,d2))
        for d1,d2 in dummy:
            if len(d1.staple.domains)>1 or len(d2.staple.domains)>1:
                d1.set_is_edge(True)
                d2.set_is_edge(True)
        seam_cols = self._cadnano.seam_df.columns[self._cadnano.seam_df.any()].tolist()
        for domain in self._domains:
            domain.set_actual_type('b')
            if domain.is_at_edge:
                if domain.crossover_3p != None: # cannot be single-domain
                    if domain.crossover_3p.domain_5p.is_at_edge: # must have a crossover to another edge domain
                        domain.set_actual_type('e')
                if domain.crossover_5p != None:
                    if domain.crossover_5p.domain_3p.is_at_edge:
                        domain.set_actual_type('e')
            if domain.is_at_seam:
                if domain.crossover_3p != None: # cannot be single-domain
                    if domain.crossover_3p.domain_5p.is_at_seam: # must have a crossover to another seam domain
                        if domain.idx5p not in seam_cols: # the other end must not terminate at the seam (N2 types)
                            domain.set_actual_type('s')
                if domain.crossover_5p != None:
                    if domain.crossover_5p.domain_3p.is_at_seam:
                        if domain.idx3p not in seam_cols:
                            domain.set_actual_type('s')
        seam_doms = []
        edge_doms = []
        for domain in self.domains:
            if domain.is_seam:
                seam_doms.append(domain)
            if domain.is_edge:
                edge_doms.append(domain)
        return seam_doms, edge_doms
    # end def

    def fill_crossover_types(self):
        vhs = self._cadnano.edge_df.index.tolist()
        outside_vh_pairs = [(vhs[0],vhs[-1])]
        outside_vh_pairs.extend(list(zip(vhs[1:-1:2], vhs[2:-1:2])))
        for cross in self.crossovers:
            if (cross.d1.vh, cross.d2.vh) in outside_vh_pairs or (cross.d2.vh, cross.d1.vh) in outside_vh_pairs:
                cross.set_type('o')
            else:
                cross.set_type('i')
            if cross.d1.is_seam and cross.d2.is_seam:
                cross.set_type('s')
            if abs(cross.d1.vh - cross.d2.vh) > 1 and len(cross.staple.domains) == 3:
                cross.set_type('l')
            if abs(cross.d1.s_index - cross.d2.s_index) > 1:
                cross.set_type('l')
        # Check long crossovers are correct
        for cross in self.crossovers:
            if cross.is_long and cross.type != 'l':
                raise ValueError(f'Long crossover with type {cross.type} found.')
    # end def
                
    def find_column_ids(self):
        """
        Fills in values for:
        _edge_column_ids
        _seam_column_ids
        _column_id_to_cadnano_col
        """
        seam_df = self._cadnano.seam_df
        edge_df = self._cadnano.edge_df
        vertex_df = self._cadnano.vertex_df 
        column_edges = sorted(vertex_df.columns[vertex_df.any()].tolist())
        cadnano_cols = list(zip(column_edges[:-1], column_edges[1:]))
        cadnano_cols = [a for a in cadnano_cols if abs(a[0]-a[1]) > 1]
        self._column_id_to_cadnano_col = {i+1: col for i, col in enumerate(cadnano_cols)}
        seam_points = sorted(seam_df.columns[seam_df.any()].tolist())
        self._seam_column_ids = [i for i, col in self._column_id_to_cadnano_col.items() if any(edge in col for edge in seam_points)]
        edge_points = sorted(edge_df.columns[edge_df.any()].tolist())
        self._edge_column_ids = [i for i, col in self._column_id_to_cadnano_col.items() if any(edge in col for edge in edge_points)]
    # end def

    def add_column_ids_to_domains(self):
        for domain in self.domains:
            domain_col_ids = set()
            for col_id, col in self.col_idxs.items():
                if domain.idxLow == col[0]:
                    domain_col_ids.add(col_id)
                if domain.idxHigh == col[1]:
                    domain_col_ids.add(col_id)
            domain.set_col_ids(list(domain_col_ids))
    # end def

    def create_cross_pairs(self):
        result = []
        index = 0
        for cross1 in self.crossovers:
            for cross2 in self.crossovers:
                if cross1.ind < cross2.ind:
                    if cross1.v1 == cross2.v2 and cross2.v1 == cross1.v2:
                        result.append(CrossPair(index,cross1,cross2))
                        index+=1
        return result
    # end def

    def get_domain_size_ids(self):
        limits = [10,20,30] # upper limits for small, medium, large. Above that becomes Xlarge
        smalls = [obj.ind for obj in self.domains if obj.length<limits[0]]
        mediums = [obj.ind for obj in self.domains if obj.length<limits[1] and obj.length>limits[0]]
        larges = [obj.ind for obj in self.domains if obj.length<limits[2] and obj.length>limits[1]]
        xlarges = [obj.ind for obj in self.domains if obj.length>limits[2]]
        Result = {}
        if len(smalls) > 0: Result['Small_Domains'] = smalls
        if len(mediums) > 0: Result['Medium_Domains'] = mediums
        if len(larges) > 0: Result['Large_Domains'] = larges
        if len(xlarges) > 0: Result['XLarge_Domains'] = xlarges
        return Result
    # end def

    def get_seam_vhs_idxs_nucs(self):
        seam_df = self._cadnano.seam_df
        seam_vhs = seam_df[seam_df.any(axis=1)].index.tolist()
        seam_cols = seam_df.columns[seam_df.any()].tolist()
        stacked = seam_df.stack()
        seam_locs = stacked[stacked == True].index.tolist()
        seam_nucs = [self._cadnano.nucleotide_map[loc] for loc in seam_locs]
        return seam_vhs, seam_cols, seam_nucs

    ### Getters ###

    @property
    def json_file(self):
        """
        Returns the path of the JSON file associated with this object.

        Returns:
            str: The path of the JSON file.
        """
        return self._json_file_path

    @property
    def index(self):
        """
        Returns the index of the pool.

        Returns:
            int: The index of the pool.
        """
        return self._index
    @property
    def idx(self):
        """
        Legacy function. Returns index.
        """
        return self._index

    @property
    def helices(self):
        """
        Returns the helices of the pool.

        Returns:
            list: A list of Helix objects.
        """
        return self._helices

    @property
    def staples(self):
        """
        Returns the staples of the pool.

        Returns:
            list: A list of Staple objects.
        """
        return self._staples
    
    @property
    def domains(self):
        """
        Returns the domains of the pool.

        Returns:
            list: A list of Domain objects.
        """
        return self._domains
    
    @property
    def crossovers(self):
        """
        Returns the crossovers of the pool.

        Returns:
            list: A list of Crossover objects.
        """
        return self._crossovers
    
    @property
    def vertices(self):
        """
        Returns the vertices of the pool.

        Returns:
            list: A list of vertices.
        """
        return self._vertices

    @property
    def column_id_to_cadnano_col(self):
        """
        Returns a dictionary mapping the column ID to the Cadnano column.

        Returns:
            dict: A dictionary mapping the column ID to the Cadnano column.
        """
        return self._column_id_to_cadnano_col
    
    @property
    def col_idxs(self):
        """
        Legacy function. Returns _column_id_to_cadnano_col.
        """
        return self._column_id_to_cadnano_col

    @property
    def edge_column_ids(self):
        """
        Returns the column IDs of the edge domains.

        Returns:
            list: A list of column IDs of the edge domains.
        """
        return self._edge_column_ids
    
    @property
    def edge_cols(self):
        """
        Legacy function. Returns _edge_column_ids.
        """
        return self._edge_column_ids

    @property
    def seam_column_ids(self):
        """
        Returns the column IDs of the seam domains.

        Returns:
            list: A list of column IDs of the seam domains.
        """
        return self._seam_column_ids

    @property
    def seam_cols(self):
        """
        Legacy function. Returns _seam_column_ids.
        """
        return self._seam_column_ids
    
    @property
    def seam_domains(self):
        """
        Returns the seam domains.

        Returns:
            list: A list of Domain objects representing the seam domains.
        """
        return self._seam_domains
    @property
    def seam_doms(self):
        """
        Legacy function. Returns _seam_domains.
        """
        return self._seam_domains
    
    @property
    def edge_domains(self):
        """
        Returns the edge domains.

        Returns:
            list: A list of Domain objects representing the edge domains.
        """
        return self._edge_domains
    @property
    def edge_doms(self):
        """
        Legacy function. Returns _edge_domains.
        """
        return self._edge_domains
    
    @property
    def cross_pairs(self):
        """
        Returns the cross pairs.

        Returns:
            list: A list of CrossPair objects.
        """
        return self._cross_pairs

    @property
    def staple_num_domains(self):
        """
        Returns a list of unique staple sizes in the pool (number of domains in each staple)

        Returns:
            list: A list of integers representing the number of domains found in all staples.
        """
        return self._staple_num_domains
    @property
    def staple_types(self):
        """
        Legacy function. Returns _staple_num_domains.
        """
        return self._staple_num_domains

    @property
    def domain_size_ids(self):
        """
        Returns a dictionary of domain ids with keys being the size.

        Returns:
            dict: A dictionary of domain size IDs.
        """
        return self._domain_size_ids
    @property
    def domain_sizes(self):
        """
        Legacy function. Returns _domain_size_ids.
        """
        return self._domain_size_ids

    @property
    def PoolName(self):
        return self._json_file_path
    
    @property
    def ActualPoolName(self):
        return self._json_file_path.split('/')[-1].split('.')[0]

    @property
    def num_nucs(self):
        return self._cadnano.nucleotide_df.max().max()+1

    @property
    def seam_vhs(self):
        return self._seam_vhs
    @property
    def seam_idxs(self):
        return self._seam_columns
    @property
    def seam_nucs(self):
        return self._seam_nucs

    ### Visualisations ###

    def add_pos(self):
        # Rectangular
        disp_x = 1
        disp_y = 2
        vhs = self._cadnano.edge_df.index.tolist()
        start_vh = vhs[0]
        last_vh = vhs[-1]
        mid_vh = (last_vh+start_vh)/2
        for vertex in self.vertices:
            x1 = vertex.idx3p
            y1 = vertex.hel3p*XY_SCALE
            x2 = vertex.idx5p
            y2 = vertex.hel5p*XY_SCALE
            vertex.rpos = Endpoints(x1,y1,x2,y2)
        for staple in self.staples:
            if len(staple.domains) == 1:
                d1 = staple.domains[0]
                d1.dy = 0
                if d1.vh == start_vh: d1.dy=disp_y
                elif d1.vh == last_vh: d1.dy=-disp_y
                else:
                    if (d1.vh+start_vh)%2==0: d1.dy=-disp_y
                    else: d1.dy=disp_y
                #if d1.vh > 5: d1.dy = -1
                #if d1.vh < 5: d1.dy = 1
            elif len(staple.domains) == 2:
                d1 = staple.domains[0]; d2 = staple.domains[-1]
                if d1.vh > d2.vh: d1.dy,d2.dy = -disp_y,disp_y
                if d1.vh < d2.vh: d1.dy,d2.dy = disp_y,-disp_y
                if d1.vh == d2.vh:
                    if (d1.vh+start_vh)%2==0: d1.dy,d2.dy = -disp_y,-disp_y
                    else: d1.dy,d2.dy = disp_y,disp_y
            elif len(staple.domains) == 3:
                d1 = staple.domains[0]; d2 = staple.domains[1]; d3 = staple.domains[-1]
                if d1.vh > d2.vh > d3.vh: d1.dy,d2.dy,d3.dy = -disp_y,0,disp_y
                if d1.vh < d2.vh < d3.vh: d1.dy,d2.dy,d3.dy = disp_y,0,-disp_y
                '''
                if d1.vh > d2.vh and d2.vh == d3.vh: d1.dy,d2.dy,d3.dy = -disp_y,disp_y,disp_y
                if d1.vh < d2.vh and d2.vh == d3.vh: d1.dy,d2.dy,d3.dy = disp_y,-disp_y,-disp_y
                if d1.vh == d2.vh and d2.vh > d3.vh: d1.dy,d2.dy,d3.dy = disp_y,disp_y,-disp_y
                if d1.vh == d2.vh and d2.vh < d3.vh: d1.dy,d2.dy,d3.dy = -disp_y,-disp_y,disp_y
                '''
                if d1.vh > d2.vh and d2.vh == d3.vh: d1.dy,d2.dy,d3.dy = -disp_y,disp_y,disp_y
                if d1.vh < d2.vh and d2.vh == d3.vh: d1.dy,d2.dy,d3.dy = disp_y,-disp_y,-disp_y
                if d1.vh == d2.vh and d2.vh > d3.vh: d1.dy,d2.dy,d3.dy = -disp_y,-disp_y,disp_y
                if d1.vh == d2.vh and d2.vh < d3.vh: d1.dy,d2.dy,d3.dy = disp_y,disp_y,-disp_y
        for domain in self.domains:
            x1, y1 = domain.v1.rpos.x2, domain.v1.rpos.y2 + domain.dy
            x2, y2 = domain.v2.rpos.x1, domain.v2.rpos.y1 + domain.dy
            if x1 > x2:
                x1-=disp_x
                x2+=disp_x
            else:
                x1+=disp_x
                x2-=disp_x
            domain.rpos = Endpoints(x1,y1,x2,y2)
        for cross in self.crossovers:
            x1, y1 = cross.d1.rpos.x2, cross.d1.rpos.y2
            x2, y2 = cross.d2.rpos.x1, cross.d2.rpos.y1
            cross.rpos = Endpoints(x1,y1,x2,y2)
        # Circular
        num_nucs = self.num_nucs
        radius = 100
        offset = (num_nucs/4)-self.vertices[0].n3p-(6*16)
        if 'SqU1' in self.PoolName or 'SqUa1' in self.PoolName: offset = (num_nucs/4)-(1*16)
        if 'SqU2' in self.PoolName or 'SqUa2' in self.PoolName: offset = (num_nucs/4)-(3*16)
        for vertex in self.vertices:
            n3p = (vertex.n3p+offset)%num_nucs  #circ_subtract(vertex.n3p,offset,num_nucs)
            n5p = (vertex.n5p+offset)%num_nucs  #circ_subtract(vertex.n5p,offset,num_nucs)
            theta1 = (-2*np.pi*n3p)/num_nucs
            theta2 = (-2*np.pi*n5p)/num_nucs
            x1 = radius*np.cos(theta1)
            y1 = radius*np.sin(theta1)
            x2 = radius*np.cos(theta2)
            y2 = radius*np.sin(theta2)
            vertex.cpos = Endpoints(x1,y1,x2,y2)
        for domain in self.domains:
            x1, y1 = domain.v1.cpos.x2, domain.v1.cpos.y2
            x2, y2 = domain.v2.cpos.x1, domain.v2.cpos.y1
            domain.cpos = Endpoints(x1,y1,x2,y2)
        for cross in self.crossovers:
            x1, y1 = cross.d1.cpos.x2, cross.d1.cpos.y2
            x2, y2 = cross.d2.cpos.x1, cross.d2.cpos.y1
            cross.cpos = Endpoints(x1,y1,x2,y2)

    def draw_scaffold(self,ax,layout='rect',labels=False,broken=False):
        colour = default_colours[0]
        alpha = 1
        tickness = 0.8
        for v in self.vertices:
            rad = 0
            if v.domain3p != None and v.domain5p != None:
                if layout == 'rect' and abs(v.domain3p.vh-v.domain5p.vh)>2: rad = -0.2
                if layout == 'rect': v.pos = v.rpos
                elif layout == 'circ': v.pos = v.cpos
            else:
                if layout == 'rect': v.pos = v.rpos
                elif layout == 'circ': v.pos = v.cpos
            if broken and v.ind == 0: continue
            e = matplotlib.patches.FancyArrowPatch(v.pos.r1,v.pos.r2,
                                linewidth=tickness,
                                arrowstyle='-',
                                alpha=alpha,
                                connectionstyle='arc3,rad=%s'%rad,
                                shrinkA=0,shrinkB=0,
                                color=colour)
            if labels: ax.text(v.pos.x1, v.pos.y1, str(v.ind))
            ax.add_patch(e)

        for v1, v2 in zip(self.vertices[:-1], self.vertices[1:]):
            e = matplotlib.patches.FancyArrowPatch(v1.pos.r2,v2.pos.r1,
                                linewidth=tickness,
                                arrowstyle='-',
                                alpha=alpha,
                                shrinkA=0,shrinkB=0,
                                color=colour)
            ax.add_patch(e)
        v1, v2 = self.vertices[-1], self.vertices[0]
        e = matplotlib.patches.FancyArrowPatch(v1.pos.r2,v2.pos.r1,
                            linewidth=tickness,
                            arrowstyle='-',
                            alpha=alpha,
                            shrinkA=0,shrinkB=0,
                            color=colour)
        ax.add_patch(e)

    def set_default_colors(self):
        colour = 'red'
        for staple in self.staples:
            colour  = default_colours[len(staple.domains)]
            staple.colour = colour
            for domain in staple.domains: domain.colour = colour
            for crossover in staple.crossovers: crossover.colour = colour

    def set_grey_colors(self):
        colour = 'grey'
        for staple in self.staples:
            staple.colour = colour
            for domain in staple.domains: domain.colour = colour
            for crossover in staple.crossovers: crossover.colour = colour

    def set_custom_color(self,colour):
        for staple in self.staples:
            staple.colour = colour
            for domain in staple.domains: domain.colour = colour
            for crossover in staple.crossovers: crossover.colour = colour

    def set_staple_colors(self,colors):
        for i,colour in enumerate(colors):
            self.staples[i].colour = colour

    def set_domain_colors(self,colors):
        for i,colour in enumerate(colors):
            self.domains[i].colour = colour

    def set_crossover_colors(self,colors):
        for i,colour in enumerate(colors):
            self.crossovers[i].colour = colour

    def set_domain_alphas(self,alphas):
        for i,alpha in enumerate(alphas):
            self.domains[i].alpha = alphas[i]

    def set_crossover_alphas(self,alphas):
        for i,alpha in enumerate(alphas):
            self.crossovers[i].alpha = alphas[i]

    def draw_crossovers(self,ax,layout,labelled=False):
        tickness = 1.5
        for crossover in self.crossovers:
            if crossover.type == 'l': continue
            alpha = crossover.alpha
            #if crossover.colour == 'white': alpha = 0
            crossover.add_path()
            if layout == 'rect':  pos, path = crossover.rpos, crossover.rpath
            elif layout == 'circ': pos, path = crossover.cpos, crossover.cpath
            if layout == 'rect':
                patch = matplotlib.patches.PathPatch(path,
                                            linewidth = tickness,
                                            linestyle = crossover.linestyle,
                                            edgecolor = crossover.colour,
                                            facecolor = None,
                                            fill = False,
                                            capstyle = 'round',
                                            #capstyle = 'projecting',
                                            alpha=alpha)
            elif layout == 'circ':
                #scaling = abs(crossover.n1-crossover.n2)/self.scaf.length()
                #scaling = 40*circ_dist(crossover.n1,crossover.n2,self.scaf.length())/self.scaf.length()
                #rad = 1/scaling
                rad = -0.6
                if crossover.type=='s': rad = 0.1
                patch = matplotlib.patches.FancyArrowPatch(pos.r1,pos.r2,
                        arrowstyle='-',
                        linestyle = '-',
                        connectionstyle='arc3,rad=%s'%rad,
                        mutation_scale=10.0,
                        lw = 1,
                        color = crossover.colour,
                        alpha=alpha)
            ax.add_patch(patch)
            if labelled: ax.text(pos.center[0],pos.center[1],str(crossover.ind),fontsize=8)

    def draw_domains(self,ax,layout,labelled=False):
        tickness = 1.5
        for domain in self.domains:
            #alpha = 1
            alpha = domain.alpha
            #if domain.colour == 'white': alpha = 0
            domain.add_path()
            if layout == 'rect':  pos, path = domain.rpos, domain.rpath
            elif layout == 'circ': pos, path = domain.cpos, domain.cpath
            patch = matplotlib.patches.PathPatch(path,
                                        linewidth=tickness,
                                        edgecolor = domain.colour,
                                        facecolor = None,
                                        fill = False,
                                        capstyle = 'round',
                                        #capstyle = 'projecting',
                                        alpha=alpha)
            ax.add_patch(patch)
            if labelled: ax.text(pos.center[0],pos.center[1],str(domain.ind),fontsize=8)

    def draw_staples(self,ax,layout='rect',labelled=False):
        tickness = 1.5
        alpha = 1
        for staple in self.staples:
            staple.add_path()
            if layout == 'rect':  pos, path = staple.domains[0].rpos, staple.rpath
            elif layout == 'circ': pos, path = staple.domains[0].cpos, staple.cpath
            patch = matplotlib.patches.PathPatch(path,
                                        linewidth=tickness,
                                        edgecolor = staple.colour,
                                        facecolor = None,
                                        fill = False,
                                        #joinstyle = 'bevel',
                                        joinstyle = 'round',
                                        #joinstyle = 'miter',
                                        alpha=alpha)
            ax.add_patch(patch)
            if labelled: ax.text(pos.center[0], pos.center[1], str(staple.ind), fontsize=8)

    ### File Writers ###
    
    def help_top(self,myfile):
        myfile.write('{'+self.ActualPoolName+'\n')
        myfile.write('\t[Specifications\n')
        myfile.write('\t\tnum_nucs = '+str(self.num_nucs)+'\n')
        myfile.write('\t]\n')
        myfile.write('\t[Domains\n')
        for domain in self.domains:
            line = '\t\t'+str(domain.ind)+'\t'+str(domain.n1)+'-'+str(domain.n2)+'\t'+str(domain.actual_type)
            myfile.write(line+'\n')
        myfile.write('\t]\n')
        myfile.write('\t[Staples\n')
        for staple in self.staples:
            line = '\t\t'+str(staple.ind)+'\t'
            for domain in staple.domains:
                line+= str(domain.ind)+','
            line = line[:-1]
            myfile.write(line+'\n')
        myfile.write('\t]\n')
        myfile.write('\t[Crossovers\n')
        for crossover in self.crossovers:
            line = '\t\t'+str(crossover.ind)+'\t'+str(crossover.d1.ind)+'-'+str(crossover.d2.ind)+'\t'+str(crossover.type)
            myfile.write(line+'\n')
        myfile.write('\t]\n')
        myfile.write('\t[Helices\n')
        for helix in self.helices:
            line = '\t\t'
            line += str(helix.ind) + ' : '
            for domain in helix.domains:
                line+= str(domain.ind)+' '
            line = line[:-1]
            myfile.write(line+'\n')
        myfile.write('\t]\n')
        myfile.write('}\n')
    def write_top_Oct19(self,out_path):
        with open(out_path,'w') as myfile:
            self.help_top(myfile)

    def help_OPs(self,myfile):
        if len(self.domains) != len(self.staples):
            single_OP(myfile,'ST','Staples',self.idx,[obj.ind for obj in self.staples])
        if len(self.crossovers) != 0:
            single_OP(myfile,'CR','Crossover',self.idx,[obj.ind for obj in self.crossovers])
        idxs = [obj.ind for obj in self.domains if obj.is_seam]
        if len(idxs)!=0:
            single_OP(myfile,'DOM','Seam_Domains',self.idx,idxs)
        idxs = [obj.ind for obj in self.domains if obj.is_edge]
        if len(idxs)!=0:
            single_OP(myfile,'DOM','Edge_Domains',self.idx,idxs)
        if len(self.staple_types) > 1:
            for num_dom in self.staple_types:
                if num_dom == 1:
                    name = 'SingleDom_Staples'
                if num_dom == 2:
                    name = 'DoubleDom_Staples'
                if num_dom == 3:
                    name = 'TripleDom_Staples'
                idxs = [obj.ind for obj in self.staples if len(obj.domains) == num_dom]
                if len(idxs)!=0:
                    single_OP(myfile,'ST',name,self.idx,idxs)
        idxs = [obj.ind for obj in self.crossovers if obj.type == 'i']
        if len(idxs)!=0:
            single_OP(myfile,'CR','Inside_Cross',self.idx,idxs)
        idxs = [obj.ind for obj in self.crossovers if obj.type == 'o']
        if len(idxs)!=0:
            single_OP(myfile,'CR','Outside_Cross',self.idx,idxs)
        idxs = [obj.ind for obj in self.crossovers if obj.type == 's']
        if len(idxs)!=0:
            single_OP(myfile,'CR','Seam_Cross',self.idx,idxs)
        idxs = [obj.ind for obj in self.crossovers if obj.type == 'l']
        if len(idxs)!=0:
            single_OP(myfile,'CR','Long_Cross',self.idx,idxs)
        if len(self.edge_doms)!=0:
            idxs = [idx for idx,obj in enumerate(self.helices)]
            if len(idxs)!=0:
                single_OP(myfile,'HLX','Helix',self.idx,idxs)
            if len(self.seam_doms)!=0:
                idxs = [idx for idx,obj in enumerate(self.helices)]
                if len(idxs)!=0:
                    single_OP(myfile,'LH','L_Helix',self.idx,idxs)
                    single_OP(myfile,'RH','R_Helix',self.idx,idxs)
                idxs = [idx-self.helices[0].ind for idx in self.seam_vhs]
                if len(idxs)!=0:
                    single_OP(myfile,'HLX','Helix',self.idx,idxs)
        if len(self.seam_doms)!=0:
            idxs = [obj.ind for obj in self.domains if obj.idxHigh <= self.seam_idxs[0]]
            if len(idxs)!=0:
                single_OP(myfile,'DOM','Left_Domains',self.idx,idxs)
            idxs = [obj.ind for obj in self.domains if obj.idxLow >= self.seam_idxs[1]]
            if len(idxs)!=0:
                single_OP(myfile,'DOM','Right_Domains',self.idx,idxs)
        if len(self.domain_sizes) > 1:
            for name, idxs in self.domain_sizes.items():
                single_OP(myfile, 'DOM', name, self.idx, idxs)
        col_numbers = []
        for col, idxs in self.col_idxs.items():
            col_numbers.append(idxs[0])
            col_numbers.append(idxs[1])
        for col_id in col_numbers:
            idxs = [obj.ind for obj in self.crossovers if obj.idx1 == col_id and obj.idx2 == col_id]
            if len(idxs) != 0: single_OP(myfile, 'CR', 'Column_'+str(col_id), self.idx, idxs)
        if len(self.crossovers)!=0:
            for helix in self.helices:
                idxs = [obj.ind for obj in helix.domains]
                single_OP(myfile, 'DOM', 'Row_'+str(helix.ind), self.idx, idxs)
        idxs = [obj.ind for obj in self.cross_pairs]
        if len(idxs) != 0: single_OP(myfile, 'CRPair', 'CrossPairs', self.idx, idxs)
        idxs = [obj.ind for obj in self.cross_pairs if obj.type == 's']
        if len(idxs) != 0: single_OP(myfile, 'CRPair', 'Seam_CrossPairs', self.idx, idxs)
        idxs = [obj.ind for obj in self.cross_pairs if obj.type == 'i']
        if len(idxs) != 0: single_OP(myfile, 'CRPair', 'Inside_CrossPairs', self.idx, idxs)
        idxs = [obj.ind for obj in self.cross_pairs if obj.type == 'o']
        if len(idxs) != 0: single_OP(myfile, 'CRPair', 'Outside_CrossPairs', self.idx, idxs)
        idxs = [obj.ind for obj in self.cross_pairs if obj.type == 'l']
        if len(idxs) != 0: single_OP(myfile, 'CRPair', 'Long_CrossPairs', self.idx, idxs)
    def write_OP_Oct19(self,out_dir,name):
        with open(out_dir+name+'_OP.txt','w') as myfile:
            self.help_OPs(myfile)


if __name__ == '__main__':
    file_path = '/Users/behnamnajafi/Code/DLM/DLM2/Run/Input/JSONs/RcU.json'
    pool = Pool(file_path)
