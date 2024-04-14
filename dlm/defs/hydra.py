import copy
from dlm.defs.general import Limits

# Root directories for saved simulation data
DataRootDirSabrent = '/Volumes/Sabrent/Hydra'
DataRootDirSamsung = '/Volumes/Sam980/Hydra'
DataRootDirExtraSpace = '/Volumes/ExtraSpace/Hydra'
DataRootDirSandisk = '/Volumes/SanDisk2TB/Hydra'

# directory structure for different code_versions
# the most recent is the default
default_dir_structure = ['Scaffold','k_plus','Topology','RateMethod','RateModel','Conc',
                         'PRot','SRot','Gamma','n_param','Missing','Init','SimType',
                         'TempRate','dT','US','Window','Weight','Cluster','Seed']
# this applies to July19, Aug19, Sep19, Oct19
july19_dir_structure = [item for item in default_dir_structure if item != 'RateMethod']
# this applies to june19 and earlier
june19_dir_structure = [item for item in july19_dir_structure if item != 'k_plus']

dir_structures = [default_dir_structure, july19_dir_structure, june19_dir_structure]

def parse_hydra_path(path):
    split_path = path.split('/')
    root_directory = '/'.join(split_path[0:5])
    actual_dir_structure = None
    for dir_structure in dir_structures:
        if len(split_path[5:]) == len(dir_structure):
            actual_dir_structure = dir_structure
            return root_directory, actual_dir_structure
    if actual_dir_structure is None:
        raise ValueError('Could not parse path: ' + path)
    



SetX = {
        'RootDir' : '',
        'DirStructure' : default_dir_structure,
        'RateMethod': ['X'],
        'Scaffold' : ['average'],
        'k_plus' : ['1000'],
        'Topology' : ['X'],
        'RateModel' : ["local"],
        'Conc' : ['C100'],
        'PRot' : ["R0"],
        'SRot' : ["S0"],
        'Gamma' : ["2.5"],
        'n_param' : ["2"],
        'Missing' : ["M0"],
        'Ramp' : ['X'],
        'Temp' : ['X'],
        'US' : ['false'],
        'Window' : ['W0'],
        'Weight' : ['w0'],
        'Cluster' : ["false"],
        'Seed' : [str(i) for i in range(1,201)]}

CompsApr23 = ['RateModel', 'Scaffold', 'TempRate']
SetApr23 = copy.deepcopy(SetX)
SetApr23['RateMethod'] = ['custom']
SetApr23['Topology'] = ['RcUa']
SetApr23['k_plus'] = ['500']
SetApr23['Missing'] = ['M0']
SetApr23['RateModel'] = ['local', 'global']
SetApr23['Scaffold'] = ['seqave']
SetApr23['Ramp'] = [('empty', 'isothermal')]
SetApr23['Temp'] = [(str(T), 'nan') for T in list(range(20, 60, 5)) + list(range(60, 71, 1))]
SetApr23['Seed'] = [str(i) for i in range(1,1001)]
SetApr23['RootDir'] = DataRootDirSandisk + '/April23'
SetApr23['DirStructure'] = default_dir_structure

CompsMar23AM = ['RateModel', 'Topology', 'SimType', 'Scaffold', 'TempRate', 'Weight']
SetMar23AM = copy.deepcopy(SetX)
SetMar23AM['RateMethod'] = ['custom']
SetMar23AM['RateModel'] = ['local', 'global']
SetMar23AM['Scaffold'] = ['PUC', 'seqave']
SetMar23AM['k_plus'] = ['500']
SetMar23AM['Topology'] = ['RcUa','RcUaH', 'RcUaN', 'RcS', 'RcT']
SetMar23AM['Conc'] = ['C100']
SetMar23AM['Gamma'] = ['2.5']
SetMar23AM['n_param'] = ['2']
SetMar23AM['Ramp'] = [('empty', 'anneal'), ('coated', 'melt')]
SetMar23AM['Temp'] = [('1', '30'), ('10', '3')]
SetMar23AM['Seed'] = [str(i) for i in range(1, 101)]
SetMar23AM['RootDir'] = DataRootDirSandisk + '/Mar23'
SetMar23AM['DirStructure'] = default_dir_structure


