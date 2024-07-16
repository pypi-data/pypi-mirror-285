from SpringSaLaDpy.input_file_extraction import *
import os
import matplotlib.pyplot as plt
from .ClusTopology_ss import ClusterDensity
from .DataPy import *
from .times_2_title import * 
from .Format import format

def read_viewer(path):
    if path[-7:] == '_FOLDER':
        last_item = ''
    else:
        last_item = os.path.split(path)[1][:-12] + '_FOLDER'
    specific_path  = os.path.join(path, last_item)

    _,split_file = read_input_file(specific_path)
    total_time = float(split_file[0][1].split(' ')[2])
    dt_image = float(split_file[0][5].split(' ')[1])
    count = int(total_time/dt_image)

    input_file = find_txt_file(specific_path)
    return count, dt_image, input_file

def plot(search_directory, times=[], size_threshold=1, bonds_hist=False):
    
    input_file, rounded_times, title_str = format(search_directory, times, file_type='viewer')

    cd = ClusterDensity(input_file, ss_timeSeries=rounded_times)
    cd.getCD_stat(cs_thresh=size_threshold, title_str=title_str, bonds_hist=bonds_hist)

def time_course(path, indices = [], size_threshold=1, legend_right=True):
    count, dt_image, input_file = read_viewer(path)

    times = [0]
    for i in range(int(count) + 1):
        times.append(i*dt_image)
    times.pop(0)

    cd = ClusterDensity(input_file, ss_timeSeries=[times[0]])
    vfiles = glob(cd.simObj.getInpath() + "/viewer_files/*.txt")[:]
    
    outputs = []
    for i in range(3):
        outputs.append([[],[],[]])

    for time in times:
        cs_tmp, rg_tmp, rmax_tmp = [], [], []
        
        cd = ClusterDensity(input_file, ss_timeSeries=[time])
        for vfile in vfiles:
            #this line takes up the majority of the computation time
            res, MCL, mtp_cs, mtp_rg, mtp_rmax = cd.getClusterDensity(vfile, size_threshold)

            cs_tmp.extend(mtp_cs)
            rg_tmp.extend(mtp_rg)
            rmax_tmp.extend(mtp_rmax)

        csList = np.concatenate(cs_tmp).ravel().tolist()
        rgList = np.concatenate(rg_tmp).ravel().tolist()
        rmaxList = np.concatenate(rmax_tmp).ravel().tolist()
        
        plotting_lists = [rgList, csList, rmaxList]

        for i, plotting_list in enumerate(plotting_lists):
            if csList == []:
                for j in range(3):
                    outputs[i][j].append(0)
            else:
                outputs[i][0].append(min(plotting_list))
                outputs[i][1].append(sum(plotting_list)/len(plotting_list))
                outputs[i][2].append(max(plotting_list))

    plot_dict = {
        0: 'Minimum',
        1: 'Average',
        2: 'Maximum'
    }

    label_dict = {
        0: ['Radius of Gyration', 'Radius of Gyration (nm)'],
        1: ['Cluster Size', 'Molecules per Cluster'],
        2: ['Maximum Cluster Radius', 'Distance (nm)']
    }

    if indices == []:
        indices = [0,1,2]

    legend_list = []
    for i, output in enumerate(outputs):
        plt.figure()
        for index in indices:
            legend_list.append(plot_dict[index])
            plt.plot(times,output[index])
            plt.title(label_dict[i][0])
            plt.ylabel(label_dict[i][1])
        plt.xlabel('Time (seconds)')
        
        if not legend_right:
            plt.legend(legend_list)      
        else:
            plt.legend(legend_list, bbox_to_anchor=(1.02, 1), loc='upper left')
        
    

    
    