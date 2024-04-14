from dlm.sims.seed import Seed
from dlm.defs.hydra import default_dir_structure, july19_dir_structure, june19_dir_structure
from dlm.defs.hydra import SetX
import os

def find_seeds_with_output(path):
    seeds_with_output = []  # List to store directories with an 'Output' subdirectory
    # Check each item in the directory specified by 'path'
    for entry in os.listdir(path):
        # Construct the full path to the item
        full_path = os.path.join(path, entry)
        # Check if the item is a directory
        if os.path.isdir(full_path):
            # Check if this directory contains a subdirectory named 'Output'
            output_path = os.path.join(full_path, 'Output')
            if os.path.isdir(output_path):
                # If 'Output' directory exists, add the directory name to the list
                seeds_with_output.append(entry)
    return sorted(seeds_with_output, key=int)


class Simulation:
    def __init__(self):
        self._dictionary = dict()
        self._path = ''
        self._full_name = ''
        self._reduced_name = ''
        self._seeds = []

        self._reduced_name = ''

        self._RootDir = '' # includes the code version on hydra
        self._DirStructure = []  # specifies the order of other keys in the directory structure
        self._RateMethod = ''  
        self._Scaffold = ''  
        self._k_plus = ''  
        self._Topology = ''  
        self._RateModel = ''  
        self._Conc = ''  
        self._PRot = ''  
        self._SRot = ''  
        self._Gamma = ''  
        self._n_param = ''  
        self._Missing = ''  
        self._Ramp = ()  
        self._Temp = ()
        self._US = '' 
        self._Window = ''  
        self._Weight = ''  
        self._Cluster = ''
        self._Seed = []

        # these appear in path but not in the dictionary
        self._Init = ''
        self._SimType = ''
        self._TempRate = ''
        self._dT = ''

    @classmethod
    def from_dict(cls, d: 'dict[str, str]') -> 'Simulation':
        """
        Create a Simulation instance from a dictionary.

        Args:
            d (dict[str, str]): A dictionary containing the simulation information.

        Returns:
            Simulation: An instance of the Simulation class.

        Raises:
            ValueError: If the dictionary does not contain the correct keys.
        """
        if set(d.keys()) != set(SetX.keys()):
            raise ValueError('The dictionary does not contain the correct keys.')
        instance = cls()
        instance._dictionary = {k: v for k, v in d.items() if k not in ['DirStructure', 'RootDir']}
        for key, val in d.items():
            setattr(instance, '_'+key, val)
        # set dependent variables
        instance._Init = instance._Ramp[0]
        instance._SimType = instance._Ramp[1]
        instance._TempRate = instance._Temp[0]
        instance._dT = instance._Temp[1]
        instance._path = '/'.join([instance._RootDir] + [instance.__getattribute__(key) for key in instance._DirStructure[:-1]])
        instance._full_name = '_'.join([instance.__getattribute__(key) for key in default_dir_structure[:-1]])
        instance._seeds = instance.add_seeds_by_parent()
        return instance
    
    @classmethod
    def from_hydra_path(cls, path: 'str') -> 'Simulation':
        """
        Create a Simulation instance from a Hydra type path.

        Args:
            path (str): of the type '/Volumes/Sabrent/Hydra/July19/...'

        Returns:
            Simulation: An instance of the Simulation class.
        """
        instance = cls()
        instance._path = path
        split_path = path.split('/')
        instance._RootDir = '/'.join(split_path[0:5])
        actual_dir_structure = None
        dir_structures = [default_dir_structure[:-1], july19_dir_structure[:-1], june19_dir_structure[:-1]]
        for dir_structure in dir_structures:
            if len(split_path[5:]) == len(dir_structure):
                actual_dir_structure = dir_structure
                break
        if actual_dir_structure is None:
            raise ValueError('Could not parse path: ' + path)
        else:
            instance._DirStructure = actual_dir_structure
        instance._dictionary = {key: val for key, val in zip(instance._DirStructure, split_path[5:])}
        if 'k_plus' not in instance._DirStructure:
            instance._dictionary['k_plus'] = '500'
        if 'RateMethod' not in instance._DirStructure:
            instance._dictionary['RateMethod'] = 'custom'
        for key, val in instance._dictionary.items():
            setattr(instance, '_'+key, val)
        seeds_dirs = find_seeds_with_output(path)
        instance._dictionary['Seed'] = seeds_dirs
        instance._Ramp = (instance._Init, instance._SimType)
        instance._Temp = (instance._TempRate, instance._dT)
        instance._dictionary['Ramp'] = instance._Ramp
        instance._dictionary['Temp'] = instance._Temp
        instance._dictionary = {k:v for k,v in instance._dictionary.items() if k not in ['Init', 'SimType', 'TempRate', 'dT']}
        instance._full_name = '_'.join([instance.__getattribute__(key) for key in default_dir_structure[:-1]])
        instance._seeds = instance.add_seeds_by_parent()
        return instance

    def add_seeds_by_parent(self):
        sims = []
        for seed in self._dictionary['Seed']:
            sims.append(Seed.from_parent(self,seed))
        return sims

    def add_seeds_by_dicts(self):
        sims = []
        for seed in self._dictionary['Seed']:
            newDict = dict(self._dictionary)
            newDict['Seed'] = seed
            sims.append(Seed.from_dict(newDict))
        return sims
    
    def set_name(self, comps):
        self._reduced_name = '_'.join(self.__getattribute__(key) for key in comps)

    @property
    def path(self):
        return self._path
    @property
    def full_name(self):
        return self._full_name
    @property
    def seeds(self):
        return self._seeds
    @property
    def Set(self):
        return self._dictionary
    @property
    def RootDir(self):
        return self._RootDir
    @property
    def DirStructure(self):
        return self._DirStructure
    
    @property
    def name(self):
        return self._reduced_name
    
    @property
    def RateMethod(self):
        return self._RateMethod
    @property
    def Scaffold(self):
        return self._Scaffold
    @property
    def k_plus(self):
        return self._k_plus
    @property
    def Topology(self):
        return self._Topology
    @property
    def RateModel(self):
        return self._RateModel
    @property
    def Conc(self):
        return self._Conc
    @property
    def PRot(self):
        return self._PRot
    @property
    def SRot(self):
        return self._SRot
    @property
    def Gamma(self):
        return self._Gamma
    @property
    def n_param(self):
        return self._n_param
    @property
    def Missing(self):
        return self._Missing
    @property
    def Ramp(self):
        return self._Ramp
    @property
    def Temp(self):
        return self._Temp
    @property
    def US(self):
        return self._US
    @property
    def Window(self):
        return self._Window
    @property
    def Weight(self):
        return self._Weight
    @property
    def Cluster(self):
        return self._Cluster
    @property
    def Seed(self):
        return self._Seed
    @property
    def Init(self):
        return self._Init
    @property
    def SimType(self):
        return self._SimType
    @property
    def TempRate(self):
        return self._TempRate
    @property
    def dT(self):
        return self._dT
    
    @property
    def code_vers(self):
        return self._RootDir.split('/')[-1]

    

