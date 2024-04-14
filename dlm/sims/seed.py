from dlm.defs.general import scaffold_file_names, Limits
from dlm.defs.hydra import default_dir_structure, july19_dir_structure, june19_dir_structure

input_dictionary_template = {
        'RootDir' : str, 
        'DirStructure' : list,
        'RateMethod': str,
        'Scaffold' : str,
        'k_plus' : str,
        'Topology' : str,
        'RateModel' : str,
        'Conc' : str,
        'PRot' : str,
        'SRot' : str,
        'Gamma' : str,
        'n_param' : str,
        'Missing' : str,
        'Ramp' : tuple,
        'Temp' : tuple,
        'US' : str,
        'Window' : str,
        'Weight' : str,
        'Cluster' : str,
        'Seed' : str}

def input_dictionary_is_valid(mydict, keytypes):
    # Check for missing keys
    missing_keys = [key for key in keytypes if key not in mydict]
    if missing_keys:
        raise ValueError(f"Missing keys: {missing_keys}")

    # Check for type mismatches
    type_mismatches = [
        key for key in mydict if not isinstance(mydict[key], keytypes.get(key))
    ]
    if type_mismatches:
        raise TypeError(f"Type mismatches for keys: {type_mismatches}")

    # If all keys are present and types match
    return True

def find_matching_directory_structure(input_dir_values, dir_structures = 
                                      [default_dir_structure, july19_dir_structure, june19_dir_structure]):
    """
    Finds the matching directory structure.
    If the number of elements match one of the predefined directory structures,
    then that structure is returned.
    Args:
        input_dir_values (str): list of strings made up of the split path after the root directory.
    """
    actual_dir_structure = None
    for dir_structure in dir_structures:
        if len(input_dir_values) == len(dir_structure):
            actual_dir_structure = dir_structure
            break
    if actual_dir_structure is None:
        raise ValueError('Could not match to any directory structure.')
    else:
        return actual_dir_structure

class Seed:
    def __init__(self):
        self._dictionary = dict()
        self._path = ''
        self._full_name = ''
        self._reduced_name = ''

        self._RootDir = '' # includes the code version on hydra
        self._DirStructure = []  # specifies the order of other keys in the directory structure
        self._RateMethod = ''  # must be specified for June19, July19-Oct19 paths. 
        self._Scaffold = ''  
        self._k_plus = ''  # must be specified for June19 paths.
        self._Topology = ''  
        self._RateModel = ''
        self._Conc = ''  
        self._PRot = ''  
        self._SRot = ''  
        self._Gamma = ''  
        self._n_param = ''  
        self._Missing = ''  
        self._Ramp = () # tuple in input dictionary but not in path
        self._Temp = () # tuple in input dictionary but not in path  
        self._US = '' 
        self._Window = ''  
        self._Weight = ''  
        self._Cluster = '' 
        self._Seed = ''  

        self._Init = '' # not in the input dictionary but in the path
        self._SimType = '' # not in the input dictionary but in the path
        self._TempRate = '' # not in the input dictionary but in the path
        self._dT = '' # not in the input dictionary but in the path

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
        if not input_dictionary_is_valid(d, input_dictionary_template):
            raise ValueError('The dictionary does not contain the correct keys.')
        instance = cls()
        instance._dictionary = {k: v for k, v in d.items()}
        instance._dictionary['Init'] = instance._dictionary['Ramp'][0]
        instance._dictionary['SimType'] = instance._dictionary['Ramp'][1]
        instance._dictionary['TempRate'] = instance._dictionary['Temp'][0]
        instance._dictionary['dT'] = instance._dictionary['Temp'][1]
        for key, val in instance._dictionary.items():
            setattr(instance, '_'+key, val)
        instance.set_dependent_variables()
        instance._path = '/'.join([instance._RootDir] + [instance._dictionary[key] for key in instance._DirStructure])
        instance._full_name = '_'.join([instance._dictionary[key] for key in default_dir_structure])
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
        instance._dictionary['RootDir'] = '/'.join(split_path[0:5])
        instance._dictionary['DirStructure'] = find_matching_directory_structure(split_path[5:])
        for key, val in zip(instance._dictionary['DirStructure'], split_path[5:]):
            instance._dictionary[key] = val
        if 'k_plus' not in instance._dictionary['DirStructure']:
            instance._dictionary['k_plus'] = '500'
        if 'RateMethod' not in instance._dictionary['DirStructure']:
            instance._dictionary['RateMethod'] = 'custom'
        instance._dictionary['Ramp'] = (instance._dictionary['Init'], instance._dictionary['SimType'])
        instance._dictionary['Temp'] = (instance._dictionary['TempRate'], instance._dictionary['dT'])
        for key, val in instance._dictionary.items():
            setattr(instance, '_'+key, val)
        instance.set_dependent_variables()
        instance._full_name = '_'.join([instance._dictionaty[key] for key in default_dir_structure])
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
        """
        Legacy method. Gives the reduced version of the dictionary.
        """
        return {k:v for k,v in self._dictionary.items() 
            if k not in ['DirStructure', 'RootDir', 'Init', 'SimType', 'TempRate', 'dT']}
    
    @property
    def dictionary(self):
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