from .MoleculeCounter import *
from .Molclustpy_visualization_funcitons import *
from SpringSaLaDpy.display_info import *
from SpringSaLaDpy.data_locator import *

def plot(search_directory, data_selection='FullCount', indices=[], list_options=True, legend_right=True, fill=True):
    data_file_path = data_file_finder(search_directory, search_term=data_selection, path_list=['data', 'Run0'])
    data_file = os.path.split(data_file_path)[1]
    
    # Compute the free molecular concentrations
    mc = MoleculeCounter(search_directory, dataFile=data_file)
    mc.getMoleculeStat()

    title = os.path.split(data_file)[1][:-4]
    if list_options:
        column_info(data_file_path, start_col=1)

    plotTimeCourseCopy(search_directory, title, indices, legend_right, fill)