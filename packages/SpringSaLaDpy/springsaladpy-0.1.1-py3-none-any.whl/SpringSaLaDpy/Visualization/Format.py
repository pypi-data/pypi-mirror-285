import os
from SpringSaLaDpy.data_locator import find_txt_file
from SpringSaLaDpy.input_file_extraction import read_input_file
from SpringSaLaDpy.time_rounder import find_nearest_time
from .times_2_title import times_2_title

#Switch to the _FOLDER folder if you're not already there and round times to the nearest available values.
def format(search_directory, times, file_type):

    input_file = find_txt_file(search_directory)

    #Round to nearest available time based on dt value
    _, split_file = read_input_file(search_directory)
    if file_type == 'viewer':
        dt = float(split_file[0][5][10:])
    else:
        dt = float(split_file[0][4][9:])
    dt_trimmed =  dt - 1e-12
    total_time = float(split_file[0][1][12:])
    
    total_time = round(total_time - (total_time % dt_trimmed),7)
    rounded_times = []
    for time in times:
        rounded_time = float(find_nearest_time(search_directory, ['data', 'Run0'], time, dt, 'Clusters_Time')[0])
        if rounded_time <= total_time and not rounded_time < 0:
            rounded_times.append(rounded_time)
            if rounded_time != time:
                print(f'Warning, the provided time {time} has been rounded to the closest available value: {rounded_time}')
        else:
            print(f'Warning, the provided time {time} is not between 0 and the last available time: {total_time}')
    if rounded_times == []:
        print(f'Warning, no valid time points. Now defaulting to the last time point: {total_time}')
        rounded_times.append(total_time)

    rounded_times.sort()
    title_str = times_2_title(rounded_times)

    return input_file, rounded_times, title_str