CompsMar23US = ['RateModel', 'Scaffold', 'Topology', 'TempRate', 'Window', 'Weight']
SetsMar23US = []
SetMar23US1 = copy.deepcopy(SetX)
top = 'RcUa'
SetMar23US1['RateMethod'] = ['custom']
SetMar23US1['Topology'] = [top]
SetMar23US1['RateModel'] = ['local', 'global']
SetMar23US1['Scaffold'] = ['PUC', 'seqave']
SetMar23US1['Ramp'] = [('random', 'isothermal')]
#SetMar23US1['Temp'] = [('-100', 'nan')]
SetMar23US1['Temp'] = [('-96','nan'),('-97','nan'),('-98','nan'),('-99','nan'),('-100','nan'),('-101','nan'),('-102','nan'),('-103','nan'),('-104','nan')]
SetMar23US1['US'] = ['true']
Windows = []
for wind in Limits[top].keys():
    if wind.split('_')[0] == 'D':
        Windows.append(wind + '-Domains_' + top)
    if wind.split('_')[0] == 'SD':
        Windows.append(wind + '-Seam_Domains_' + top.split('_')[0])
SetMar23US1['Window'] = Windows
#SetMar23US1['Weight'] = ['w0','w1']
SetMar23US1['Weight'] = ['w0']
SetMar23US1['Seed'] = [str(i) for i in range(1, 101)]
#SetMar23US1['Seed'] = [str(i) for i in range(1, 16)]
SetMar23US1['RootDir'] = DataRootDirSandisk + '/Mar23'
SetMar23US1['DirStructure'] = default_dir_structure
SetsMar23US.append(SetMar23US1)

SetMar23US2 = copy.deepcopy(SetMar23US1)
top = 'RcS'
SetMar23US2['Topology'] = [top]
SetMar23US2['Weight'] = ['w0','w1']
SetMar23US2['Temp'] = [('-100', 'nan')]
Windows = []
for wind in Limits[top].keys():
    if wind.split('_')[0] == 'D':
        Windows.append(wind + '-Domains_' + top)
SetMar23US2['Window'] = Windows
SetMar23US2['Seed'] = [str(i) for i in range(1, 16)]
SetsMar23US.append(SetMar23US2)

SetMar23US3 = copy.deepcopy(SetMar23US1)
top = 'RcT'
SetMar23US3['Topology'] = [top]
SetMar23US3['Weight'] = ['w0','w1']
SetMar23US3['RateModel'] = ['local']
SetMar23US3['Temp'] = [('-100', 'nan')]
Windows = []
for wind in Limits[top].keys():
    if wind.split('_')[0] == 'D':
        Windows.append(wind + '-Domains_' + top)
SetMar23US3['Window'] = Windows
SetMar23US3['Seed'] = [str(i) for i in range(1, 16)]
SetsMar23US.append(SetMar23US3)

SetMar23US4 = copy.deepcopy(SetMar23US1)
top = 'RcUaH'
SetMar23US4['Topology'] = [top]
SetMar23US4['Temp'] = [('68.0791', 'nan'),('-100','nan')]
SetMar23US4['Seed'] = [str(i) for i in range(1, 16)]
Windows = []
for wind in Limits[top].keys():
    if wind.split('_')[0] == 'D':
        Windows.append(wind + '-Domains_' + top)
SetMar23US4['Window'] = Windows
SetsMar23US.append(SetMar23US4)

SetMar23US5 = copy.deepcopy(SetMar23US1)
top = 'RcUaN'
SetMar23US5['Topology'] = [top]
SetMar23US5['Temp'] = [('68.0791', 'nan'),('-100','nan')]
SetMar23US5['Seed'] = [str(i) for i in range(1, 16)]
Windows = []
for wind in Limits[top].keys():
    if wind.split('_')[0] == 'D':
        Windows.append(wind + '-Domains_' + top)
SetMar23US5['Window'] = Windows
SetsMar23US.append(SetMar23US5)

#SetsMar23US = []
SetMar23US6 = copy.deepcopy(SetMar23US1)
top = 'RcUa_RcH'
SetMar23US6['Topology'] = [top]
SetMar23US6['Temp'] = [('40', 'nan'), ('45', 'nan'), ('50', 'nan'), ('55', 'nan'), ('60', 'nan')]
Windows = []
for wind in Limits[top].keys():
    if wind.split('_')[0] == 'D':
        Windows.append(wind + '-Domains_' + top.split('_')[0])
SetMar23US6['Window'] = Windows
SetMar23US6['Seed'] = [str(i) for i in range(1, 6)]
#SetsMar23US.append(SetMar23US6)

