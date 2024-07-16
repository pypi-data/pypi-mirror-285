import numpy as np
from .Reader_functions import *
from .data_locator import *
from .input_file_extraction import *


def Describe_input_file(search_directory, search_term='', links=False, reactions=False, kinetics=False):
    molecules, split_file = read_input_file(search_directory, search_term)

    print('Molecules:\n')

    #Molecule Processing
    multi_state_types = []
    multi_state_sites = []
    for item in molecules:   
        #General Info
        typStr = ''
        split_general_info = item[0].split()
        site_types = int(split_general_info[6])
        for j in range(2,2+site_types):
            type_split = item[j].split()
            type_name = type_split[2]
            states = [i for i in type_split if '"' in i]
            site_name = states.pop(0)
            typStrAddition = ''
            if len(states) == 1:
                pass
            else:
                for state in states:
                    typStrAddition = typStrAddition + f'{state[1:-1]}, '
                typStrAddition = typStrAddition[:-2]
                typStrAddition = f' ({len(states)} possible states: {typStrAddition})'
                multi_state_types.append(type_name[1:-1])
            typStr = f'{typStr}{type_name[1:-1]}{typStrAddition}, '
            if kinetics:
                initial_count = f' (Initial Count: {split_general_info[4]})'
            else:
                initial_count = ''
        print(f'MOLECULE: {split_general_info[1]}{initial_count}')
        print(f'This molecule has {split_general_info[6]} site types: {typStr[:-2]}')

        #Sites
        total_sites = int(split_general_info[8])
        site_data = []
        for i in range(3 + site_types, 3 + site_types + 3*total_sites, 3):
            site_split1 = item[i].split()
            site_split2 = item[i+1].split()
            if len(site_split2) > 11:
                multi_state_sites.append(int((i-site_types)/3) - 1)
            site = [f'{site_split1[0]} {site_split1[1]}', site_split1[3], site_split2[2][1:-1], site_split2[8]]
            site_data.append(site)

        #Sites (default ordering)
        '''
        print(f'\nIt consists of {total_sites} connected sites:')
        for site in site_data:
            print(f'Site {site[0][5:]} ({site[1]}) of type "{site[2]}"')
            pass
        '''

        #Sites (grouped by type)
        sites_reordered = []
        site_type_names = []  
        for site in site_data:
            if site[2] not in site_type_names:
                site_type_names.append(site[2])
                #Site type name, Numpy Array(#Intracellular, #Extracellular, #Membrane), [list of sites], color 
                sites_reordered.append([site[2], location2vec(site[1]), [site[0]], site[3].lower().capitalize()])
            else:
                for reordered_site in sites_reordered:
                    if site[2] == reordered_site[0]:
                        reordered_site[1] = reordered_site[1] + location2vec(site[1])
                        reordered_site[2].append(site[0])
        
        print(f'\nIt consists of {total_sites} connected sites:')
        for reordered_site in sites_reordered:
            location_list = list(reordered_site[1])
            site_list = list(reordered_site[2])
            for index in location_list:
                addStr = ''
                if location_list[0] != 0:
                    addStr = addStr + f'{location_list[0]} {reordered_site[3]} intracellular, '
                if location_list[1] != 0:
                    addStr = addStr + f'{location_list[1]} {reordered_site[3]} extracellular, '
                if location_list[2] != 0:
                    addStr = addStr + f'{location_list[2]} {reordered_site[3]} membrane, '
            addStr2 = ''
            for index in site_list:
                addStr2 = addStr2 + 'Site' + index[4:] + ', '
            if ',' in addStr2[:-2]:
                print(f'Type {reordered_site[0]}: {addStr[:-2]} sites ({addStr2[:-2]})')
            else:
                print(f'Type {reordered_site[0]}: {addStr[:-2]} site ({addStr2[:-2]})')        
        
        total_links = int(split_general_info[10])
        link_data = []
        for i in range(4 + site_types + 3*total_sites, 4 + site_types + 3*total_sites + total_links):
            split_link = item[i].split()
            link = [split_link[2], split_link[5]]
            link_data.append(link)
        
        #[[link index, list of links],[link index, list of links],...]
        link_lists = []
        for site in site_data:
            split_site = site[0].split()
            link_count_init = [split_site[1], []]
            link_lists.append(link_count_init)
        for link_list in link_lists:
            for link in link_data:
                if link_list[0] == link[0]:
                    link_list[1].append(link[1])
                elif link_list[0] == link[1]:
                    link_list[1].append(link[0])
                else:
                    pass

        link_lists_remaining = link_lists

        #Links (no repeated entries)
        '''
        print(f'\nThis molecule had {total_links} total links between sites:')
        while True:
            record_length = 0
            for link_list in link_lists:
                if len(link_list[1]) > record_length:
                    record_length = len(link_list[1])
                    record_loc = int(link_list[0])
            if record_length == 0:
                break

            site_str = ''
            for site in link_lists_remaining[record_loc][1]:
                site_str = f'{site_str} site {site},'
            
            print(f'Site {record_loc} is connected to{site_str[:-1]}')
            for link_list_remaining in link_lists_remaining:
                link_list_remaining[1] = [i for i in link_list_remaining[1] if i != str(record_loc)] 
            link_lists_remaining[record_loc][1] = []
        print('\n')
        '''


        #All links for all sites
        if links:
            print(f'\nIt has {total_links} total links between sites:')
            for link in link_lists:
                site_str = ''
                for site in link[1]:
                    site_str = f'{site_str} site {site},'
                print(f'Site {link[0]} is connected to{site_str[:-1]}')
        print('------------------------------------------------------------------------------------------------------------\n')

    if reactions:
        transition_reactions, allosteric_reactions, binding_reactions = read_reactions(split_file)
        print('************************************************************************************************************\n')
        print('Reaction Rules')
        #State Transition Reactions
        if len(transition_reactions) != 0:
            print(f'\nState Transition Reactions: {len(transition_reactions)}')
            for transition_reaction in transition_reactions:
                split_reaction = transition_reaction.split('\'')
                split_condition = split_reaction[10].split()
                condition = split_condition[-1]

                if split_reaction[13] not in multi_state_types:
                    state = ''
                elif split_reaction[15] == 'Any_State':
                    state = ' in any state'
                else:
                    state = ' of state ' + split_reaction[15]
                
                if condition == 'None':
                    condition_str = ''
                elif condition == 'Free':
                    condition_str = f'provided that it is free'
                else:
                    condition_str = f'provided that it is bound to site {split_reaction[13]} of a molecule {split_reaction[11]}{state}'

                if kinetics:
                    rate = f'at a rate of {split_reaction[10].split()[1]} s-1 '
                else:
                    rate = ''
                print(f'A site of type {split_reaction[5]} in a {split_reaction[3]} molecule can change its state from {split_reaction[7]} to {split_reaction[9]} {rate}{condition_str}')

        #Allosteric Reactions
        if len(allosteric_reactions) != 0:
            print(f'\nAllosteric Reactions: {len(allosteric_reactions)}')
            for allosteric_reaction in allosteric_reactions:
                split_reaction = allosteric_reaction.split('\'')
                split_allosteric_site = split_reaction[-3].split()

                if int(split_allosteric_site[3]) not in multi_state_sites:
                    condition = ''
                else:
                    condition = f'provided that Site {split_allosteric_site[3]} of the same molecule is in state {split_reaction[-2]}'

                if kinetics:
                    rate = f'at a rate of {split_reaction[8].split()[1]} s-1 '
                else:
                    rate = ''
                print(f'{split_reaction[4][3:-3]} of molecule {split_reaction[3]} can change its state from {split_reaction[5]} to {split_reaction[7]} {rate}{condition}')

        #Biomolecular Binding Reactions
        if len(binding_reactions) != 0:
            print(f'\nBiomolecular Binding Reactions: {len(binding_reactions)}')
            for binding_reaction in binding_reactions:
                split_reaction = binding_reaction.split('\'')
                
                if split_reaction[5] not in multi_state_types:
                    state1 = ''
                elif split_reaction[7] == 'Any_State':
                    state1 = ' (in any state)'
                else:
                    state1 = f' (of state {split_reaction[7]})'
                
                if split_reaction[11] not in multi_state_types:
                    state2 = ''
                elif split_reaction[13] == 'Any_State':
                    state2 = ' (in any state)'
                else:
                    state2 = f' (of state {split_reaction[13]})'

                if kinetics:
                    on_rate = f'\n\tOn rate: {split_reaction[14].split()[1]} uM-1.s-1,'
                    off_rate = f'off rate: {str(split_reaction[14].split()[3])} s-1'
                    #if float(split_reaction[14].split()[3]) != 0.0:
                else:
                    on_rate = off_rate = ''
                print(f'Site {split_reaction[5]} of molecule {split_reaction[3]}{state1} can bind to site {split_reaction[11]} of {split_reaction[9]}{state2} {on_rate} {off_rate}')

