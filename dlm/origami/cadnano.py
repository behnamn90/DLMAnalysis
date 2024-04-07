import json
import pandas as pd
import matplotlib.pyplot as plt
import warnings

def parse_json_data(vstrands_data):
    dfs = []
    for vstrand in vstrands_data:
        df = pd.DataFrame({'scaf': vstrand['scaf'], 'stap': vstrand['stap']})
        df['num'] = vstrand['num']
        df['skip'] = vstrand['skip']
        df = df.reset_index().rename(columns={'index': 'col_idx'})
        dfs.append(df)
    DF = pd.concat(dfs, axis=0)
    DF = DF.loc[~DF.apply(lambda row: any(row.apply(lambda x: x == [-1,-1,-1,-1])), axis=1)]
    DF = DF.reset_index(drop=True)
    scaffold_df = DF.pivot(index='num', columns='col_idx', values='scaf')
    staple_df = DF.pivot(index='num', columns='col_idx', values='stap')
    skip_df = DF.pivot(index='num', columns='col_idx', values='skip')
    return scaffold_df, staple_df, skip_df

def get_staple_colors(vstrands_data, staple_paths):
    start_colors = {}
    for vstrand in vstrands_data:
        row = vstrand['num']
        for domain_to_color in vstrand['stap_colors']:
            assert len(domain_to_color) == 2, 'Domain should have 2 elements'
            col, color = domain_to_color
            start_colors[(row, col)] = color
    staple_starts = [path[0] for path in staple_paths]
    assert staple_starts == list(start_colors.keys()), 'Staple starts and color starts do not match'
    # cadnano gives numbers that I want to map to colors
    cadnano_numbers = list(start_colors.values())  # Your original list of numbers
    unique_numbers = set(cadnano_numbers)
    # Predefined list of colors
    colors = ['red', 'green', 'blue', 'yellow', 'orange', 'purple', 'brown', 'pink']
    # Ensure there are enough colors for the unique numbers
    assert len(colors) >= len(unique_numbers), "Not enough colors for unique numbers"
    # Mapping unique numbers to colors
    number_to_color = {number: color for number, color in zip(unique_numbers, colors)}
    # Create the final list of colors corresponding to the original list of numbers
    final_colors_list = [number_to_color[number] for number in cadnano_numbers]
    return final_colors_list

def follow_path(df, start):
    path = [start]
    current = start
    while True:
        cell_value = df.loc[current]
        if cell_value[2:] == [-1, -1]:  # Check if it's the end of the path
            break
        next_step = tuple(cell_value[2:])
        if next_step in path:  # Prevent looping indefinitely
            break
        path.append(next_step)
        current = next_step
    return path


class Cadnano:
    def __init__(self):
        self._json_file_path = None
        self._json_file_name = None
        self._scaffold_df = None
        self._staple_df = None
        self._skip_df = None
        self._scaffold_path = None
        self._staple_paths = None
        self._staple_colors = None

    ### Constructors ###
    @classmethod
    def from_json(cls, file_path):
        instance = cls()
        instance.json_file_path = file_path
        with open(file_path, 'r') as file:
            data = json.load(file)
        instance._json_file_name = data['name']
        if instance._json_file_name != instance.json_file_path.split("/")[-1]:
            warnings.warn('File name and path do not match', UserWarning)
        instance._scaffold_df, instance._staple_df, instance._skip_df = parse_json_data(data['vstrands'])
        instance._scaffold_path, instance._staple_paths = instance.get_oligo_paths()
        instance._staple_colors = get_staple_colors(data['vstrands'], instance._staple_paths)
        instance._nucleotide_map = instance.get_nucleotide_map()
        return instance
    # end def

    def get_oligo_paths(self):
        scaffold_starts = self._scaffold_df.map(lambda x: x[:2] == [-1, -1]).stack()[lambda x: x].index.tolist()
        scaffold_paths = [follow_path(self._scaffold_df, start) for start in scaffold_starts]
        assert len(scaffold_paths) == 1, 'There should be only one scaffold path'
        staple_starts = self._staple_df.map(lambda x: x[:2] == [-1, -1]).stack()[lambda x: x].index.tolist()
        staple_paths = [follow_path(self._staple_df, start) for start in staple_starts]
        return scaffold_paths[0], staple_paths
    # end def

    def get_nucleotide_map(self):
        nucleotide_map = {}
        skip_locations = set(self._skip_df.stack()[lambda x: x==-1].index.tolist())
        nuc = 0
        for location in self._scaffold_path:
            if location in skip_locations:
                nucleotide_map[location] = -1
            else:
                nucleotide_map[location] = nuc
                nuc += 1
        return nucleotide_map
    # end def

    ### Getters ###
    @property
    def json_file_path(self):
        return self._json_file_path
    # end def

    @property
    def scaffold_df(self):
        return self._scaffold_df
    # end def

    @property
    def staple_df(self):
        return self._staple_df
    # end def

    @property
    def skip_df(self):
        return self._skip_df
    # end def

    ### Setters ###
    @json_file_path.setter
    def json_file_path(self, value):
        if value and isinstance(value, str):
            self._json_file_path = value
        else:
            raise ValueError("file_path must be a non-empty string.")
    # end def

    ### Methods ###
    def draw(self, ax):
        print(self._staple_paths)
        for i, staple_path in enumerate(self._staple_paths):
            color = self._staple_colors[i]
            for pair in zip(staple_path[:-1], staple_path[1:]):
                x1, y1 = pair[0][1], pair[0][0]
                x2, y2 = pair[1][1], pair[1][0]
                ax.plot([x1, x2], [y1, y2], color=color)
    # end def

if __name__ == '__main__':
    file_path = '/Users/behnamnajafi/Code/DLM/DLM2/Run/Input/JSONs/RcUa4x4.json'
    cadnano = Cadnano.from_json(file_path)
    
