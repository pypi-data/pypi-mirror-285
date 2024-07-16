import pandas as pd
from SpringSaLaDpy.data_locator import data_file_finder
from SpringSaLaDpy.input_file_extraction import read_input_file
from .Molclustpy_visualization_funcitons import *
from SpringSaLaDpy.time_rounder import find_nearest_time
import os

def plot(search_directory, time=None, specialClusters=[], width=0.15, alpha=0.5):
    path_list = ['data', 'Cluster_stat', 'Histograms', 'Size_Comp_Freq', 'MEAN_Run']
    
    #Round to nearest available time based on dt_data value
    _, split_file = read_input_file(search_directory)
    dt_data = float(split_file[0][4][9:])

    search_term = 'Size_Comp_Freq'

    time, comp_file = find_nearest_time(search_directory, path_list, time, dt_data, search_term)

    df = pd.read_csv(comp_file)
    df = df.rename({'Size':'Clusters'}, axis = 1)

    molecules = df.columns[1].split(',')

    df_expanded = df[df.columns[1]].str.split(',', expand=True)
    df_expanded.columns = molecules

    df = pd.concat([df, df_expanded], axis=1)

    for molecule in molecules:
        df[molecule] = df[molecule].astype(float) * df['Frequency in clusters of the same size']

    df = df.groupby('Clusters')[molecules].sum().reset_index()

    df['row_sum'] = df[molecules].sum(axis=1)

    for molecule in molecules:
        df[molecule] = df[molecule] / df['row_sum']

    df = df.drop(['row_sum'], axis=1)

    outpath = os.path.normpath(comp_file)
    outpath = os.path.join(*outpath.split(os.sep)[:-5])

    if not os.path.isdir(outpath + os.sep + 'pyStat'):
        os.makedirs(outpath + os.sep + 'pyStat')

    csv_path = os.path.join(outpath, 'pyStat', 'Cluster_composition.csv')
    df.to_csv(csv_path)

    plotClusterCompositionCopy(outpath, time, specialClusters, width, alpha)