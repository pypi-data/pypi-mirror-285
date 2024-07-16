import pandas as pd
import matplotlib.pyplot as plt
from SpringSaLaDpy.data_locator import data_file_finder
from SpringSaLaDpy.input_file_extraction import read_input_file
from .Molclustpy_visualization_funcitons import plotAverageZTimeCourse
import statistics
import numpy as np
import os
import csv

def average_Z(df, desired_IDs):
    color_df = df[df['ID'].isin(desired_IDs)]
    return color_df['Z'].astype(float).mean()
'''
def site_info(colors_and_sites):
    print('Sites:')
    i_max = 0
    for i, color_and_site in enumerate(colors_and_sites):
        i_max = i
        append_str = ''
        for site in color_and_site[1]:
            append_str = f'{append_str}{site[1]} of {site[0]}, '
        output = f'{i}: {append_str}'
        print(output[:-2])

    lines = []
    for i in range(0, i_max + 1):
        lines.append(i)

    print('\nList of indices:')
    print(lines)
'''

def site_info(name_list):
    print('Sites:')
    for i, name in enumerate(name_list):
        print(f'{i}: {name[1]} of {name[0]}')
    lines = []
    for i in range(0, len(name_list)):
        lines.append(i)

    print('\nList of indices:')
    print(lines)

def molecule_info(name_list):
    print('Molecules:')
    for i, name in enumerate(name_list):
        print(f'{i}: {name}')
    lines = []
    for i in range(0, len(name_list)):
        lines.append(i)

    print('\nList of indices:')
    print(lines)

def color_info(name_list):
    
    print('Sites with the same color:')
    for i, name in enumerate(name_list):
        print(f'{i}: {name}')
    lines = []
    for i in range(0, len(name_list)):
        lines.append(i)

    print('\nList of indices:')
    print(lines)

