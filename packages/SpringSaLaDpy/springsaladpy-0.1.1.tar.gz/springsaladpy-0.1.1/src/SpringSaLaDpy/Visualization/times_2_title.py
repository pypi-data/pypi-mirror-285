def times_2_title(times):
    if len(times) > 1:
            title_str = ' at: '
            for time in times:
                title_str = f'{title_str}{str(time)}, '
            title_str = title_str[:-2]
    else:
        title_str = ' at '
        title_str = f'{title_str}{str(times[0])}'
    title_str = title_str + ' s'
    return title_str