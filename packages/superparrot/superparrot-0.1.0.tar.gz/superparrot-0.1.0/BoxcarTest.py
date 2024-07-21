import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter

import parrot
os.chdir(r"C:\Users\Tim\Downloads\boxcar_test\2024-06-26")

def read_boxcar(file_name,
                boxcar_path="boxcars/0/sample",
                position_path="demods/0/sample.auxin0"):
    with h5py.File(file_name, 'r') as f:
        trace_ids = list(f.keys())
        # Read-in first trace
        trace_id = trace_ids[0]
        # Read out device name, e.g. dev2179
        dev = list(f[f"{trace_id}"].keys())
        # Take first element from list (there should only be one device)
        dev = dev[0]
        # Connect to path
        path = f"{trace_id}/{dev}/"
        # Read-in timebase
        timebase = f[path + boxcar_path].attrs["timebase"]
        # Read-in time array
        time = f[path + boxcar_path + "/timestamp"][:]
        # Read-in position and THz signal
        position = f[path + position_path + "/value"][:]
        signal = f[path + boxcar_path + "/value"][:]
        # Keep only values, which are not NaN
        time = time[~np.isnan(signal)]
        position = position[~np.isnan(signal)]
        signal = signal[~np.isnan(signal)]

        time = time[~np.isnan(position)]
        signal = signal[~np.isnan(position)]
        position = position[~np.isnan(position)]
        # Concert timesamples to time in [s]
        time = time * timebase
        # Start measurement at 0 s
        time -= np.min(time)
        data = {"time": time,
                "position": position,
                "signal": signal}
    return data

data = read_boxcar('100kHz-0,5GaP_newmount_THz_00000.h5')
peakpeak_position = np.max(data["position"]) - np.min(data["position"])
my_scale = 2 * 6.6e-11 / 1
light = read_boxcar('100kHz-0,5GaP_newmount_THz_00000.h5')
dark1 = read_boxcar('100kHz-0,5GaP_newmount_dark1_00000.h5')
dark2 = read_boxcar('100kHz-0,5GaP_newmount_dark2_00000.h5')
process_obj = parrot.Process()
data = process_obj.thz_and_two_darks(light, dark1, dark2, scale = my_scale, debug=True)
plt.show(block=False)
post_obj = parrot.PostProcessData(data)
data = post_obj.correct_systematic_errors()
data = post_obj.cut_data(time_start=-10e-12)
data = post_obj.super_gaussian(window_width=0.6)
data = post_obj.calc_fft()
data = post_obj.get_statistics()

plot_obj = parrot.Plot(max_THz_frequency=10e12)
plot_obj.simple_multi_cycle(data)
plt.show(block=False)