SetMar23US7 = copy.deepcopy(SetMar23US6)
Windows = []
for wind in Limits[top].keys():
    if wind.split('_')[0] == 'SD':
        Windows.append(wind + '-Seam_Domains_' + top.split('_')[0])
SetMar23US7['Window'] = Windows
#SetsMar23US.append(SetMar23US7)


#######################################################################################################################

CompsDec20 = ['Scaffold', 'TempRate', 'Missing']
SetDec20 = copy.deepcopy(SetX)
SetDec20['RateMethod'] = ['custom']
SetDec20['Topology'] = ['RcUa_RcH']
SetDec20['k_plus'] = ['500']
SetDec20['Scaffold'] = ['average', 'PUC', 'PJB']
SetDec20['Ramp'] = [('coated', 'isothermal')]
SetDec20['Temp'] = [(str(T), 'nan') for T in list(range(20, 40, 5)) + list(range(40, 60 + 1, 1))]
SetDec20['Missing'] = ['M0']
SetDec20['Missing'] += ['M1_Nuc_Edge']
SetDec20['Missing'] += ['M2_Nuc_Seam']
SetDec20['Missing'] += ['M3_Nuc_Edge']
SetDec20['Missing'] += ['M7_Nuc_Edge']
SetDec20['Missing'] += ['M10_Rand', 'M10_Col_Seam', 'M10_Col_NearSeam3P', 'M10_Col_NearSeam5P',
					'M10_Col_Middle3P', 'M10_Col_Middle5P', 'M10_Nuc_Seam']
SetDec20['Missing'] += ['M12_Rand', 'M12_Col_Seam', 'M12_Col_Edge', 'M12_Nuc_Body',
					'M12_Row_Middle', 'M12_Col_Body']
SetDec20['Missing'] += ['M24_Col_SeamEdge']
SetDec20['RootDir'] = DataRootDirSabrent + '/Dec20'
SetDec20['DirStructure'] = default_dir_structure

CompsDec20Rot = ['Scaffold', 'TempRate', 'Missing','PRot']
SetDec20Rot = copy.deepcopy(SetDec20)
SetDec20Rot['Scaffold'] = ['PUC', 'average']
SetDec20Rot['PRot'] = ['R-2','R-4','R4','R2']
SetDec20Rot['Missing'] = ['M0','M10_Col_Seam', 'M10_Col_NearSeam3P', 'M10_Col_NearSeam5P']

CompsDec20RcT = ['Topology','Scaffold', 'TempRate', 'Missing']
SetDec20RcT = copy.deepcopy(SetDec20)
SetDec20RcT['Topology'] = ['RcT_RcH']
SetDec20RcT['Scaffold'] = ['PUC', 'average']
SetDec20RcT['Temp'] = [(str(T),'nan') for T in list(range(20,61,5))] 
SetDec20RcT['Missing'] = ['M0','M7_Nuc_Edge','M10_Col_Seam', 'M10_Col_Middle3P']

CompsDec20ss = ['Topology','Scaffold','TempRate','SimType']
SetDec20ss = copy.deepcopy(SetDec20)
SetDec20ss['Topology'] = ['RcUa', 'RcUa_RcH']
SetDec20ss['k_plus'] = ['500']
SetDec20ss['Scaffold'] = ['PUC', 'average']
SetDec20ss['Ramp'] = [('empty', 'isothermal')]
SetDec20ss['Temp'] = [(str(T), 'nan') for T in list(range(20, 61, 5))]
SetDec20ss['Missing'] = ['M0']

CompsDec20ssHighT = ['Topology','Scaffold','TempRate','SimType']
SetDec20ssHighT = copy.deepcopy(SetDec20)
SetDec20ssHighT['Topology'] = ['RcUa']
SetDec20ssHighT['k_plus'] = ['500']
SetDec20ssHighT['Scaffold'] = ['average']#'PUC',]
SetDec20ssHighT['Ramp'] = [('empty', 'isothermal')]
SetDec20ssHighT['Temp'] = [(str(T), 'nan') for T in list(range(61, 71, 1))]
SetDec20ssHighT['Missing'] = ['M0']


