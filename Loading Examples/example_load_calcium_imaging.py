from pynwb import NWBHDF5IO

io = NWBHDF5IO(r'C:\Users\knasi\Consulting\NWB project\Ed\Jack\Jack.nwb', 'r')
nwbfile = io.read()


# Accessing raw data (if they are saved on the NWB file)
print(nwbfile.acquisition)
photonSeries = nwbfile.acquisition['TwoPhotonSeries']

# Accessing processed data
print(nwbfile.processing)
data_interfaces = nwbfile.processing['ophys0']
fluorescence = data_interfaces['Fluorescence']
roi_response_series = fluorescence.roi_response_series
roi_response_series_slice0 = roi_response_series['RoiResponseSeries_slice0']

data_ref = roi_response_series_slice0.data  # This is just a reference to the data - it is not loaded yet
data = data_ref[:]  # Now it is an ndarray


