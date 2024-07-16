import os
from .data_locator import data_file_finder
from .digit_counter import count_digits

def find_nearest_time(search_directory, path_list, time, dt, search_term):
    if time != None:
        #Round to nearest available time based on dt value
        if round(time % dt, 7) >= dt/2:
            time = round(time - (time % dt) + dt, 7)
        else:
            time = round(time - (time % dt), 7)

        decimals = count_digits(dt, 7)
        time = format(float(time), f'.{decimals}f')
        file = data_file_finder(search_directory, path_list, search_term=time, no_warnings=True)
    else:
        file = data_file_finder(search_directory, path_list, search_term=search_term, no_warnings=True)
        time = float(os.path.split(file)[1].split('_')[2])
    return time, file