CompsApr22 = ['Scaffold', 'k_plus', 'Topology', 'TempRate', 'Window', 'Weight']
SetApr22 = copy.deepcopy(SetX)
SetApr22['RateMethod'] = ['custom']
SetApr22['Topology'] = ['RcUa4x4']
SetApr22['Ramp'] = [('random', 'isothermal')]
SetApr22['Temp'] = [(str(temp), 'nan') for temp in range(68, 69)]
SetApr22['US'] = ['true']
SetApr22['Window'] = ['D_W' + str(i) + '-Domains_RcUa4x4' for i in range(1, 2)]
SetApr22['Window'] += ['SD_W' + str(i) + '-Seam_Domains_RcUa4x4' for i in range(1, 2)]
SetApr22['Weight'] = ['w0']
SetApr22['Seed'] = [str(i) for i in range(1, 3)]
SetApr22['RootDir'] = DataRootDirExtraSpace + '/Apr22'
SetApr22['DirStructure'] = default_dir_structure

SetApr22N = copy.deepcopy(SetApr22)
SetApr22N['Temp'] = [(str(temp), 'nan') for temp in range(69, 71)]
SetApr22N['Window'] = ['D_W' + str(i) + '-Domains_RcUa2x8' for i in range(1, 2)]
SetApr22N['Window'] += ['C_W' + str(i) + '-Crossover_RcUa2x8' for i in range(1, 2)]
SetApr22N['Seed'] = [str(i) for i in range(1,20)]
SetApr22N['Topology'] = ['RcUa2x8']
SetApr22N['RateModel'] = ['local', 'global']

SetJan23A = copy.deepcopy(SetApr22)
SetJan23A['Temp'] = [(str(66.8), 'nan')]
SetJan23A['Window'] = ['D_W' + str(i) + '-Domains_RcUa2x8' for i in range(1, 2)]
SetJan23A['Seed'] = [str(i) for i in range(1,21)]
SetJan23A['Topology'] = ['RcUa2x8']
SetJan23A['RateModel'] = ['local', 'global']
SetJan23A['Weight'] = ['w0','w1']
SetJan23A['RootDir'] = DataRootDirExtraSpace + '/Jan23'

SetJan23B = copy.deepcopy(SetJan23A)
SetJan23B['Window'] = ['D_W' + str(i) + '-Domains_RcUa4x4' for i in range(1, 2)]
SetJan23B['Topology'] = ['RcUa4x4']

Sets = []
Set1 = {
	'Scaffold' : ['PJB'],
	'k_plus' : ['3500','1000','500','200','100','50'],
	'Topology' : ['RcU','RcH','RcT'],
	'RateModel' : ["local"],
	'Conc' : ['C10','C20','C40','C100','C200','C400','C800'],
	'PRot' : ["R0"],
	'SRot' : ["S0"],
	'Gamma' : ["2.5"],
	'n_param' : ["2"],
	'Missing' : ["M0"],
	'Ramp' : [('empty','anneal'),('coated','melt')],
	'Temp' : [('1','30'),('10','3'),('4','7.5'),('2','15'),('0.5','60'),('0.25','120'),('0.125','240')],
	'US' : ["false"],
	'Window' : ["W0"],
	'Weight' : ["w0"],
	'Cluster' : ["false"],
	'Seed' : [str(i) for i in range(1,6)]}
Set1['RootDir'] = DataRootDirSamsung + '/July19'
Set1['DirStructure'] = july19_dir_structure
Sets.append(Set1)
Set2 = copy.deepcopy(Set1)
Set2['Scaffold'] = ['PJB']
Set2['k_plus'] = ['1000','500','200','100','50']
Set2['Conc'] = ['C20','C40','C100','C200','C400']
Set2['Temp'] = [('1','30'),('4','7.5'),('2','15'),('0.5','60'),('0.25','120'),('0.125','240')]
Set2['Seed'] = [str(i) for i in range(6,36)]
Sets.append(Set2)
Set3 = copy.deepcopy(Set2)
Set3['k_plus'] = ['500']
Set3['Scaffold'] = ['PJB']
Set3['Topology'] = ['RcUH','RcUN','RcUH2','RcUN2']
Set3['Conc'] = ['C100','C200','C400']
Set3['Seed'] = [str(i) for i in range(1,30)]
Sets.append(Set3)
Set4 = copy.deepcopy(Set3)
Set4['Scaffold'] = ['average','PUC']
Set4['Topology'] = ['RcU','RcH','RcT','RcUH','RcUN','RcUH2','RcUN2']
Sets.append(Set4)
Set5 = copy.deepcopy(Set4)
Set5['Scaffold'] = ['average','PUC','PJB']
Set5['Topology'] = ['RcS']#,'RcSH','RcSH2','RcSN','RcSN2']
Set3['Seed'] = [str(i) for i in range(1,20)]
Sets.append(Set5)
SetsJuly19 = Sets


