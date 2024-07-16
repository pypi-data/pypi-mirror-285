import os

def format_directory(search_directory):
    if os.path.split(search_directory)[1][-7:] == '_FOLDER':
        plotting_path = search_directory
    else:
        plotting_path = os.path.join(search_directory, os.path.split(search_directory)[1][:-12] + '_FOLDER')

    return plotting_path