import pandas as pd
import numpy as np
import os
from SpringSaLaDpy.data_locator import *
from molclustpy import *
from .Molclustpy_visualization_funcitons import *

def format_file_name(file_name):
    split_name = file_name.split('_')
    if 'Site_' not in file_name:
        return split_name[0]
    else:
        return f'{split_name[0]} {split_name[1]} {split_name[2]} {split_name[3]}'

def plot(path, data_selection=[]):
    
    if type(data_selection) != list:
        print("Error: Your data_selection must be a list")
        return
    
    df = pd.read_csv(path, skiprows=1)
    
    output_columns = []
    molecule_list = []
    states = ['free', 'bound', 'total']
    num_entries = (df.shape[1] - 3)/2
    
    #Get list of molecule names from columns
    '''for item in df.columns:
        if item != ' ':
            split_item = item.split().pop()
            if '.1' not in split_item and split_item not in molecule_list and split_item != 'Time':
                molecule_list.append(split_item)'''
    
    #Determine the columns the user wants displayed based on the data_selection argument
    '''for item in data_selection:
        if type(item) == str:
            if item.upper() in (state.upper() for state in states):
                for column in df.columns:
                    if item.upper() in column and not '.1' in column:
                        if column not in output_columns:
                            output_columns.append(column)
            elif item in molecule_list:
                length = len(item)
                for column in df.columns:
                    if column[-length:] == item:
                        if column not in output_columns:
                            output_columns.append(column)
            else:
                print(f'Warning: "{item}" doesn\'t correspond to a recognized molecule name or state in the dataset provided')
        elif type(item) == int:
            if item < 1 or item > num_entries:
                print(f'Warrning: Entry {item} is out of range')
                continue
            if df.columns[item] not in output_columns:
                output_columns.append(df.columns[item])
        else:
            print('Error: Only str and int datatypes are allowed in the data_selection list')
            return'''
    
    output_columns = list(df.columns[1:int(num_entries + 1)])

    outpath = os.path.split(path)[0] + "/pyStat"

    if not os.path.isdir(outpath):
        os.makedirs(outpath)
    
    average_list = ['Time']
    average_list.extend(output_columns)
    stdev_list = [x + '.1' for x in output_columns]
    stdev_list.insert(0,'Time')
    Averages = df[average_list].to_numpy()
    Stdevs = df[stdev_list].to_numpy()
    average_list = [x.replace(' ','_')[1:] if x != 'Time' else x for x in average_list]
    obs_names = '\t'.join(average_list)

    np.savetxt(outpath + "/Mean_Observable_Counts.txt", Averages, header=obs_names, fmt='%.6e')
    np.savetxt(outpath + "/Stdev_Observable_Counts.txt", Stdevs, header=obs_names, fmt='%.6e')
    outpath = os.path.split(outpath)[0]

    file_name = os.path.split(path)[1][23:]
    file_name = format_file_name(file_name)
    plotTimeCourseCopy(outpath, file_name, data_selection)
    

    #Old plotting code
    '''#Plot selected columns with corresponding 1 standard deviations bounds
    if output_columns == []:
        print('Error: No data selected')
        return
    else:
        df.plot('Time', output_columns)
        for output in output_columns:
            plt.fill_between(df['Time'], 
                             df[output] - df[output + '.1'], 
                             df[output] + df[output + '.1'], 
                             alpha=0.2)

        plt.xlabel('Time (Seconds)')
        plt.ylabel('Average Molecule Counts')
        plt.show()'''