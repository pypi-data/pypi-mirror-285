# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 14:19:54 2019

@author: Ani Chattaraj
"""
from SpringSaLaDpy.DrawingTool import Draw_2D_Molecule, ReadSimFile
from data_locator import find_txt_file

def display_molecules(path):
    
    txtfile = find_txt_file(path)

    #txtfile = "Z:/Nwasp_regulation/SpringSaLaD_Models/Newer_NWASP/2nwasp_Arp23_allostericRxn_corr_SIMULATIONS/2nwasp_arp23_allosRxn_corr_SIM.txt"
    #print(file)

    saveImage = False
    simfile = ReadSimFile(txtfile)
    #outpath = simfile.getOutPath()
    outpath = ''
    molNames, molcounts, SiteList, LinkList = simfile.getSiteStats()

    #print(SiteList)
    LineWidth = 0.75

    for mol, site, link in zip(molNames, SiteList, LinkList):
        
        print(mol + ':')
        mol2D = Draw_2D_Molecule(mol,site,link,outpath)
        mol2D.displayMolecule(LineWidth, saveImage)
        #mol2D.displayMolecules(SiteList,LinkList, LineWidth, saveImage)

