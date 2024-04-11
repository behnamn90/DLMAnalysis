import json
import pandas as pd
import matplotlib.pyplot as plt
import warnings

def parse_json_data(vstrands_data):
    """
    Parse the JSON data of vstrands and return dataframes for scaffold, staple, and skip.
    Args:
        vstrands_data (list): A list of dictionaries containing vstrand data.
        - vstrand['scaf'] is a list of [from_helix, from_col, to_helix, to_col]
        - vstrand['stap'] is a list of [from_helix, from_col, to_helix, to_col]
        Each [from_helix, from_col, to_helix, to_col] location in the 2D list of vstrands_data is the grid point in cadnano.
        - vstrand['num'] is the row number of the vstrand in cadnano 
    Returns:
        tuple: A tuple containing three dataframes - scaffold_df, staple_df, and skip_df.
    """
    dfs = []
    for vstrand in vstrands_data:
        df = pd.DataFrame({'scaf': vstrand['scaf'], 'stap': vstrand['stap']})
        df['num'] = vstrand['num']
        df['skip'] = vstrand['skip']
        df = df.reset_index().rename(columns={'index': 'col_idx'})
        dfs.append(df)
    DF = pd.concat(dfs, axis=0)
    # Remove cells with no strands
    DF = DF.loc[~DF.apply(lambda row: any(row.apply(lambda x: x == [-1,-1,-1,-1])), axis=1)]
    DF = DF.reset_index(drop=True)
    scaffold_df = DF.pivot(index='num', columns='col_idx', values='scaf')
    staple_df = DF.pivot(index='num', columns='col_idx', values='stap')
    skip_df = DF.pivot(index='num', columns='col_idx', values='skip')
    return scaffold_df, staple_df, skip_df

