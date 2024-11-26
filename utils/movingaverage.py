def moving_average(window, window_size):
    window_average = round(sum(window) / window_size, 2)
    
    return window_average