Sets = []
Set1 = {
	'Scaffold' : ['average','PJB','PUC'],
	'Topology' : ["RcUa","RcUaH","RcUaH2","RcUaN","RcUaN2",'RcT','RcH'],
	'RateModel' : ["local"],
	'Conc' : ["C100","C10"],
	'PRot' : ["R0"],
	'SRot' : ["S0"],
	'Gamma' : ["2.5"],
	'n_param' : ["2"],
	'Missing' : ["M0"],
	'Ramp' : [('empty','anneal'),('coated','melt')],
	'Temp' : [('1','30'),('10','3')],
	'US' : ["false"],
	'Window' : ["W0"],
	'Weight' : ["w0"],
	'Cluster' : ["false"],
	'Seed' : [str(i) for i in range(1,60)]}
Set1['RootDir'] = DataRootDirSamsung + '/June19'
Set1['DirStructure'] = june19_dir_structure
Sets.append(Set1)
Set2 = copy.deepcopy(Set1)
Set2['Topology'] = ['RcUa','RcT','RcH']
Set2['Temp'] = [('0.1','300')]
Sets.append(Set2)
Set3 = copy.deepcopy(Set1)
Set3['Topology'] = ["RcS","RcSH","RcSH2","RcSN","RcSN2"]
Set3['Seed'] = [str(i) for i in range(1,10)]
Sets.append(Set3)
Set4 = copy.deepcopy(Set1)
Set4['Scaffold'] = ['PJB']
Set4['Topology'] = ['RcU','RcUH','RcUN']
Set4['Conc'] = ['C10','C20','C40','C80','C100','C200','C400','C600','C800','C1000']
Set4['Temp'] = [('1','30'),('10','3'),('4','7.5'),('2','15'),('0.5','60'),('0.25','120'),('0.125','240')]
Set4['Seed'] = [str(i) for i in range(1,10)]
Sets.append(Set4)
Set5 = copy.deepcopy(Set4)
Set5['Topology'] = ['RcT','RcH']
Set5['Seed'] = [str(i) for i in range(100,110)]
Sets.append(Set5)
Set6 = copy.deepcopy(Set5)
Set6['Seed'] = [str(i) for i in range(100,106)]
Set6['Topology'] = ['RcS']
Sets.append(Set6)
SetsJune19 = Sets

SetSep22 = copy.deepcopy(SetX)
SetSep22['RateMethod'] = ['custom']
SetSep22['Scaffold'] = ['PUCaverage', 'PUC']
SetSep22['k_plus'] = ['1000']
SetSep22['Topology'] = ['RcH2x8', 'RcUa2x8', 'RcUa2x8a', 'RcUa2x8b', 'RcUa4x4', 'RcU4x4', 'RcT4x4', 'RcS8x2b']
SetSep22['Conc'] = ['C10', 'C100']
SetSep22['Gamma'] = ['1.5', '2.5']
SetSep22['n_param'] = ['0', '2', '4']
SetSep22['Ramp'] = [('empty', 'anneal'), ('coated', 'melt')]
SetSep22['Temp'] = [('1', '30'), ('4', '7.5')]
SetSep22['Seed'] = [str(i) for i in range(1, 101)]
SetSep22['RootDir'] = DataRootDirExtraSpace + '/Sep22'
SetSep22['DirStructure'] = default_dir_structure


