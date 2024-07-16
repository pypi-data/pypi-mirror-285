import os
import fnmatch
import glob

#Finds the last txt file in the search_directory
def find_txt_file(search_directory, search_term=''):
    if search_term != '':
        return find_files(search_directory, search_term)
    else:
        match = None
        for file in os.listdir(search_directory):
            if file.endswith(".txt"):
                match = os.path.join(search_directory, file)
        return match

#Finds the last file in a given directory that contains search_term in the file name
def find_files(search_directory, search_term, no_warnings=False):
    match = None
    count = 0
    for filename in os.listdir(search_directory):
        if search_term in filename:
            count += 1
            match = os.path.join(search_directory, filename)
    if not no_warnings:
        if match == None:
            print(f'Error, could not find the search term "{search_term}" in any file in the search directory "{search_directory}"')
        if count > 1:
            print(f'Warning, there are multiple files that contain the search term "{search_term}".\nThe file "{match}" is currently selected.\nPlease provide a more specific search term if this is not the file you want\n')
    return match

def data_file_finder(search_directory, path_list, search_term = None, file_name = None, run = None, no_warnings=True):
    if file_name == None:
        file_name = find_txt_file(search_directory)
    else:
        file_name = os.path.join(search_directory, file_name)
    
    augmented_path_list = []
    if search_directory[-7:] == '_FOLDER':
        augmented_path_list = [search_directory] + path_list
    else:
        augmented_path_list = [file_name[:-4] + '_FOLDER'] + path_list
    lower_search_directory = os.path.join(*augmented_path_list)

    if run != None:
        result = find_files(lower_search_directory, f'Run{run}', no_warnings=no_warnings)
    else:
        result = find_files(lower_search_directory, search_term, no_warnings=no_warnings)
    return result