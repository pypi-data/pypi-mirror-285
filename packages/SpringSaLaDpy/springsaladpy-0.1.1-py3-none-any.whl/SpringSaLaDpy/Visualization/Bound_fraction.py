import numpy as np
from .ClusterCrossLinking import CrossLinkIndex
from .times_2_title import *
from SpringSaLaDpy.data_locator import *
from .Format import format

def plot(search_directory, times, size_threshold_mean=1, grouping='all', hist=False):     
    input_file, rounded_times, title_str = format(search_directory, times, 'viewer')

    vf = data_file_finder(search_directory, ['viewer_files'], run=0)

    CLI = CrossLinkIndex(input_file, ss_timeSeries=rounded_times)

    print(CLI)
    #d = cl.mapSiteToMolecule()
    #rif = ReadInputFile(txtfile)
    #print(rif.getReactiveSites())
    #print(len(cl.getActiveSiteIDs())) 
    CLI.getSI(vf) 
    CLI.getSI_stat() 
    CLI.plot_SI_stat(color='gray', fs=16, xticks=None, yticks=None, hist=hist, title_str=title_str, size_threshold_mean=size_threshold_mean, grouping=grouping)
    #CLI.plot_SI_stat(color='c', xticks=None, yticks=None)