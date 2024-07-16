import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
from numpy import array

def plotClusterDistCopy(path, times, sizeRange=[], title_str=''):
    # plotting the cluster size distribution (ACO: average cluster occupancy)
    fix, ax = plt.subplots(figsize=(7,4))
    df = pd.read_csv(path + '/pyStat/Cluster_stat/SteadyState_distribution.csv')
    cs, foTM = df['Cluster size'], df['foTM']

    if len(sizeRange) == 0:
        aco = sum(cs*foTM)
        plt.bar(cs, height=foTM, fc='grey',ec='k', label=f'ACO = {aco:.2f}')
        plt.axvline(aco, ls='dashed', lw=1.5, color='k')
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True, min_n_ticks=1))
        plt.xlabel('Cluster Size (molecules)')
        plt.ylabel('Fraction of total molecules')
        plt.title(f'Cluster Size Distribution{title_str}')
        plt.legend()
        plt.show()
    else:
        # sizeRange = [1,10,20]
        # clusters : 1-10, 10-20, >20
        idList = [0]
        #xbar = np.arange(1, len(sizeRange)+1, 1)
        xLab = [f'{sizeRange[i]} - {sizeRange[i+1]}' for i in range(len(sizeRange) - 1)]
        xLab.append(f'> {sizeRange[-1]}')
        
        for size in sizeRange[1:]:
            i = 0
            while cs[i] < size:
                i += 1
            if cs[i] == size:
                idList.append(i+1)
            else:
                idList.append(i)
            
        
        foTM_binned = [sum(foTM[idList[i]: idList[i+1]]) for i in range(len(idList)-1)]
        foTM_binned.append(sum(foTM[idList[-1]:]))
        
        try:
            plt.bar(xLab, foTM_binned, color='grey', ec='k')
            ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True, min_n_ticks=1))
            plt.xlabel('Cluster size range (molecules)')
            plt.ylabel('Fraction of total molecules')
            plt.title(f'Binned Cluster Size Distribution{title_str}')
            plt.ylim(0,1)
            plt.show()
        except:
            print('Invalid size range!! Maximal size range might be higher than largest cluster!')

def getColumns(txtfile):
    # name of observables in gdat file
    with open(txtfile,'r') as tf:
        lines = tf.readlines()
    lines[0] = lines[0][8:-1]
    columns = ['Time']
    columns.extend(lines[0].split('\t'))
    return columns

def plotTimeCourseCopy(path, file_name, obsList=[], legend_right=True, fill=True):
    # plotting the observable time course
    txtfile = path + '/pyStat/Count_stat/Mean_Observable_Counts.txt'
    mean_data = np.loadtxt(path + '/pyStat/Count_stat/Mean_Observable_Counts.txt')
    std_data = np.loadtxt(path + '/pyStat/Count_stat/Stdev_Observable_Counts.txt')
    
    _, numVar = mean_data.shape
    colNames = getColumns(txtfile)
    if len(obsList) == 0:
        for i in range(1, numVar):
            x, y, yerr = mean_data[:,0], mean_data[:,int(i)], std_data[:,int(i)]
            plt.plot(x,y, label=f'{colNames[i]}')
            if fill:
                plt.fill_between(x, y-yerr, y+yerr, alpha=0.2)
    else:
        for i in obsList:
            x, y, yerr = mean_data[:,0], mean_data[:,int(i+1)], std_data[:,int(i+1)]
            plt.plot(x,y, label=f'{colNames[i+1]}')
            if fill:
                plt.fill_between(x, y-yerr, y+yerr, alpha=0.2)

    fill_str = ''
    if fill:
        fill_str = ' (bounds of 1 SD)'

    if not legend_right:
        plt.legend()      
    else:
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Observable Counts')
    plt.title(f'{file_name}{fill_str}')
    plt.show()

def plotAverageZTimeCourse(mean_data, std_data, colNames, legend_right=True, fill=False, colors=[]):    
    _, numVar = mean_data.shape
    for i in range(1, numVar):
        x, y, yerr = mean_data[:,0], mean_data[:,int(i)], std_data[:,int(i)]
        if colors != []:
            plt.plot(x,y, label=f'{colNames[i]}', color=colors[i-1])
            if fill:
                plt.fill_between(x, y-yerr, y+yerr, alpha=0.2, color=colors[i-1])
            else:
                pass
        else:
            plt.plot(x,y, label=f'{colNames[i]}')
            if fill:
                plt.fill_between(x, y-yerr, y+yerr, alpha=0.2)
            else:
                pass
    
    fill_str = ''
    if fill:
        fill_str = ' (bounds of 1 SD)'

    if not legend_right:
        plt.legend()      
    else:
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Distance (nm)')
    plt.title(f'Average Distance to Membrane{fill_str}')
    plt.show()

def plotBarGraph(xdata, yList, yLabels, title='', width=0.1, alpha=0.5, legend_right=False):
    N_entry = len(yList)
    midVarId = N_entry//2
    fix, ax = plt.subplots()
    if N_entry % 2 == 1:
        # odd number 
        plt.bar(xdata, yList[midVarId], width=width, alpha=alpha, label=yLabels[midVarId])
        idx = 1
        for id_lh in range(0, midVarId):
            plt.bar(xdata - 0.15*idx, yList[id_lh], width=width, alpha=alpha, label=yLabels[id_lh])
            idx += 1
        idx = 1
        for id_rh in range(midVarId+1, N_entry):
            plt.bar(xdata + 0.15*idx, yList[id_rh], width=width, alpha=alpha, label=yLabels[id_rh])
            idx += 1
    else:
        # even number 
        shiftIndex = [0.06] + [0.1]*midVarId
        
        idx = 1
        for id_lh in range(0, midVarId):
            plt.bar(xdata - idx*shiftIndex[idx-1], yList[id_lh], width=width, alpha=alpha, label=yLabels[id_lh])
            idx += 1
        
        idx = 1
        for id_rh in range(midVarId, N_entry):
            plt.bar(xdata + idx*shiftIndex[idx-1], yList[id_rh], width=width, alpha=alpha, label=yLabels[id_rh])
            idx += 1
        pass
    
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True, min_n_ticks=1))
    if not legend_right:
        plt.legend()      
    else:
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.xlabel('Cluster size (molecules)')
    plt.ylabel('Frequency')
    plt.title(title, pad=12)
    plt.show()

def plotClusterCompositionCopy(path, title_str, specialClusters=[], width=0.1, alpha=0.6, legend_right=True):
    df = pd.read_csv(path)
    csList = df['Clusters']
    if len(specialClusters) == 0:
        mols = df.columns[2:]
        freqList = [df[mol] for mol in mols]
        plotBarGraph(csList, freqList, mols, width=width, alpha=alpha, title=f'Cluster Composition{title_str}', legend_right=legend_right)
    else:
        idx = [i for i in range(len(csList)) if csList[i] in specialClusters]
        df2 = df.iloc[idx]
        mols = df.columns[2:]
        freqList = [df2[mol] for mol in mols]
        plotBarGraph(df2['Clusters'], freqList, mols, width=width, alpha=alpha, title=f'Cluster Composition{title_str}', legend_right=legend_right)