if __name__ == '__main__':
    sample_path = '/Volumes/Sam980/Hydra/June19/average/RcUa/local/C100/R0/S0/2.5/2/M0/empty/anneal/1/30/false/W0/w0/false'
    sim = Simulation.from_hydra_path(sample_path)
    sample_dict = {
        'RootDir': '/Volumes/Sam980/Hydra/June19',
        'DirStructure': ['Scaffold', 'Topology', 'RateModel', 'Conc', 'PRot', 'SRot', 'Gamma', 'n_param', 'Missing', 'Init', 'SimType', 'TempRate', 'dT', 'US', 'Window', 'Weight', 'Cluster'],
        'Scaffold': 'average',
        'Topology': 'RcUa',
        'RateModel': 'local',
        'Conc': 'C100',
        'PRot': 'R0',
        'SRot': 'S0',
        'Gamma': '2.5',
        'n_param': '2',
        'Missing': 'M0',
        'US': 'false',
        'Window': 'W0',
        'Weight': 'w0',
        'Cluster': 'false',
        'k_plus': '500',
        'RateMethod': 'custom',
        'Ramp': ('empty', 'anneal'),
        'Temp': ('1', '30'),
        'Seed': [str(i) for i in range(1, 61)]
    }
    sim = Simulation.from_dict(sample_dict)

    #print(sim._RootDir)
    print(sim.full_name)
    print([seed.Seed for seed in sim.seeds])
    for seed in sim.seeds:
        print(seed.full_name)
    #print(sim.path)
    #print(sim.Set)
    #print([seed.full_name for seed in sim.seeds])