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

os.chdir(r"Z:\Nextcloud\labdata\projects\HiFi_THz_Source_Vol2\measurments\ZI_Boxcar\2024-07-11")


def get_data(file_name):
    with h5py.File(file_name, "r") as f:
        trace_ids = list(f.keys())
        # Read-in first trace
        trace_id = trace_ids[0]
        # Read out device name, e.g. dev2179
        dev = list(f[f"{trace_id}"].keys())
        # Take first element from list (there should only be one device)
        dev = dev[0]
        data = {}
        for trace_id in trace_ids:
            # Connect to path
            path = f"{trace_id}/{dev}/"
            timebase = f[path + "boxcars/0/sample/"].attrs["timebase"]
            time = f[path + "boxcars/0/sample/timestamp"][:]
            position = f[path + "demods/0/sample.auxin0/value"][:]
            signal = f[path + "boxcars/0/sample/value"][:]
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
            # Get name from ZI interface
            name = str(f[path + "boxcars/0/sample/chunkheader"]["name"][0])[2:-1]
            data[name] = {"time": time, "position": position, "signal": signal}
        return data


raw_data = get_data("2024-07-11_improvedBPD_00000.h5")
print(raw_data.keys())
angles = [254, 210]#np.arange(240,265,5)
output_data = {}
scale = (2 * 1e-3 / c) / 1
for angle in angles:
    filter_dict = {k: v for k, v in raw_data.items() if k.startswith(str(angle))}
    light = [v for k, v in filter_dict.items() if "THz" in k][0]
    dark1 = [v for k, v in filter_dict.items() if "dark1" in k][0]
    dark2 = [v for k, v in filter_dict.items() if "dark2" in k][0]
    data = parrot.process.thz_and_two_darks(light,
                                            dark1,
                                            dark2,
                                            lowcut_signal=10,
                                            scale=scale,
                                            debug=True)
    data = parrot.post_process_data.correct_systematic_errors(data)
    data = parrot.post_process_data.cut_data(data, time_start=0e-12, time_stop=10e-12)
    data = parrot.post_process_data.window(data)
    data = parrot.post_process_data.pad_zeros(data)
    data = parrot.post_process_data.correct_gain_in_spectrum(data)
    parrot.plot.simple_multi_cycle(data, water_absorption_lines=False, max_THz_frequency=10e12)
    #parrot.plot.extended_multi_cycle(data, water_absorption_lines=False, max_THz_frequency=10e12)
    plt.show(block=True)
    output_data[angle] = data

fig, ax = plt.subplots()
for angle in angles:
    data = output_data[angle]
    color = next(ax._get_lines.prop_cycler)['color']
    ax.plot(data["dark"]["frequency"], 10*np.log10(np.abs(data["dark"]["average"]["frequency_domain"])**2), color="black", alpha=0.6)
    ax.plot(data["light"]["frequency"],  10*np.log10(np.abs(data["light"]["average"]["frequency_domain"])**2), color=color, label=angle)
ax.grid(True)
ax.xaxis.set_major_formatter(EngFormatter("Hz"))
ax.set_xlabel("Frequency")
ax.set_ylabel("Power spectrum (dB)")
ax.set_xlim(right=12e12)
ax.legend(title="Angle (°)")
plt.show(block=True)