SetSep22RealOG = copy.deepcopy(SetX)
SetSep22RealOG['RateMethod'] = ['custom']
SetSep22RealOG['Scaffold'] = ['average','PUC']
SetSep22RealOG['k_plus'] = ['500']
SetSep22RealOG['Topology'] = ['RcS','RcUa','RcU','RcT']
SetSep22RealOG['Topology'] += ['RcUH', 'RcUN', 'RcUaH', 'RcUaN']
SetSep22RealOG['Conc'] = ['C100']
SetSep22RealOG['Gamma'] = ['2.5']
SetSep22RealOG['n_param'] = ['2']
SetSep22RealOG['Ramp'] = [('empty', 'anneal'), ('coated', 'melt')]
SetSep22RealOG['Temp'] = [('1', '30')]
SetSep22RealOG['Seed'] = [str(i) for i in range(1, 151)]
SetSep22RealOG['RootDir'] = DataRootDirSamsung + '/Sep22'
SetSep22RealOG['DirStructure'] = default_dir_structure
SetSep22RealFast = copy.deepcopy(SetX)
SetSep22RealFast['RateMethod'] = ['custom']
SetSep22RealFast['Scaffold'] = ['average']
SetSep22RealFast['k_plus'] = ['500']
SetSep22RealFast['Topology'] = ['RcS','RcUa','RcU','RcT']
SetSep22RealFast['Topology'] += ['RcUH', 'RcUN', 'RcUaH', 'RcUaN']
SetSep22RealFast['Conc'] = ['C100']
SetSep22RealFast['Gamma'] = ['2.5']
SetSep22RealFast['n_param'] = ['2']
SetSep22RealFast['Ramp'] = [('empty', 'anneal'), ('coated', 'melt')]
SetSep22RealFast['Temp'] = [('4', '7.5')]
SetSep22RealFast['Seed'] = [str(i) for i in range(1, 151)]
SetSep22RealFast['RootDir'] = DataRootDirSamsung + '/Sep22'
SetSep22RealFast['DirStructure'] = default_dir_structure
SetSep22RealLow = copy.deepcopy(SetX)
SetSep22RealLow['RateMethod'] = ['custom']
SetSep22RealLow['Scaffold'] = ['average']
SetSep22RealLow['k_plus'] = ['500']
SetSep22RealLow['Topology'] = ['RcS','RcUa','RcU','RcT']
SetSep22RealLow['Topology'] += ['RcUH', 'RcUN', 'RcUaH', 'RcUaN']
SetSep22RealLow['Conc'] = ['C10']
SetSep22RealLow['Gamma'] = ['2.5']
SetSep22RealLow['n_param'] = ['2']
SetSep22RealLow['Ramp'] = [('empty', 'anneal'), ('coated', 'melt')]
SetSep22RealLow['Temp'] = [('1', '30')]
SetSep22RealLow['Seed'] = [str(i) for i in range(1, 151)]
SetSep22RealLow['RootDir'] = DataRootDirSamsung + '/Sep22'
SetSep22RealLow['DirStructure'] = default_dir_structure
SetsSep22Real = [SetSep22RealOG,SetSep22RealFast,SetSep22RealLow]


SetXUS = {
        'Scaffold': ['average', 'PUC'],
        'k_plus': ['500'],
        'Topology': ['X'],
        'RateModel': ["local"],
        'Conc': ['C100'],
        'PRot': ["R0"],
        'SRot': ["S0"],
        'Gamma': ["2.5"],
        'n_param': ["2"],
        'Missing': ["M0"],
        'Ramp': [('random', 'isothermal')],
        'Temp': ['X'],
        'US': ['true'],
        'Window': ['X'],
        'Weight': ['w2'],
        'Cluster': ["false"],
        'Seed': [str(i) for i in range(1, 8)]}
SetXUS['RootDir'] = DataRootDirSamsung + '/Oct19'
SetXUS['DirStructure'] = july19_dir_structure

Set1 = copy.deepcopy(SetXUS)
Set1['Topology'] = ['RcUa']
Set1['Temp'] = [(str(temp), 'nan') for temp in range(60, 71, 1)]
Set1['Window'] = ['D_W' + str(i) + '-Domains_RcUa' for i in range(1, 18)]
Set2 = copy.deepcopy(SetXUS)
Set2['Topology'] = ['RcUa_RcH']
Set2['Temp'] = [(str(temp), 'nan') for temp in range(40, 61, 2)]
Set2['Window'] = ['D_W' + str(i) + '-Domains_RcUa' for i in range(1, 18)]
Set3 = copy.deepcopy(SetXUS)
Set3['Topology'] = ['RcT']
Set3['Temp'] = [(str(temp), 'nan') for temp in range(60, 71, 1)]
Set3['Window'] = ['D_W' + str(i) + '-Domains_RcT' for i in range(1, 18)]
Set4 = copy.deepcopy(SetXUS)
Set4['Topology'] = ['RcS']
Set4['Temp'] = [(str(temp), 'nan') for temp in range(60, 71, 1)]
Set4['Window'] = ['D_W' + str(i) + '-Domains_RcS' for i in range(1, 25)]
Set5 = copy.deepcopy(SetXUS)
Set5['Topology'] = ['RcUa']
Set5['Temp'] = [('68', 'nan')]
Set5['Window'] = ['SD_W' + str(i) + '-Seam_Domains_RcUa' for i in range(1, 3)]
Set6 = copy.deepcopy(Set5)
Set6['Window'] = ['SC_W' + str(i) + '-Seam_Cross_RcUa' for i in range(1, 2)]
Set7 = copy.deepcopy(Set5)
Set7['Window'] = ['C_W' + str(i) + '-Crossover_RcUa' for i in range(1, 9)]
Set8 = copy.deepcopy(Set5)
Set8['Window'] = ['S_W' + str(i) + '-Staples_RcUa' for i in range(1, 10)]
SetsUS = [Set1, Set2, Set3, Set4, Set5, Set6, Set7, Set8]

