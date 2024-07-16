# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 17:47:10 2019

@author: Ani Chattaraj
"""

from .DataPy import ReadInputFile, InterSiteDistance, ProgressBar, displayExecutionTime
import re
import numpy as np
import networkx as nx
from glob import glob
import matplotlib.pyplot as plt

def connected_component_subgraphs(G):
    for c in nx.connected_components(G):
        yield G.subgraph(c)

class CrossLinkIndex:
    
    def __init__(self, txtfile, ss_timeSeries, activeSites=None):
        self.simObj = ReadInputFile(txtfile)
        self.ss_timeSeries = ss_timeSeries
        tf, dt, dt_data, dt_image = self.simObj.getTimeStats()
        inpath = self.simObj.getInpath() + "/data"
        numRuns = self.simObj.getNumRuns()
        self.N_frames = int(tf/dt_image)
        self.inpath = inpath
        self.numRuns = numRuns
        self.activeSites = activeSites
    
    def __repr__(self):
        simfile = self.simObj.txtfile.split('/')[-1]
        info = f"Class : {self.__class__.__name__}\nSystem : {simfile}"
        return info
    @staticmethod
    def getMolIds(molfile, molName):
        molDict = {}
        mIds = []
        with open(molfile, 'r') as tmpfile:
            for line in tmpfile:
                line = line.strip().split(',')
                if line[-1] == molName:
                    mIds.append(line[0])
        molDict[molName] = mIds
        return molDict
    @staticmethod
    def getSiteIds(sitefile, molName):
        siteDict = {}
        sIds = []
        with open(sitefile, 'r') as tmpfile:
            for line in tmpfile:
                line = line.strip().split(',')
                if line[-1].split()[0] == molName:
                    sIds.append(line[0])
        siteDict[molName] = sIds
        return siteDict
    @staticmethod
    def getRevDict(myDict):
        # k,v = key : [val1, val2, ...]
        revDict = {}
        for k,v in myDict.items():
            for val in v:
                revDict[val] = k
        return revDict
    @staticmethod
    def splitArr(arr, n):
        subArrs = []
        if (len(arr)%n == 0):
            f = int(len(arr)/n)
            i = 0
            while (i < len(arr)):
                sub_arr = arr[i : i+f]
                i += f
                subArrs.append(sub_arr)
            return subArrs
        else:
            print(f"Can't split the given array (length = {len(arr)}) into {n} parts")
    
    def getReactiveSiteIDs(self):
        RS_ids = []
        sIDfile = InterSiteDistance.findFile(self.inpath, self.numRuns, "SiteIDs")
        if self.activeSites == None:
            activeSites = self.simObj.getReactiveSites()
            #print('Active siteList based on rxnrules ... ')
            #print(activeSites)
        else:
            activeSites = self.activeSites
        
        with open(sIDfile,'r') as sf:
            lines = sf.readlines()
            for line in lines:
                line = line.split(',')
                if line[-1].split()[-1] in activeSites:
                    RS_ids.append(line[0])
        return RS_ids
    
    def mapSiteToMolecule(self):
        #inpath = self.simObj.getInpath() + "\data"
        #numRuns = self.simObj.getNumRuns()
        sIDfile = InterSiteDistance.findFile(self.inpath, self.numRuns, "SiteIDs")
        mIDfile = InterSiteDistance.findFile(self.inpath, self.numRuns, "MoleculeIDs")
        molName, molCount = self.simObj.getMolecules()
        molIDs, siteIDs = {}, {}
        for mol in molName:
            molIDs.update(self.getMolIds(mIDfile, mol))
            siteIDs.update(self.getSiteIds(sIDfile, mol))
        spmIDs = {} # sites per molecule
        for mol, count in zip(molName, molCount):
            #molDict = {}
            arr = self.splitArr(siteIDs[mol], count)
            mol_ids = molIDs[mol]
            d = dict(zip(mol_ids, arr))
            spmIDs.update(d)
        rev_spm = self.getRevDict(spmIDs)
        return rev_spm
    @staticmethod
    def getBindingStatus(frame):
        IdList, linkList = [], [] 
        for line in frame:
            if re.search("ID", line):
                IdList.append(line.split()[1])
            if re.search("Link", line):
                line = line.split()
                linkList.append((line[1], line[3]))
        return IdList, linkList
    
    def getSteadyStateFrameIndices(self, viewerfile):
        frame_indices = []
        ss_indices = [] 
        tps = []
        index_pairs = []
        with open(viewerfile, 'r') as tmpfile:
            lines = tmpfile.readlines()
            for i, line in enumerate(lines):
                if re.search("SCENE", line):
                    frame_indices.append(i)
                    tp = lines[i+1].split()[-1]
                    tps.append(tp)
                    if any([np.isclose(float(tp), t) for t in self.ss_timeSeries]):
                        ss_indices.append(i)
            frame_indices.append(len(lines))
        for ii, elem in enumerate(frame_indices):
            if elem in ss_indices:
                index_pairs.append((elem, frame_indices[ii+1]))
        return tps, index_pairs
    
    @staticmethod
    def createGraph(IdList, LinkList):
        G = nx.Graph()
        G.add_nodes_from(IdList)
        G.add_edges_from(LinkList)
        return G
    
    def getSI(self, viewerfile):
        # SI : saturation index = bound binding sites / total binding sites
        CS_list = [] # list of clusters
        SI_list = []
        msm = self.mapSiteToMolecule()
        completeTrajectory = False
        tps, index_pairs = self.getSteadyStateFrameIndices(viewerfile)
        RS_list = self.getReactiveSiteIDs()
        
        if len(tps) != self.N_frames + 1:
            #print("N_frames : ", len(tps))
            pass
        else:
            completeTrajectory = True
            #print("frames : ", len(tps))
            with open(viewerfile, 'r') as infile:
                lines = infile.readlines()
                for i,j in index_pairs:
                    current_frame = lines[i:j]
                    cluster_index = 0
                    Ids, Links = self.getBindingStatus(current_frame)
                    mIds, mLinks = [msm[k] for k in Ids], [(msm[k1], msm[k2]) for k1,k2 in Links]
                    sG = self.createGraph(Ids, Links)
                    mG = self.createGraph(mIds, mLinks)
                    #G.subgraph(c) for c in connected_components(G)
                    for sg, mg in zip(connected_component_subgraphs(sG), connected_component_subgraphs(mG)):
                        #print(f"cluster {cluster_index}")
                        cluster_index += 1
                        sites = list(sg.nodes)
                        mols = list(mg.nodes)
                        site_pairs = list(sg.edges())
                        if len(mols) == 1:
                            pass  # excluding the monomers
                        else:
                            RSites = [s for s in sites if s in RS_list]
                            tmpList = [(id1,id2) for id1,id2 in site_pairs if msm[id1] != msm[id2]]
                            bound_sites = set([id1 for id1,id2 in tmpList] + [id2 for id1,id2 in tmpList])
                            bound_Rsites = [bs for bs in bound_sites if bs in RSites]
                            freeSites = len(RSites) - len(bound_Rsites)
                            #print('Rsites')
                            #print(RSites)
                            #print('Bound sites')
                            #print(bound_sites)
                            #print()
                            SI = len(bound_Rsites)/len(RSites) 
                            SI_list.append(SI)
                            CS_list.append(len(mols))
        if completeTrajectory:
            return CS_list, SI_list
        else:
            return None
        
    def getRadialDist(self, viewerfile):
        # SI : saturation index = bound binding sites / total binding sites
        CS_list = [] # list of clusters
        SI_list = []
        msm = self.mapSiteToMolecule()
        completeTrajectory = False
        tps, index_pairs = self.getSteadyStateFrameIndices(viewerfile)
        RS_list = self.getReactiveSiteIDs()
        
        if len(tps) != self.N_frames + 1:
            #print("N_frames : ", len(tps))
            pass
        else:
            completeTrajectory = True
            #print("frames : ", len(tps))
            with open(viewerfile, 'r') as infile:
                lines = infile.readlines()
                for i,j in index_pairs:
                    current_frame = lines[i:j]
                    #print(current_frame)
                    cluster_index = 0
                    Ids, Links = self.getBindingStatus(current_frame)
                    mIds, mLinks = [msm[k] for k in Ids], [(msm[k1], msm[k2]) for k1,k2 in Links]
                    sG = self.createGraph(Ids, Links)
                    mG = self.createGraph(mIds, mLinks)
                    #G.subgraph(c) for c in connected_components(G)
                    for sg, mg in zip(connected_component_subgraphs(sG), connected_component_subgraphs(mG)):
                        #print(f"cluster {cluster_index}")
                        cluster_index += 1
                        sites = list(sg.nodes)
                        mols = list(mg.nodes)
                        site_pairs = list(sg.edges())
                        if len(mols) == 1:
                            pass  # excluding the monomers
                        else:
                            RSites = [s for s in sites if s in RS_list]
                            tmpList = [(id1,id2) for id1,id2 in site_pairs if msm[id1] != msm[id2]]
                            bound_sites = set([id1 for id1,id2 in tmpList] + [id2 for id1,id2 in tmpList])
                            bound_Rsites = [bs for bs in bound_sites if bs in RSites]
                            freeSites = len(RSites) - len(bound_Rsites)
                            #print('Rsites')
                            #print(RSites)
                            #print('Bound sites')
                            #print(bound_sites)
                            #print()
                            SI = len(bound_Rsites)/len(RSites) 
                            SI_list.append(SI)
                            CS_list.append(len(mols))
        if completeTrajectory:
            return CS_list, SI_list
        else:
            return None


    @displayExecutionTime
    def getSI_stat(self):
        print("Calculating SI ...")
        CS_stat, SI_stat = [], []
        outpath = self.simObj.getOutpath("SI_stat")
        vfiles = glob(self.simObj.getInpath() + "/viewer_files/*.txt")
        #vfiles = glob(self.simObj.getInpath() + "/test/*.txt")
        IVF = [] # Incomplete Viewer File
        N_traj = len(vfiles)
        
        for i, vfile in enumerate(vfiles):
            res = self.getSI(vfile)
            if res == None:
                #print(f"Run{i} : None")
                IVF.append(vfile)
            else:
                #print(res)
                CS_stat.extend(res[0])
                SI_stat.extend(res[1])
            ProgressBar("Progress", (i+1)/N_traj)
        
        with open(outpath + "/CS_stat.txt", "w") as of1, open(outpath + "/SI_stat.txt", "w") as of2:
            np.savetxt(of1, np.array(CS_stat))
            np.savetxt(of2, np.array(SI_stat))
        
        completeTrajCount = N_traj - len(IVF)
        ss_tp1000 = [t*1e3 for t in self.ss_timeSeries]
        with open(outpath + "/Sampling_stat.txt","w") as of:
            of.write(f"Complete Trajectories : {completeTrajCount}\n\n")
            of.write(f"Steady state timepoints (ms): {ss_tp1000}\n\n")
            if len(IVF) > 0:
                for ivf in IVF:
                    ivf = ivf.split('/')[-1]
                    of.write(f"{ivf}\n")
        print(f"Complete Trajectories : {completeTrajCount}")
        
        print("CS array:", len(CS_stat))
        print("SI_array:", len(SI_stat))
    
    def plot_SI_stat(self, scatter=True, hist=False, fs=18, color='b', xticks=None, yticks=None, title_str='', size_threshold_mean=10, grouping='all'):
        path = self.simObj.getInpath() + "/pyStat/SI_stat"
        simfile = self.simObj.txtfile.split('/')[-1]
        name = simfile.replace(".txt","")
        try:
            cs_arr = np.genfromtxt(path + "/CS_stat.txt", delimiter=',')
            ce_arr = np.genfromtxt(path + "/SI_stat.txt", delimiter=',')
            cs_arr, ce_arr = cs_arr[:-1], ce_arr[:-1]
            meanVal = np.mean(ce_arr)
            if scatter:
                xy = [(x,y) for x,y in zip(cs_arr, ce_arr)]
                freq_dict = {p: xy.count(p) for p in set(xy)}
                tot_count = sum(freq_dict.values())
                x_counts = {}
                for x, y in xy:
                    if x in x_counts:
                        x_counts[x] += 1
                    else:
                        x_counts[x] = 1
                cs_count = {p: x_counts[p[0]] for p in xy}

                if grouping=='col':
                    freq_dict = {k: (v/cs_count[k]) for k,v in freq_dict.items()}
                else:
                    freq_dict = {k: (v/tot_count) for k,v in freq_dict.items()}
                cs,ce,freq = [], [], []
                
                for p,f in freq_dict.items():
                    cs.append(p[0])
                    ce.append(p[1])
                    freq.append(f)
                
                plt.figure(figsize=(6,3))
                sc = plt.scatter(cs,ce,c=freq, s=50, cmap='rainbow')
                ce_gt = [ce for ce,cs in zip(ce,cs) if cs > size_threshold_mean]
                if ce_gt != []:
                    m_ce = sum(ce_gt)/len(ce_gt)
                    plt.axhline(m_ce, ls='dashed', lw=1.5, 
                                color='k', label=f'mean = {m_ce:.3f}')
                    plt.legend(fontsize=16)
                else:
                    pass
                cbar = plt.colorbar(sc)
                cbar.ax.set_ylabel('Frequency')
                
                #plt.scatter(cs_arr, ce_arr, color=color, label="mean SI = {:.4f}".format(meanVal))
                plt.xlabel("Cluster size (molecules)", fontsize=fs)
                plt.ylabel("Bound fraction", fontsize=fs)
                if not xticks == None:
                    plt.xticks(ticks=xticks)
                if not yticks == None:
                    plt.yticks(ticks=yticks)
                #plt.title(name, fontsize=16)
                plt.title("Cluster Bound Fraction Scatter Plot" + title_str, fontsize=16)
                plt.show()
            if hist and grouping=='col':
                print('Warning, histogram hidden when grouping=\'col\'. Please switch to grouping=\'all\' if you want to see the histogram.')
            if hist and grouping=='all':
                plt.subplots(figsize=(5,3))
                weights = np.ones_like(ce_arr)/len(ce_arr)
                bins=int(np.sqrt(len(ce_arr)))
                plt.hist(ce_arr, bins=20, weights=weights, color=color, label="mean BF = {:.4f}".format(meanVal))
                plt.axvline(meanVal, ls ='dashed', lw=1, color='k')
                plt.xlabel("Bound Fraction (BF)", fontsize=fs)
                plt.ylabel("Frequency", fontsize=fs)
                #plt.title(name)
                plt.title(f"Cluster Bound Fraction Histogram Plot" + title_str)
                plt.legend()
            
            
        except:
            print(f"No files found inside {path}")