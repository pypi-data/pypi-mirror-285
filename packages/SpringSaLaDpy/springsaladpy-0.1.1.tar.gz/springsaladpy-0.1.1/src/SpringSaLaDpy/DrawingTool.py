# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 21:37:50 2019

@author: Ani Chattaraj
"""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import os
from math import atan, sin, cos
from collections import namedtuple
import re
import numpy as np

class Draw_2D_Molecule:
    def __init__(self, molName, SiteList, LinkList, outPath):
        self.molecularName = molName
        self.siteList = SiteList
        self.linkList = LinkList
        self.outPath = outPath
    
    @staticmethod
    def draw_circle(SiteObj):
        """
        modify the color string if defined site-color is invalid
        in CSS-style matplotlib implementation (like 'dark_violet') 
        LIME_GREEN : limegreen; Dark_violet : darkviolet
        """
        coor, r = SiteObj.coordinates, SiteObj.radius
        x, y = coor[2], coor[1]
        try:
            if SiteObj.color.lower() == 'white':
                circle = plt.Circle((x,y), radius=r, facecolor='lightsteelblue')
                print("White site color encountered; replaced with lightsteelblue")
            else:
                circle = plt.Circle((x,y), radius=r, facecolor=SiteObj.color)
        except:
            color = SiteObj.color.replace("_","") # "dark_violet" has to be in "darkviolet" format
            circle = plt.Circle((x,y), radius=r, facecolor=color)  
        
        return plt.gca().add_patch(circle)
    
    
    def draw_line(self, SiteObj1, SiteObj2, width):
        """
        take a pair of sites ; draw a line between the surface (excluding the radius)
        For non-linear molecules, calculates the slope between two spheres and
        place the line points along that direction.
        """
        c1, r1 = SiteObj1.coordinates, SiteObj1.radius
        c2, r2 = SiteObj2.coordinates, SiteObj2.radius
        x1, y1 = c1[2], c1[1]
        x2, y2 = c2[2], c2[1]
        
        try:
            slope = atan((y2-y1)/(x2-x1))  # in radians
            
            # pn: peripherial coordinates of site n
            p1_x, p1_y = x1 + r1 * cos(slope), y1 + r1 * sin(slope)  
            p2_x, p2_y = x2 - r2 * cos(slope), y2 - r2 * sin(slope)
            
            line = plt.Line2D((p1_x, p2_x), (p1_y, p2_y), linewidth=width, color='k')
            
            return plt.gca().add_line(line)
        except:
            print(f"Can't draw line for {SiteObj1.seqNum} & {SiteObj2.seqNum} in {self.molecularName}")
        
        
    @staticmethod
    def mapLinkToSite(Sites, Links):
        siteObj_pair = []
        for link in Links:
            s1, s2 = None, None
            for site in Sites:
                if link.Site1 == site.seqNum:
                    s1 = site
                elif link.Site2 == site.seqNum:
                    s2 = site
            siteObj_pair.append((s1,s2))
        #print(siteObj_pair)
        return siteObj_pair
    
    def displayMolecule(self, Width, saveImage):
        plt.axes()
        coor = np.array([SiteObj.coordinates for SiteObj in self.siteList])
        x_min, x_max = min(coor[:,2]), max(coor[:,2])
        #print(x_min, x_max)
        y_min = min(coor[:,1])
        #print(mod_sites)
        sizes = []
        for site in self.siteList:
            coor = site.coordinates
            x = coor[2]
            x_update = (x - x_min) + 5
            site.coordinates[2] = x_update
            self.draw_circle(site)
            sizes.append(site.radius)
        
        molLength = self.siteList[-1].coordinates[-1] - self.siteList[0].coordinates[-1]
        Largest_ball = max(sizes) + 2
        #print(molLength,  Largest_ball)
        Linked_Sites = self.mapLinkToSite(self.siteList, self.linkList)
        #print(Linked_Sites)
        for s1, s2 in Linked_Sites:
            self.draw_line(s1, s2, width=Width)
        #plt.axes(frameon=False)
        plt.axis('image')
        
        #plt.axis(xmin=0, xmax= (x_max - x_min) + 5, ymin=y_min-Largest_ball, ymax=y_min+Largest_ball)
        
        plt.xlabel('nm', fontsize=16)
        plt.ylabel('nm', fontsize=16)
        plt.tick_params(axis='x', labelsize=16)
        plt.yticks([y_min-Largest_ball,y_min+Largest_ball])
        #plt.xlim((0,35))
        #Axes.set_ylim((0,5))
        
        #plt.tick_params(labelsize='small')
        if saveImage:
            plt.savefig(self.outPath+"\\{}_pyDraw2.png".format(self.molecularName), dpi=400)

        plt.show()
    def displayMolecules(self, sList, linkList, Width=1, saveImage=False):
        y = 2
        for sites, links in zip(sList, linkList):
            
            coor = np.array([SiteObj.coordinates for SiteObj in sites])
            x_min, x_max = min(coor[:,2]), max(coor[:,2])
            sizes = []
            for site in sites:
                coor = site.coordinates
                x = coor[2]
                x_update = (x - x_min) + 1
                site.coordinates[2] = x_update
                site.coordinates[1] = y
                self.draw_circle(site)
                sizes.append(site.radius)
            
            
            Linked_Sites = self.mapLinkToSite(sites, links)
            #print(Linked_Sites)
            for s1, s2 in Linked_Sites:
                self.draw_line(s1, s2, width=Width)
            
            y += 3
           
        plt.axis('image')
        plt.axis(ymin=-1, ymax=7)
        plt.xlabel('nm', fontsize=12)
        plt.ylabel('nm', fontsize=12)
        if saveImage:
            plt.savefig(self.outPath+"/system_pyDraw_test.png", dpi=400)
        plt.show()
                
            
            
     
            
      
class ReadSimFile:
    def __init__(self,txtfile):
        self.txtfile = txtfile
        
    def getOutPath(self):
        path = [f for f in self.txtfile.split('/')]
        newpath = '/'.join(path[:-1])
        outpath = newpath + '/pyStat//pyDraw'
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        return outpath
        
    def readFile(self):
        with open(self.txtfile, 'r') as tmpfile:
            Lines = tmpfile.readlines()
            tmpfile.close()
        return Lines
    
    def getSystemVolume(self):
        Lines = self.readFile()
        Lx, Ly, Lz = 0, 0, 0
        for line in Lines:
            if re.search('L_x', line):
                Lx = float(line.split(':')[-1]) * 1e3  # um to nm
            if re.search('L_y', line):
                Ly = float(line.split(':')[-1]) * 1e3  # um to nm
            if re.search('L_z', line):
                Lz = float(line.split(':')[-1]) * 1e3  # um to nm
        system_vol = Lx*Ly*Lz
        return system_vol
    
    def getSiteStats(self):
        # location: Membrane, extra-cellular or intra-cellular
        # coordinates: [x,y,z]
        Site = namedtuple("Site", ["seqNum", "compartment", "radius", "color", "coordinates"])
        Link = namedtuple("Link", ["Site1", "Site2"])
        LineIndex = []
        molNames, molcounts = [], []
        Lines = self.readFile()
        
        for index, line in enumerate(Lines):
            if not re.search('[*]', line):
                if re.search('MOLECULE', line):
                    specs = line.split(':')[-1].split()
                    if len(specs) > 2:
                        molNames.append(specs[0].replace('"',''))
                        molcounts.append(int(specs[3]))
                        LineIndex.append(index)
        LineIndex.append(len(Lines))
        #print(LineIndex)
        SiteList = []
        LinkList = []
        i = 0
        while i < len(LineIndex) - 1:
            subLines = Lines[LineIndex[i]: LineIndex[i+1]]
            siteList = []
            linkList = []
            for index, line in enumerate(subLines):
                if re.search("SITE", line) and not re.search("[*]", line):
                    line1, line2 = subLines[index+1], subLines[index+2]
                    line = line.split(':')
                    specs = line1.split(':')[-1].split()
                    coors = line2.split()
                    #print(line)
                    siteSpecs = {"seqNum":line[0].strip(), "compartment":line[1].strip(), 
                                 "radius":float(specs[3]), "color":specs[7], 
                                 "coordinates": [float(coors[1]), float(coors[3]), float(coors[5])]}
                    S = Site(**siteSpecs)
                    #print(S)
                    siteList.append(S)
                elif re.search("LINK", line):
                    line = line.split(':')
                    site_pair = {"Site1":line[1].strip().upper(), "Site2":line[4].strip().upper()}
                    linkList.append(Link(**site_pair))
                    
            SiteList.append(siteList)
            LinkList.append(linkList)
            
            i += 1
        
        return molNames, molcounts, SiteList, LinkList
    
    @staticmethod
    def calculateLinkerDistance(linkedSites):
        dist = []
        for site1, site2 in linkedSites:
            p1, p2 = site1.coordinates, site2.coordinates
            d = np.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2)
            dist.append(d)
        return dist
    
    def printStructuralParameters(self, e2eList):
        V = self.getSystemVolume()
        occupied_vol = []
        mols, molcounts, sites, links = self.getSiteStats()
        simName = self.txtfile.split('/')[-1].replace('.txt','')
        print(f'\nSystem: {simName}\n')
        for mol, num, site, link, e2ed in zip(mols, molcounts, sites, links, e2eList):
            linkedSites = Draw_2D_Molecule.mapLinkToSite(site, link)
            LD = self.calculateLinkerDistance(linkedSites)
            #print(LD)
            """
            Caculate the eucledian distance using matrix algebra:
                coor = np.array([s.coordinates for s in site])
                linkerLength = np.sqrt(np.sum((np.diff(coor, axis=0))**2, axis=1))
            """
            
            m_LL = np.mean(LD)
            diameters = np.array([s.radius for s in site])*2
            m_diameter = np.mean(diameters)
            ex_vol = sum(diameters**3)*num
            sp = (e2ed*m_LL)/m_diameter
            occupied_vol.append(ex_vol)
            print(f"molecule: {mol}")
            print(f"mean_LinkerLength: {m_LL:.3f} nm")
            print(f"mean_diameter: {m_diameter:.3f} nm")
            print(f"end_To_end distance: {e2ed:.3f} nm")
            print(f"Excluded volume: {ex_vol:.3f} nm3")
            print(f"SP = {sp:.5f}\n")
        fraction_vol_occupied = (sum(occupied_vol)/V)*100
        print(f"System volume = {V} nm3\nOccupied volume fraction = {fraction_vol_occupied:.3f} %")
            
               
            
    
    
    