def get_staple_colors(vstrands_data, staple_paths):
    """
    Get the colors corresponding to the staples in cadnano.

    Args:
        vstrands_data (list): List of vstrand data containing information about the vstrands.
        - vstrand[i]['stap_colors'] is a list of [column, color] for each staple that begins in the vstrand.
        staple_paths (list): List of staple paths.

    Returns:
        list: List of colors corresponding to the staple paths.

    Raises:
        AssertionError: If the column_to_color does not have 2 elements.
        AssertionError: If the staple starts from the found path do not match color starts from cadnano.
        AssertionError: If there are not enough colors for unique numbers specified by cadnano.
    """
    start_colors = {}
    for vstrand in vstrands_data:
        row = vstrand['num']
        for column_to_color in vstrand['stap_colors']:
            assert len(column_to_color) == 2, 'Column_to_color should have 2 elements'
            col, color = column_to_color
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
    """
    Follows a path in a DataFrame starting from a given position, which should be a scaffold or staple start.

    Args:
        df (DataFrame): The DataFrame containing the grid's in/out info about scaffold or staples.
        start (tuple): The starting position of the path.

    Returns:
        list: A list of tuples representing the path followed.

    """
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
    """
    Class representing a cadnano origami structure.

    Attributes:
        _json_file_path (str): The path to the JSON file.
        _json_file_name (str): The name of the JSON file.
        _scaffold_df (pandas.DataFrame): DataFrame representing the scaffold structure.
        _staple_df (pandas.DataFrame): DataFrame representing the staple structure.
        _skip_df (pandas.DataFrame): DataFrame representing the skip locations.
        _scaffold_path (list): List of locations in the scaffold path.
        _staple_paths (list): List of lists, each representing a staple path.
        _staple_colors (list): List of colors for each staple strand.
        _nucleotide_map (dict): Dictionary mapping each location to its corresponding nucleotide index.
        _scaffold_crossovers (pandas.DataFrame): DataFrame representing scaffold crossovers.
        _nucleotide_df (pandas.DataFrame): DataFrame containing nucleotide information for each location in the scaffold path.
        _seam_df (pandas.DataFrame): DataFrame representing scaffold crossovers with False values for edge crossovers.
        _edge_df (pandas.DataFrame): DataFrame representing scaffold crossovers with True values for edge crossovers.
        _staple_crossover_df (pandas.DataFrame): DataFrame indicating whether there is a staple crossover at each location.
        _vertex_df (pandas.DataFrame): DataFrame indicating whether there is a vertex at each location.
    """
    def __init__(self):
        self._json_file_path = None
        self._json_file_name = None
        self._scaffold_df = None
        self._staple_df = None
        self._skip_df = None
        self._scaffold_path = None
        self._staple_paths = None
        self._staple_colors = None
        self._nucleotide_map = None
        self._scaffold_crossovers = None
        self._nucleotide_df = None
        self._seam_df = None
        self._edge_df = None
        self._staple_crossover_df = None
        self._vertex_df = None

    ### Constructors ###
    @classmethod
    def from_json(cls, file_path):
        """
        Constructor to create an instance of the class from a JSON file.

        Args:
            cls: The class to create an instance of.
            file_path (str): The path to the JSON file.

        Returns:
            instance: An instance of the class.

        Raises:
            UserWarning: If the file name and path do not match.

        """
        instance = cls()
        instance.json_file_path = file_path
        with open(file_path, 'r') as file:
            data = json.load(file)
        instance._json_file_name = data['name']
        #if instance._json_file_name != instance.json_file_path.split("/")[-1]:
            #warnings.warn('File name and path do not match', UserWarning)
        instance._scaffold_df, instance._staple_df, instance._skip_df = parse_json_data(data['vstrands'])
        instance._scaffold_path, instance._staple_paths = instance.get_oligo_paths()
        #instance._staple_colors = get_staple_colors(data['vstrands'], instance._staple_paths)
        instance._nucleotide_map = instance.get_nucleotide_map()
        instance._nucleotide_df = instance.get_nucleotide_df()
        instance._seam_df, instance._edge_df = instance.get_scaffold_crossover_dfs()
        instance._staple_crossover_df = instance.get_staple_crossover_df()
        instance._vertex_df = instance.get_vertex_df()
        return instance
    # end def

    def get_oligo_paths(self):
        """
        Returns the scaffold and staple paths in the origami structure.

        Returns:
            tuple: A tuple containing the scaffold path and a list of staple paths.
        """
        scaffold_starts = self._scaffold_df.map(lambda x: x[:2] == [-1, -1]).stack()[lambda x: x].index.tolist()
        scaffold_paths = [follow_path(self._scaffold_df, start) for start in scaffold_starts]
        assert len(scaffold_paths) == 1, 'There should be only one scaffold path'
        staple_starts = self._staple_df.map(lambda x: x[:2] == [-1, -1]).stack()[lambda x: x].index.tolist()
        staple_paths = [follow_path(self._staple_df, start) for start in staple_starts]
        return scaffold_paths[0], staple_paths
    # end def

    def get_nucleotide_map(self):
        """
        Returns a dictionary mapping each location in cadnano grid to its corresponding nucleotide index.
        If a location is in the skip locations, it is mapped to -1.
        """
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

    def get_nucleotide_df(self):
        """
        Returns a DataFrame containing nucleotide value for each location in the cadnano grid.
        For positions that have skips, the value is -1.

        Returns:
            pandas.DataFrame: A DataFrame containing nucleotide information for each location in the scaffold path.
        """
        nucleotide_df = self._skip_df.copy()
        for location in self._scaffold_path:
            nucleotide_df.loc[location] = self._nucleotide_map[location]
        return nucleotide_df
    # end def

    def get_scaffold_crossover_dfs(self):
        """
        Returns two dataframes: `seam_df` and `edge_df` representing scaffold crossovers.

        `seam_df` is a dataframe where the values are False for the columns corresponding to the edge crossovers,
        and True for all other columns.

        `edge_df` is a dataframe where the values are True for the columns corresponding to the edge crossovers,
        and False for all other columns.

        Returns:
            seam_df (pandas.DataFrame): A dataframe representing scaffold crossovers with False values for edge crossovers.
            edge_df (pandas.DataFrame): A dataframe representing scaffold crossovers with True values for edge crossovers.
        """
        # Find all scaffold crossovers
        scaffold_cross_df = self._scaffold_df.map(lambda x: x[0] != x[2] and -1 not in x)
        # Find the edge columns and set to False in seam_df
        cols = scaffold_cross_df.columns.tolist()
        edge_cols = (min(cols), max(cols))
        seam_df = scaffold_cross_df.copy()
        seam_df.loc[:, edge_cols[0]] = False
        seam_df.loc[:, edge_cols[1]] = False
        # Do a bitwise compare to get the edge_df
        edge_df = scaffold_cross_df ^ seam_df        
        return seam_df, edge_df
    # end def

    def get_staple_crossover_df(self):
        """
        Returns a DataFrame indicating whether there is a staple crossover at the cadnano grid.

        The returned DataFrame has the same shape as the staple DataFrame, with True values indicating
        that some staple strand has a crossover, and False values indicating no crossover.
        """
        staple_cross_df = self._staple_df.map(lambda x: x[0] != x[2] and -1 not in x)
        return staple_cross_df
    # end def

    def get_vertex_df(self):
        """
        Returns a DataFrame indicating whether there is a vertex at each location in the cadnano grid.

        Returns:
            pandas.DataFrame: A DataFrame indicating whether there is a vertex at each location.
        """
        # find locations where the staples start or end
        terminal_locations = self._staple_df.map(lambda x: -1 in x)
        # combine with all crossover locations
        vertex_df = self.staple_crossover_df | self.seam_df | self.edge_df | terminal_locations
        return vertex_df

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

    @property
    def scaffold_path(self):
        return self._scaffold_path
    # end def

    @property
    def staple_paths(self):
        return self._staple_paths
    # end def

    @property
    def staple_colors(self):
        return self._staple_colors
    # end def

    @property
    def nucleotide_map(self):
        return self._nucleotide_map
    # end def

    @property
    def nucleotide_df(self):
        return self._nucleotide_df
    # end def

    @property
    def seam_df(self):
        return self._seam_df
    # end def

    @property
    def edge_df(self):
        return self._edge_df
    # end def

    @property
    def staple_crossover_df(self):
        return self._staple_crossover_df
    # end def

    @property
    def vertex_df(self):
        return self._vertex_df

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
    file_path = '/Users/behnamnajafi/Code/DLM/DLM2/Run/Input/JSONs/RcS.json'
    cadnano = Cadnano.from_json(file_path)
    
