from add_calcium_imaging import add_calcium_imaging_thorlabs
from add_stimulus import add_stimulus_optophysiology
from add_electrophysiology import add_ephys
from add_processedROI import add_processedROI
from add_metadata import add_metadata
from add_axon_imaging import add_axon
from pynwb import NWBHDF5IO
import os

#folder_name = r"C:\Users\knasi\Consulting\NWB project\Ed\Jack"
#folder_name = r"C:\Users\knasi\Consulting\NWB project\Ed\Marion\2014_05_13a"

#folder_name = r"C:\Users\knasi\Consulting\NWB project\Ed\Vanessa\Calcium data\Exp_1727\Exp_1727"
#folder_name = r"C:\Users\knasi\Consulting\NWB project\Ed\Post NR1 example\Post NR1 example\21715015b"
folder_name = r"C:\Users\knasi\Consulting\NWB project\Ed\2018-11-16\Fish AF"
excel_fname = r"C:\Users\knasi\Consulting\NWB project\Ed\Ruthazer lab datasets.xlsx"


# 1. Initiate nwb_file and add metadata
nwbfile, single_excel_entry = add_metadata(folder_name, excel_fname)

# Display NWB metadata
#display_nwb() # TODO


if single_excel_entry['experiment_type'] == 'calcium imaging':

    # 2. Add Calcium imaging
    save_raw_files_in_nwb = False
    nwbfile = add_calcium_imaging_thorlabs(nwbfile, folder_name, save_raw_files_in_nwb)

    # 3. Add timeseries of the ROIs
    nwbfile = add_processedROI(nwbfile, folder_name, save_raw_files_in_nwb, single_excel_entry)

    # 4. Add stimuli presentation events
    nwbfile = add_stimulus_optophysiology(nwbfile, folder_name, single_excel_entry)


elif single_excel_entry['experiment_type'] == 'ephys':

    # 2. Add Electrophysiology recording
    nwbfile = add_ephys(nwbfile, folder_name)


elif single_excel_entry['experiment_type'] == 'dynamic axon imaging':
    nwbfile = add_axon(nwbfile, folder_name, single_excel_entry)

# *. Close the file
identifier = os.path.basename(folder_name)  # Grab the folder name

with NWBHDF5IO(os.path.join(folder_name, identifier+'.nwb'), 'w') as io:
    io.write(nwbfile)
    print('[*] Saved ' + identifier + '.nwb file')

