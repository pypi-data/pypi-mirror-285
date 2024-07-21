import os
# To read-in the raw data
import h5py
import numpy as np
import matplotlib

matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
from scipy.constants import c

import parrot

os.chdir(r"Z:\Nextcloud\scratch\TimScratch\parrot")


def get_data(file_name, trace_id="000"):
    with h5py.File(file_name, "r") as f:
        timebase = f[trace_id + "/dev2179/boxcars/0/sample/"].attrs["timebase"]
        time = f[trace_id + "/dev2179/boxcars/0/sample/timestamp"][:]
        position = f[trace_id + "/dev2179/demods/0/sample.auxin0/value"][:]
        signal = f[trace_id + "/dev2179/boxcars/0/sample/value"][:]
        # Keep only values, which are not NaN
        time = time[~np.isnan(signal)]
        position = position[~np.isnan(signal)]
        signal = signal[~np.isnan(signal)]
        time = time[~np.isnan(position)]
        signal = signal[~np.isnan(position)]
        position = position[~np.isnan(position)]
        # Concert timesamples to time in [s]
        time = time * timebase
        time -= np.min(time)
        data = {"time": time, "position": position, "signal": signal}
        return data


light = get_data("2024-07-02_650umMNA_00000.h5", "000")
dark1 = get_data("2024-07-02_650umMNA_00000.h5", "001")
dark2 = get_data("2024-07-02_650umMNA_00000.h5", "002")

scale = (2 * 1e-3 / c) / 1

data = parrot.process.thz_and_two_darks(light,
                                        dark1,
                                        dark2,
                                        lowcut_signal=30,
                                        scale=scale,
                                        debug=True)

data = parrot.post_process_data.correct_systematic_errors(data)
data = parrot.post_process_data.cut_data(data, time_start=0e-12, time_stop=10e-12)
data = parrot.post_process_data.window(data)
data = parrot.post_process_data.pad_zeros(data)
# data = parrot.post_process_data.correct_gain_in_spectrum(data)

parrot.plot.simple_multi_cycle(data, water_absorption_lines=False, max_THz_frequency=22e12)
parrot.plot.extended_multi_cycle(data, water_absorption_lines=False, max_THz_frequency=22e12)
plt.show(block=True)
