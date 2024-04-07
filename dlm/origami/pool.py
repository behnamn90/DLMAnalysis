import numpy as np
import matplotlib
import matplotlib.pyplot as plt


import networkx as nx

from .general import XY_SCALE, op_dict, default_colours, draw

from ..common.myfuncs import circ_subtract, circ_add

from .endpoints import Endpoints
from .helix import Helix
from .vertex import Vertex
from .domain import Domain
from .crossover import Crossover
from .crosspair import CrossPair
from .staple import Staple
from .cadnano import Cadnano

here_path = os.getcwd()
Scaff_length = 50

def seam_lengths(strand,seam_idxs, seam_vhs):
    a , b = strand.lowIdx(), seam_idxs[0]
    c , d = seam_idxs[1] , strand.highIdx()
    # The left (l1) and right (l2) lengths
    l1 = b-a+1 + strand.insertionLengthBetweenIdxs(a,b)
    l2 = d-c+1 + strand.insertionLengthBetweenIdxs(c,d)
    # double check that it is a seam
    if a < b and c < d and strand.strandSet().idNum() in seam_vhs:
        return (l1,l2)
    else:
        print('Non seam passed to seam_lengths function!')
        return None
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


class Pool:
    def __init__(self, json_file_path):
        self._json_file_path = json_file_path
        self._cadnano = Cadnano.from_json(json_file_path)



if __name__ == '__main__':
    file_path = '/Users/behnamnajafi/Code/DLM/DLM2/Run/Input/JSONs/RcUa4x4.json'
    pool = Pool(file_path)