def plot(directory_path, mode='mol', indices=[], list_options=True, verbose=False, legend_right=True, fill=True):
    molecules, _ = read_input_file(directory_path)

    new_path = data_file_finder(directory_path, ['viewer_files'], search_term='VIEW_Run0')
    new_directory = os.path.split(new_path)[0]
    num_runs = len(os.listdir(new_directory))

    z_values_list = []
    count = 0
    
    colors_and_sites = []
    used_sites = []

    for molecule in molecules:
        for line in molecule:
            if line[0:4] == 'TYPE':
                color = line.split()[8]
                type = line.split()[2][1:-1]
                molecule_name = molecule[0].split()[1][1:-1]
                if color not in (item[0] for item in colors_and_sites):
                    colors_and_sites.append([color, [[molecule_name, type]]])
                    used_sites.append([molecule_name, type])
                elif [molecule_name, type] not in used_sites:
                    for i, item in enumerate(colors_and_sites):
                        if item[0] == color:
                            colors_and_sites[i][1].append([molecule_name, type])
                    used_sites.append([molecule_name, type])
                else:
                    pass
    
    for run_num in range(num_runs):
        path = data_file_finder(directory_path, ['viewer_files'], run = run_num)
        sites_path = data_file_finder(directory_path, ['data', f'Run{run_num}'], search_term='SiteIDs.csv')

        data_dict = {}

        with open(sites_path, mode='r') as file:
            csv_reader = csv.reader(file)

            for row in csv_reader:
                key = row[0]
                value = row[1].split()
                value = [value[0], value[4]]
                data_dict[key] = value
        file.close()

        with open(path, "r") as file:
            lines = file.readlines()
        file.close()

        molecule_names = []
        site_names = []

        for key in data_dict:
            if data_dict[key][0] not in molecule_names:
                molecule_names.append(data_dict[key][0])

        for key in data_dict:
            if data_dict[key] not in site_names:
                site_names.append(data_dict[key])

        if indices == []:
            if mode=='mol':
                for i in range(len(molecule_names)):
                    indices.append(i)
            elif mode=='site':
                for i in range(len(site_names)):
                    indices.append(i)
            else:
                for i in range(len(colors_and_sites)):
                    indices.append(i)

        if list_options and count == 0:
            if mode == 'mol':
                molecule_info(molecule_names)
            elif mode == 'site':
                site_info(site_names)
            else:
                pass

        count = count + 1
        
        split_file = []
        times = []
        current_list = []

        for line in lines:
            if line == 'SCENE\n':
                split_file.append(current_list)
                current_list = []
            if line[0:2] == 'ID':
                current_list.append(line.strip()[3:])
            if line[0:11] == 'SceneNumber':
                times.append(line.split('\t')[3][:-1])
        split_file.append(current_list)
        _ = split_file.pop(0)

        for i, scene in enumerate(split_file):
            for j, row in enumerate(scene):
                split_file[i][j] = row.split('\t')

        data_frame_list = []

        column_list = ['ID', 'Radius', 'Color', 'X', 'Y', 'Z']

        for scene in split_file:
            data_frame_list.append(pd.DataFrame(scene, columns=column_list))
        
        color_list_full = [x[0] for x in colors_and_sites]
        color_list = []
        if mode=='color':
            if indices == []:
                color_list = color_list_full
            else: 
                for index in indices:
                    color_list.append(colors_and_sites[index][0])
        
        z_values = []
        desired_IDs = []
        legend_list = ['Time']
        if mode == 'mol':    
            for index in indices:
                current_len = len(desired_IDs)
                desired_IDs.append([key for key, value in data_dict.items() if value[0] == molecule_names[index]])
                if len(desired_IDs) != current_len:
                    legend_list.append(molecule_names[index])
        elif mode == 'site':
            for index in indices:
                current_len = len(desired_IDs)
                desired_IDs.append([key for key, value in data_dict.items() if value[0] == site_names[index][0] and value[1] == site_names[index][1]])
                if len(desired_IDs) != current_len:
                    if verbose:
                        legend_list.append(f'Site {site_names[index][1]} of {site_names[index][0]}')
                    else:
                        legend_list.append(site_names[index][1])
        else:
            desired_sites = []
            for color in colors_and_sites:
                tmp=[]
                for site in color[1]:
                    for key, value in data_dict.items():
                        if value == site and site not in tmp:
                            tmp.append(site)
                desired_sites.append(tmp)
            for color in desired_sites:
                tmp=[]
                for site in color:
                    tmp.extend([key for key, value in data_dict.items() if value == site])
                desired_IDs.append(tmp)
            for color in color_list:
                for color_and_site in colors_and_sites:
                    if color == color_and_site[0]:
                        legend_entry = ''
                        item_list = []
                        for site in color_and_site[1]:
                            item_list.append(site)
                        #item_list.sort()
                        for site in item_list:
                            if verbose:
                                legend_entry = legend_entry + f'Site {site[1]} of {site[0]}, '
                            else:
                                legend_entry = legend_entry + f'{site[1]}, ' 
                        legend_list.append(legend_entry[:-2])

        for i in range(len(indices)):
            line = []
            for data_frame in data_frame_list:
                line.append(average_Z(data_frame,desired_IDs[i]))
            z_values.append(line)
        z_values_list.append(z_values)

    if mode == 'color':
        display_colors = []
        for color in color_list_full:
            for color_and_site in colors_and_sites:
                if color == color_and_site[0]:
                    legend_entry = ''
                    item_list = []
                    for site in color_and_site[1]:
                        item_list.append(site)
                    #item_list.sort()
                    for site in item_list:
                        if verbose:
                            legend_entry = legend_entry + f'Site {site[1]} of {site[0]}, '
                        else:
                            legend_entry = legend_entry + f'{site[1]}, ' 
                    display_colors.append(legend_entry[:-2])
        if list_options:
            color_info(display_colors)

    avg_z_values = [[float(time) for time in times]]
    std_z_values = [[float(time) for time in times]]
            
    for i in range(len(indices)):
        tmp_list = []
        for run in z_values_list:
            tmp_list.append(run[i])
        avg = [sum(col)/len(col) for col in zip(*tmp_list)]
        avg_z_values.append(avg)
        if num_runs != 1:
            std = [statistics.stdev(col) for col in zip(*tmp_list)]
            std_z_values.append(std)
        else:
            fill = False
            std = [0 for col in zip(*tmp_list)]
            std_z_values.append(std)
        
    avg_arr = np.transpose(np.array(avg_z_values))
    std_arr = np.transpose(np.array(std_z_values))

    plotAverageZTimeCourse(avg_arr, std_arr, legend_list, legend_right=legend_right, fill=fill, colors=color_list)

    #plt.figure(figsize=(8,5))

    
    