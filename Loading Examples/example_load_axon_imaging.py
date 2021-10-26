from pynwb import NWBHDF5IO

io = NWBHDF5IO(r'C:\NWB project\Ed\2018-05-28\Claudia\Claudia.nwb', 'r')
nwbfile = io.read()

# Load averaged files / Files saved after a day or a timepoint - They are an Imagesegmentation interface
print(nwbfile.processing)
reference_image = nwbfile.processing['branch-ophys']['ImageSegmentation']['PlaneSegmentation'].reference_images[0]
data = reference_image.data

# Load branches length
print(nwbfile.processing)

branches_interface = nwbfile.processing['Claudia cell1 Total branches analysis']['Branch Growth']
data = branches_interface.data[:]  # 8x104 matrix = nTimePoints x nBranches
