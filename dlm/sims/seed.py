from dlm.defs.general import scaffold_file_names, Limits
from dlm.defs.hydra import default_dir_structure, july19_dir_structure, june19_dir_structure
from dlm.defs.hydra import parse_hydra_path
from dlm.defs.hydra import SetX

input_dictionary_keys = list(SetX.keys())

class Seed:
    def __init__(self):
        self._dictionary = dict()
        self._path = ''
        self._full_name = ''
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
        self._Ramp = () # tuple
        self._Temp = () # tuple  
        self._US = '' 
        self._Window = ''  
        self._Weight = ''  
        self._Cluster = '' 
        self._Seed = ''  

        self._Init = ''
        self._SimType = ''
        self._TempRate = ''
        self._dT = ''

        self.input_file = "input.py"
        self.missing_file = "Missing.txt"
        self.conc_file = "concentrations.txt"
        self.energy_file = "energies.txt"
        self.weight_file = "w_file.txt"
        self.stat_file = 'Output/Statistics.dat'
        self.time_file = 'Output/In_times.dat'
        self.hist_file = 'Output/Hist_last.dat'
        self.hist_file2d = 'Output/2DHist_last.dat'

    @classmethod
    def from_dict(cls, d: 'dict[str, str]') -> 'Seed':
        """
        Create a Seed instance from a dictionary.

        Args:
            d (dict[str, str]): A dictionary containing the seed information.

        Returns:
            Seed: An instance of the Seed class.

        Raises:
            ValueError: If the dictionary does not contain the correct keys.
        """
        if set(d.keys()) != set(SetX.keys()):
            raise ValueError('The dictionary does not contain the correct keys.')
        instance = cls()
        for key, val in d.items():
            setattr(instance, '_'+key, val)
        instance._dictionary = {k: v for k, v in d.items() if k not in ['DirStructure', 'RootDir']}
        # set dependent variables
        instance._Init = instance._Ramp[0]
        instance._SimType = instance._Ramp[1]
        instance._TempRate = instance._Temp[0]
        instance._dT = instance._Temp[1]
        instance.set_dependent_variables()
        instance._path = '/'.join([instance._RootDir] + [instance.__getattribute__(key) for key in instance._DirStructure])
        instance._full_name = '_'.join([instance.__getattribute__(key) for key in default_dir_structure])
        return instance

    @classmethod
    def from_hydra_path(cls, path: str) -> 'Seed':
        """
        Create a Seed instance from a Hydra type path.

        Args:
            cls: The class object.
            path (str): of the type '/Volumes/Sabrent/Hydra/July19/...'

        Returns:
            An instance of the Seed class.

        """
        instance = cls()
        instance._path = path
        split_path = path.split('/')
        instance._RootDir = '/'.join(split_path[0:5])
        actual_dir_structure = None
        dir_structures = [default_dir_structure, july19_dir_structure, june19_dir_structure]
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
        # set dependent variables
        instance._Ramp = (instance._Init, instance._SimType)
        instance._Temp = (instance._TempRate, instance._dT)
        instance._dictionary['Ramp'] = instance._Ramp
        instance._dictionary['Temp'] = instance._Temp
        instance._dictionary = {k:v for k,v in instance._dictionary.items() if k not in ['Init', 'SimType', 'TempRate', 'dT']}
        instance.set_dependent_variables()
        instance._full_name = '_'.join([instance.__getattribute__(key) for key in default_dir_structure])
        return instance

    @classmethod
    def from_parent(cls, simulation, seed_number: str) -> 'Seed':
        """
        Create a new instance of the Seed class from a parent simulation.

        Args:
            cls: The class object.
            simulation: The parent simulation object.
            seed_number: The seed number.

        Returns:
            A new instance of the Seed class.

        """
        instance = cls()
        instance._dictionary = simulation.Set
        instance._dictionary['Seed'] = seed_number
        for key, val in instance._dictionary.items():
            setattr(instance, '_'+key, val)
        instance._RootDir = simulation.RootDir
        instance._DirStructure = simulation.DirStructure
        instance._path = '/'.join([simulation.path, seed_number])
        instance._full_name = '_'.join([simulation.full_name, seed_number])
        # set dependent variables
        instance._Init = instance._Ramp[0]
        instance._SimType = instance._Ramp[1]
        instance._TempRate = instance._Temp[0]
        instance._dT = instance._Temp[1]
        instance.set_dependent_variables()
        return instance

    def set_dependent_variables(self):
        if self._Scaffold in ['PUC', 'PJB101', 'PJB103', 'PJB']:
            self.SeqDep = 'seq'
        elif self._Scaffold in ['PUCaverage']:
            self.SeqDep = 'custom'
        else:
            self.SeqDep = self.Scaffold  # could be: custom, average
        self.scaffold_file = scaffold_file_names[self._Scaffold]
        self.topology_file = self._Topology+'.top'
        self.op_file = self._Topology+"_OP.txt"
        self.conf_file = ""
        if (self._Init == 'conf_file'):
            self.conf_file = self._Topology+"_"+str(int((Limits[self._Topology][self._Window]["High"]+Limits[self._Topology][self._Window]["Low"])/2))+"_D.conf"
    
    @property
    def Set(self):
        return self._dictionary
    
    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._reduced_name
    
    @property
    def full_name(self):
        return self._full_name
    
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

    
if __name__ == '__main__':
    sample_path = '/Volumes/Sam980/Hydra/June19/average/RcUa/local/C100/R0/S0/2.5/2/M0/empty/anneal/1/30/false/W0/w0/false/1'
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
        'Seed': '1'
    }
    seed = Seed.from_hydra_path(sample_path)
    seed = Seed.from_dict(sample_dict)
    print(seed._RootDir)
    print(seed.full_name)
    print(seed.path)
    print(seed.Set)
    print(seed.Init)