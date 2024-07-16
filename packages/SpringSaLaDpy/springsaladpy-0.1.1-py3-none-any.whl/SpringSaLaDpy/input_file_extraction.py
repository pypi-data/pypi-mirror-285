import os
from .data_locator import *

def read_input_file(directory_path, search_term=''):
    path = find_txt_file(directory_path, search_term)

    with open(path, "r") as f:
        lines = f.readlines()

    split_file = []
    current_list = []

    for line in lines:
        if line[0:3] == '***':
            split_file.append(current_list)
            current_list = []
        current_list.append(line.strip())
    split_file.append(current_list)
    split_file.pop(0)

    if len(split_file) < 10:
        print(f'Error: Input file {path} doesn\'t match the expected format. Please ensure your input file is unmodified and that there are no other .txt files at the top level of your search directory.')

    #Extract molecule data
    molecules = []
    molecule = []
    for line in split_file[2]:
        if line[0:9] == 'MOLECULE:':
            molecules.append(molecule)
            molecule = []
        molecule.append(line)
    molecules.append(molecule)    
    molecules.pop(0)

    return(molecules, split_file)

def read_reactions(split_file):
    #Extract reaction data
    transition_reactions = []
    allosteric_reactions = []
    binding_reactions = []
    reaction_types = [['transition_reactions', 5], ['allosteric_reactions', 6], ['binding_reactions', 7]]
    for reaction_type in reaction_types:
        for line in split_file[reaction_type[1]]:
            if line != '':
                exec(reaction_type[0] + '.append(line)')
        exec(reaction_type[0] + '.pop(0)')
    return(transition_reactions, allosteric_reactions, binding_reactions)