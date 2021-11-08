from metadata_gui import display_metadata_nwb
from pynwb import NWBHDF5IO

io = NWBHDF5IO(r'C:\NWB project\Ed\Jack\Jack.nwb', 'r')
nwbfile = io.read()

display_metadata_nwb(nwbfile)


