from .ssalad_ClusterAnalysis import *
from .Molclustpy_visualization_funcitons import *
from .Composition_calculator import composition_calc
from .Format import format

def plot(search_directory, times, special_clusters=[], width=0.1, alpha=0.6, legend_right=True):
    
    input_file, rounded_times, title_str = format(search_directory, times, 'cluster')

    ca = ClusterAnalysis(input_file)
    ca.getMeanTrajectory(SingleTraj=False)
    ca.getSteadyStateDistribution(SS_timePoints=rounded_times)

    composition_calc(search_directory, title_str, special_clusters, width=width, alpha=alpha, legend_right=legend_right)