SetN1 = copy.deepcopy(Set1)
SetN1['Temp'] = [(str(68), 'nan')]
SetN1['Seed'] = [str(i) for i in range(1, 31)]
SetN2 = copy.deepcopy(Set2)
SetN2['Temp'] = [(str(50), 'nan')]
SetN2['Seed'] = [str(i) for i in range(1, 301)]
# SetN2['Seed'] = [str(i) for i in range(1,8)]
SetN3 = copy.deepcopy(Set3)
SetN3['Temp'] = [(str(67), 'nan')]
SetN3['Seed'] = [str(i) for i in range(1, 31)]
SetN4 = copy.deepcopy(Set4)
SetN4['Temp'] = [(str(65), 'nan')]
SetN4['Seed'] = [str(i) for i in range(1, 31)]
SetN5 = copy.deepcopy(Set5)
SetN5['Temp'] = [(str(68), 'nan')]
SetN5['Seed'] = [str(i) for i in range(1, 31)]
SetN6 = copy.deepcopy(Set6)
SetN6['Temp'] = [(str(68), 'nan')]
SetN6['Seed'] = [str(i) for i in range(1, 31)]
SetN7 = copy.deepcopy(Set7)
SetN7['Temp'] = [(str(68), 'nan')]
SetN7['Seed'] = [str(i) for i in range(1, 31)]
SetN8 = copy.deepcopy(Set8)
SetN8['Temp'] = [(str(68), 'nan')]
SetN8['Seed'] = [str(i) for i in range(1, 31)]
SetsUSN = [SetN1, SetN2, SetN3, SetN4, SetN5, SetN6, SetN7, SetN8]

SetS1 = copy.deepcopy(SetXUS)
SetS1['Topology'] = ['RcUaH']
SetS1['Temp'] = [(str(68), 'nan')]
SetS1['Window'] = ['D_W' + str(i) + '-Domains_RcUaH' for i in range(1, 18)]
SetS1['Weight'] = ['w2']
SetS1['Seed'] = [str(i) for i in range(1, 31)]
SetS2 = copy.deepcopy(SetXUS)
SetS2['Topology'] = ['RcUaN']
SetS2['Temp'] = [(str(68), 'nan')]
SetS2['Window'] = ['D_W' + str(i) + '-Domains_RcUaN' for i in range(1, 18)]
SetS2['Weight'] = ['w2']
SetS2['Seed'] = [str(i) for i in range(1, 31)]
SetS3 = copy.deepcopy(SetXUS)
SetS3['Topology'] = ['RcUaH_RcH']
SetS3['Temp'] = [(str(50), 'nan')]
SetS3['Window'] = ['D_W' + str(i) + '-Domains_RcUaH' for i in range(1, 18)]
SetS3['Weight'] = ['w2']
SetS3['Seed'] = [str(i) for i in range(1, 101)]
SetS4 = copy.deepcopy(SetXUS)
SetS4['Topology'] = ['RcUaN_RcH']
SetS4['Temp'] = [(str(50), 'nan')]
SetS4['Window'] = ['D_W' + str(i) + '-Domains_RcUaN' for i in range(1, 18)]
SetS4['Weight'] = ['w2']
SetS4['Seed'] = [str(i) for i in range(1, 101)]
SetS5 = copy.deepcopy(SetXUS)
SetS5['Topology'] = ['RcUaH']
SetS5['Temp'] = [(str(68), 'nan')]
SetS5['Window'] = ['SD_W' + str(1) + '-Seam_Domains_RcUaH']
SetS5['Weight'] = ['w2']
SetS5['Seed'] = [str(i) for i in range(1, 301)]
SetS6 = copy.deepcopy(SetS5)
SetS6['Window'] = ['SC_W' + str(1) + '-Seam_Cross_RcUaH']
SetsUSS = [SetS1, SetS2, SetS3, SetS4, SetS5, SetS6]

SetsUSNow = [SetN1, SetN3, SetN4]


