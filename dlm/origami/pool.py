import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from collections import OrderedDict

from cadnano import Cadnano
from helix import Helix
from staple import Staple
from domain import Domain
from crossover import Crossover


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

    def __init__(self, json_file_path):
        self._json_file_path = json_file_path
        self._cadnano = Cadnano.from_json(json_file_path)
        self._helices = self.add_helices()
        self._staples, self._domains, self._crossovers = list(), list(), list()
        self.create_objects()
        self.fill_domain_attributes()

    def add_helices(self):
        """
        Adds the helices to the pool.

        Returns:
            list: A list of Helix objects representing the helices in the origami structure.
        """
        helices = []
        nuc_df = self._cadnano.nucleotide_df
        for index, row in nuc_df.iterrows():
            helices.append(Helix(index, [nuc for nuc in row.tolist() if nuc != -1]))
        return helices

    def create_objects(self):
        """
        Creates the staples, domains, and crossovers in the pool by following the path of each staple.
        """
        staple_paths = self._cadnano.staple_paths
        cross_df = self._cadnano.staple_crossover_df
        seam_df = self._cadnano.seam_df
        for staple_index, staple_path in enumerate(staple_paths):
            staple = Staple(staple_index, staple_path)
            cross_positions = [pos for pos in staple_path if cross_df.loc[pos] or seam_df.loc[pos]]
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
            for i in range(0, len(cross_position_indices), 2):
                start, end = (cross_position_indices[i], cross_position_indices[i+1])
                crossover_path = staple_path[start:end+1]
                crossover = Crossover(crossover_path, crossover_staple_index, is_long=False)
                crossover_staple_index += 1
                self._crossovers.append(crossover)
                staple.add_crossover(crossover)
            if len(cross_position_indices) == 4:
                start, end = (cross_position_indices[0], cross_position_indices[3])
                crossover_path = (staple_path[start], staple_path[end])
                crossover = Crossover(crossover_path, crossover_staple_index, is_long=True)
                crossover_staple_index += 1
                self._crossovers.append(crossover)
                staple.add_crossover(crossover)
            self._staples.append(staple)

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
            domain_length = ring_distance(nuc5p, nuc3p, scaffold_length)
            is_at_seam = any([seam_df.loc[pos5p], seam_df.loc[pos3p]])
            is_edge = any([edge_df.loc[pos5p], edge_df.loc[pos3p]])
            if is_at_seam:
                domain_type = 's'
            if is_edge:
                domain_type = 'e'
            domain.set_nucs(nuc5p, nuc3p)
            domain.set_length(domain_length)
            domain.set_domain_type(domain_type)

        self._domains.sort(key=lambda domain: domain.n1)
        for i, domain in enumerate(self._domains):
            domain.set_index_on_scaffold(i)

    @property
    def json_file(self):
        """
        Returns the path of the JSON file associated with this object.

        Returns:
            str: The path of the JSON file.
        """
        return self._json_file_path

    @property
    def helices(self):
        """
        Returns the helices of the pool.

        Returns:
            list: A list of Helix objects.
        """
        return self._helices





if __name__ == '__main__':
    file_path = '/Users/behnamnajafi/Code/DLM/DLM2/Run/Input/JSONs/RcS.json'
    pool = Pool(file_path)
