import ast
import pandas as pd
import numpy as np
from .Molclustpy_visualization_funcitons import *
from SpringSaLaDpy.data_locator import *

def composition_calc(search_directory, title_str, special_clusters, width=0.1, alpha=0.6, legend_right=True):

    path = data_file_finder(search_directory, ['pyStat', 'Cluster_stat'], search_term='Clusters_composition')

    with open(path) as file:
        lines = file.readlines()
    file.close()

    molecules_list = ast.literal_eval(lines[0].split('\t')[1][1:-13])
    columns = ['Clusters']
    columns.extend(molecules_list)

    output_lists = []
    for line in lines:
        if line != '\n' and line[:12] != 'Cluster Size':
            
            size_list = line.split('\t')
            size_list.pop()
            size_list.pop(0)
            size_list.pop(0)

            for i, item in enumerate(size_list):
                size_list[i] = size_list[i].split(' : ')
                tmp = size_list[i][0].split(',')
                size_list[i][0] = np.array([float(entry) for entry in tmp])*float(size_list[i][1][:-1])/100
                size_list[i] = size_list[i][0]
            
            summed_list = sum(size_list)
            size = round(sum(summed_list))
            relative_list = summed_list/sum(summed_list)

            output_list = [size]
            output_list.extend(relative_list)
            output_lists.append(output_list)
    df = pd.DataFrame(output_lists, columns=columns)

    outpath = os.path.join(os.path.split(path)[0], 'Cluster_composition.csv')
    
    df.to_csv(outpath)

    plotClusterCompositionCopy(outpath, title_str, specialClusters=special_clusters, width=width, alpha=alpha, legend_right=legend_right)