############# In these sets, seam stacking is fixed
### The competitive RcUa_RcH set is not downloaded, used the IsoTarget set instead

### Annealing set -
## all downloaded and analysed
CompsDec22 = ['SimType']
Sets = []
SetDec22 = copy.deepcopy(SetX)
SetDec22['RateMethod'] = ['custom']
SetDec22['Scaffold'] = ['average']
SetDec22['k_plus'] = ['500']
SetDec22['Topology'] = ['RcUa','RcT','RcS']
SetDec22['Conc'] = ['C100']
SetDec22['Gamma'] = ['2.5']
SetDec22['n_param'] = ['2']
SetDec22['Ramp'] = [('empty', 'anneal'), ('coated', 'melt')]
SetDec22['Temp'] = [('1', '30'),('4', '7.5'),('10', '3')]
SetDec22['Seed'] = [str(i) for i in range(1, 151)]
SetDec22['RootDir'] = DataRootDirSamsung + '/Dec22'
SetDec22['DirStructure'] = default_dir_structure

### Isothermal set
# All downloaded
# All analysed
CompsDec22ss = ['SimType']
Sets = []
SetDec22ss = copy.deepcopy(SetX)
SetDec22ss['RateMethod'] = ['custom']
SetDec22ss['Scaffold'] = ['average','PUC']
SetDec22ss['k_plus'] = ['500']
SetDec22ss['Topology'] = ['RcUa']
SetDec22ss['Conc'] = ['C100']
SetDec22ss['Gamma'] = ['2.5']
SetDec22ss['n_param'] = ['2']
SetDec22ss['Ramp'] = [('empty','isothermal')]
SetDec22ss['Temp'] = [(str(T),'nan') for T in list(range(20,40,5))+list(range(40,71,1))]
SetDec22ss['Seed'] = [str(i) for i in range(1, 201)]
SetDec22ss['RootDir'] = DataRootDirSamsung + '/Dec22'
SetDec22ss['DirStructure'] = default_dir_structure




############# These Sets stop when all crossovers reached
### Analysis is done on hydra and pickled downloaded

### All is done + downloaded
## PUC 20C, 25C: need to redo pickles if you have time
CompsSetTarget = ['Scaffold', 'TempRate', 'Missing', 'PRot']
SetTarget = copy.deepcopy(SetX)
SetTarget['RateMethod'] = ['custom']
SetTarget['Topology'] = ['RcUa_RcH']
SetTarget['k_plus'] = ['500']
SetTarget['Scaffold'] = ['average', 'PUC']
SetTarget['Ramp'] = [('coated', 'isothermal')]
SetTarget['Temp'] = [(str(T), 'nan') for T in list(range(20, 40, 5)) + list(range(40, 60 + 1, 1))]
SetTarget['Missing'] = ['M0']
SetTarget['Missing'] += ['M1_Nuc_Edge']
SetTarget['Missing'] += ['M10_Col_Seam', 'M10_Col_NearSeam3P', 'M10_Col_NearSeam5P', 'M10_Col_Middle3P', 'M10_Col_Middle5P']
SetTarget['Seed'] = [str(i) for i in range(1000, 1501)]
SetTarget['RootDir'] = DataRootDirSandisk + '/IsoTarget'
SetTarget['DirStructure'] = default_dir_structure

### All is done + downloaded
## PUC 20C, 25C: need to redo pickles if you have time
CompsSetTargetRot = ['Scaffold', 'TempRate', 'Missing', 'PRot']
SetTargetRot = copy.deepcopy(SetX)
SetTargetRot['RateMethod'] = ['custom']
SetTargetRot['Topology'] = ['RcUa_RcH']
SetTargetRot['k_plus'] = ['500']
SetTargetRot['Scaffold'] = ['average', 'PUC']
SetTargetRot['Ramp'] = [('coated', 'isothermal')]
SetTargetRot['Temp'] = [(str(T), 'nan') for T in list(range(20, 40, 5)) + list(range(40, 60 + 1, 1))]
SetTargetRot['PRot'] = ['R-2', 'R2']
SetTargetRot['Missing'] = ['M0']
SetTargetRot['Missing'] += ['M10_Col_Seam', 'M10_Col_NearSeam3P', 'M10_Col_NearSeam5P']
SetTargetRot['Seed'] = [str(i) for i in range(1000, 1501)]
SetTargetRot['RootDir'] = DataRootDirSandisk + '/IsoTarget'
SetTargetRot['DirStructure'] = default_dir_structure
