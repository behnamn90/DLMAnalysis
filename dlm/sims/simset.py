from dlm.sims.simulation import Simulation
from itertools import product
import os

def find_simulation_paths_with_output(root_dir):
    simulations_with_output = set()
    for root, dirs, files in os.walk(root_dir, topdown=True):
        # If 'Output' is found in the subdirectories
        if 'Output' in dirs:
            # Get the parent directory of the current directory (root)
            parent_of_output = os.path.dirname(root)
            # Add the parent directory to the set
            simulations_with_output.add(parent_of_output)
            # To stop exploring further in this branch including the parent, modify dirs
            # Find the index of the parent directory in the path to modify dirs accordingly
            parent_index = root.split(os.sep).index(parent_of_output.split(os.sep)[-1])
            dirs[:] = [d for d in dirs if root.split(os.sep)[parent_index] != d]
            continue

    # Corrects for cases where there is an 'Output' folder in the root directory
    root_dir_output_folder = '/'.join(root_dir.split('/')[:-1])
    simulations_with_output.remove(root_dir_output_folder)

    return list(simulations_with_output)

input_dictionary_dtypes = {
        'RootDir' : str, 
        'DirStructure' : list, # list of strings
        'RateMethod': list, # list of strings
        'Scaffold' : list, # list of strings
        'k_plus' : list, # list of strings
        'Topology' : list, # list of strings
        'RateModel' : list, # list of strings
        'Conc' : list, # list of strings
        'PRot' : list, # list of strings
        'SRot' : list, # list of strings
        'Gamma' : list, # list of strings
        'n_param' : list, # list of strings
        'Missing' : list, # list of strings
        'Ramp' : list, # list of 2-tuples
        'Temp' : list, # list of 2-tuples
        'US' : list, # list of strings
        'Window' : list, # list of strings
        'Weight' : list, # list of strings
        'Cluster' : list, # list of strings
        'Seed' : list # list of strings
        }

def validate_input_dictionary_dtypes(d, dtypes = input_dictionary_dtypes):
    for key, expected_type in dtypes.items():
        # Retrieve the actual value from d
        actual_value = d.get(key)
        # Check if the type of the actual value matches the expected type
        if not isinstance(actual_value, expected_type):
            raise TypeError(f"Type mismatch for key '{key}': expected {expected_type}, got {type(actual_value)}")
    return True

def generate_combinations(d, skip_keys = ['RootDir', 'DirStructure', 'Seed']):
    # Filter the keys for which combinations need to be generated
    combo_keys = {k: v for k, v in d.items() if k not in skip_keys and isinstance(v, list)}
    # Generate all combinations of the filtered keys
    all_combos = product(*(combo_keys[k] for k in combo_keys))
    # Create new dictionaries for each combination
    result_dictionaries = []
    for combo in all_combos:
        new_dict = {k: v for k, v in zip(combo_keys.keys(), combo)}
        for key in skip_keys:
            new_dict[key] = d[key]
        result_dictionaries.append(new_dict)
    return result_dictionaries

def get_compare_keys(d, skip_keys = ['RootDir', 'DirStructure', 'Seed'], 
                     rename_dict = {'Ramp': 'SimType', 'Temp': 'TempRate'}):
    compare_keys = [k for k in d.keys() if k not in skip_keys and len(d[k])>1]
    return [rename_dict.get(item, item) for item in compare_keys]

def recombine_dictionaries(dicts, skip_keys = {'RootDir', 'DirStructure'}):
    """
    Recombines a list of dictionaries into a single dictionary, excluding specified keys.
    Useful for getting a super-dictionary from a list of simulation dictionaries.
    Mainly for use when generating simulations from a directory rather than a dictionary.
    Note: if used to generate simulations, it will create simulations that don't exist.
    Note: there is no possible way to get multiple simset dictionaries back so this is what we have.
    Note: Can also be used to combine dictionaries from smaller simsets into a larger simset.
    
    Args:
        dicts (list): A list of dictionaries to be recombined.
        skip_keys (set, optional): A set of keys to be excluded from the recombined dictionary. Defaults to {'RootDir', 'DirStructure'}.

    Returns:
        dict: The recombined dictionary.

    """
    recombined_dict = {k:v for k, v in dicts[0].items() if k in skip_keys}
    # For all other keys, use sets to collect unique values
    for d in dicts:
        for key, value in d.items():
            if key not in skip_keys:
                if key not in recombined_dict:
                    recombined_dict[key] = set()
                if isinstance(value, list):
                    recombined_dict[key].update(set(value))
                else:
                    recombined_dict[key].add(value)

    # Convert sets back to lists for non-skip_keys
    for key in recombined_dict:
        if key not in skip_keys:
            recombined_dict[key] = list(recombined_dict[key])

    return recombined_dict

