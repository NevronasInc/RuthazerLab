from pynwb import NWBHDF5IO
import numpy as np

io = NWBHDF5IO(r'C:\NWB project\Ed\Post NR1 example\Post NR1 example\21715015b\21715015b.nwb', 'r')
nwbfile = io.read()


# Check which label is saved within the raw acquisition
print(nwbfile.acquisition)
voltageClampSeries = nwbfile.acquisition['voltage_clamp_response_sweep0']
data_response = voltageClampSeries.data[:]
time = np.arange(start=voltageClampSeries.starting_time, stop=data_response.shape[0]/voltageClampSeries.rate, step=1/voltageClampSeries.rate)

# Get the stimulation
print(nwbfile.stimulus)
voltageClampSeries = nwbfile.stimulus['voltage_clamp_stimulus_sweep0']
data_stimulus = voltageClampSeries.data[:]
time = np.arange(start=voltageClampSeries.starting_time, stop=data_stimulus.shape[0]/voltageClampSeries.rate, step=1/voltageClampSeries.rate)
