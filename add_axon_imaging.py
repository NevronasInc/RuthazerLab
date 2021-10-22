import glob
import os

def get_branches(folder_name):
    identifier = os.path.dirname(folder_name)
    tif_files = glob.glob(os.path.join(folder_name, identifier + ' for drawing', '*draw.tif'))


def get_raw_tif_files(folder_name):
    identifier = os.path.dirname(folder_name)
    tif_files = glob.glob(os.path.join(folder_name, identifier + ' for drawing', identifier + '*draw.tif'))


def add_branches_to_nwb(nwbfile, folder_name):
    print(1)


def add_raw_tif_files_to_nwb(nwbfile, folder_name):
    print(1)


def add_axon(nwbfile, folder_name, single_excel_entry):

    if single_excel_entry['experimenter'] == "Cynthia Solek":
        branches_xslx_files = get_branches(folder_name)
        tif_files = get_raw_tif_files(folder_name)

        for iFile in
        add_branches_to_nwb(nwbfile, folder_name)
        add_raw_tif_files_to_nwb(nwbfile, folder_name)