class SimulationSet:
    def __init__(self):
        self._simulations = []
        self._dictionary = dict()
        self._super_dictionary = dict() # dictionary of recombined paths
        self._compared_keys = []
        self._name = ''

        self._RootDir = '' # includes the code version on hydra
        self._DirStructure = []  # specifies the order of other keys in the directory structure
        self._RateMethod = []
        self._Scaffold = []
        self._k_plus = []
        self._Topology = []  
        self._RateModel = []  
        self._Conc = []
        self._PRot = []  
        self._SRot = []  
        self._Gamma = []  
        self._n_param = []  
        self._Missing = []
        self._Ramp = []
        self._Temp = []
        self._US = []
        self._Window = []  
        self._Weight = []  
        self._Cluster = []
        self._Seed = []
        
    @classmethod
    def from_dictionary(cls, d: 'dict') -> 'SimulationSet':
        """
        Create a SimulationSet instance from a dictionary.

        Args:
            d (dict): A dictionary containing the simulation parameter combinations.

        Returns:
            SimulationSet: An instance of the SimulationSet class.
        """
        validate_input_dictionary_dtypes(d)
        instance = cls()
        instance._dictionary = {k: v for k, v in d.items()}
        skip_keys = ['RootDir', 'DirStructure', 'Seed']
        for ss_dict in generate_combinations(d, skip_keys=skip_keys):
            instance._simulations.append(Simulation.from_dict(ss_dict))
        instance._super_dictionary = dict(instance._dictionary)
        default_compare_keys = get_compare_keys(instance._super_dictionary, skip_keys=skip_keys)
        instance.set_compare_keys_and_names(default_compare_keys)

        return instance
    
    @classmethod
    def from_dictionaries(cls, dicts: 'list') -> 'SimulationSet':
        """
        Create a SimulationSet instance from a list of dictionaries.

        Args:
            dicts (list): A list of dictionaries containing the simulation parameter combinations.

        Returns:
            SimulationSet: An instance of the SimulationSet class.
        """
        instance = cls()
        for d in dicts:
            validate_input_dictionary_dtypes(d)
            instance._dictionary = {k: v for k, v in d.items()}
            skip_keys = ['RootDir', 'DirStructure', 'Seed']
            for ss_dict in generate_combinations(d, skip_keys=skip_keys):
                instance._simulations.append(Simulation.from_dict(ss_dict))
        instance._super_dictionary = recombine_dictionaries(dicts)
        default_compare_keys = get_compare_keys(instance._super_dictionary, skip_keys=skip_keys)
        instance.set_compare_keys_and_names(default_compare_keys)
        return instance
    
    @classmethod
    def from_hydra_path(cls, root_dir: 'str') -> 'SimulationSet':
        instance = cls()
        simulation_paths_with_output = find_simulation_paths_with_output(root_dir)
        instance._simulations = [Simulation.from_hydra_path(p) for p in simulation_paths_with_output]
        instance._dictionary = None
        instance._super_dictionary = recombine_dictionaries([sim.dictionary for sim in instance._simulations])
        return instance

    def set_compare_keys_and_names(self, keys):
        self._compared_keys = keys
        self._name = '_'.join(keys)
        for sim in self._simulations:
            sim.set_reduced_name(keys)

    @property
    def super_dictionary(self):
        return self._super_dictionary


if __name__ == '__main__':
    from dlm.defs.hydra import default_dir_structure, june19_dir_structure
    sample_dict = {
        'RootDir' : '/Volumes/Sam980/Hydra/June19',
        'DirStructure' : june19_dir_structure,
        'RateMethod': ['custom'],
        'Scaffold' : ['average', 'PUC', 'PJB'],
        'k_plus' : ['1000'],
        'Topology' : ['RcUa'],
        'RateModel' : ["local"],
        'Conc' : ['C100'],
        'PRot' : ["R0"],
        'SRot' : ["S0"],
        'Gamma' : ["2.5"],
        'n_param' : ["2"],
        'Missing' : ["M0"],
        'Ramp' : [('empty', 'anneal'), ('coated', 'melt')],
        'Temp' : [('65', 'nan')],
        'US' : ['false'],
        'Window' : ['W0'],
        'Weight' : ['w0'],
        'Cluster' : ["false"],
        'Seed' : [str(i) for i in range(1,20)]}
    sample_dict2 = {
        'RootDir' : '/Volumes/Sam980/Hydra/June19',
        'DirStructure' : june19_dir_structure,
        'RateMethod': ['custom'],
        'Scaffold' : ['average', 'PJB'],
        'k_plus' : ['1000'],
        'Topology' : ['RcUa'],
        'RateModel' : ["local"],
        'Conc' : ['C100','C200','C300'],
        'PRot' : ["R0"],
        'SRot' : ["S0"],
        'Gamma' : ["2.5"],
        'n_param' : ["2"],
        'Missing' : ["M0"],
        'Ramp' : [('empty', 'anneal'), ('coated', 'melt')],
        'Temp' : [('65', 'nan')],
        'US' : ['false'],
        'Window' : ['W0'],
        'Weight' : ['w0'],
        'Cluster' : ["false"],
        'Seed' : [str(i) for i in range(1,30)]}

    simset = SimulationSet.from_dictionaries([sample_dict,sample_dict2])
    #simset = SimulationSet.from_hydra_path('/Volumes/Sam980/Hydra/June19')
    simset = SimulationSet.from_dictionary(sample_dict)
    print(len(simset._simulations))
    print(simset.super_dictionary)
    #print(len(simset._simulations))
    #print(simset.super_dictionary)
    #print(simset._simulations[0]._dictionary['Seed'])
    #print(len(dirs))
    #for sim in dirs:
        #print(sim)


