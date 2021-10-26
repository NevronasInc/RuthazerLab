from pynwb.ophys import ImageSegmentation, TwoPhotonSeries, OpticalChannel
from pynwb.misc import TimeSeries
from PIL import Image
import pandas as pd
import numpy as np
import glob
import os

# Konstantinos Nasiotis 2021


def get_raw_tif_files(folder_name):
    identifier = os.path.basename(folder_name)
    tif_files = glob.glob(os.path.join(folder_name, identifier + ' for drawing', identifier + '*draw.tif'))

    return tif_files


def add_raw_tif_files_to_nwb(nwbfile, tif_file):
    try:
        ophys_module = nwbfile.create_processing_module(
            name='branch-ophys',
            description='optical physiology processed data that show branch growth'
        )

        # Create a device
        device = nwbfile.create_device(
            name="Microscope",
            description="Two-photon microscope",
            manufacturer="Thorlabs"
        )
        optical_channel = OpticalChannel(
            name="OpticalChannel",
            description="an optical channel",
            emission_lambda=523.0
        )

        img_seg = ImageSegmentation()
        ophys_module.add(img_seg)

        imaging_plane = nwbfile.create_imaging_plane(
            name="ImagingPlane",
            optical_channel=optical_channel,
            imaging_rate=30.0331,
            description="Cell nucleus imaging",
            device=device,
            excitation_lambda=910.0,
            indicator="GCAMP6s",
            location="cell nucleus",
            grid_spacing=[0.4050, 0.4050],
            grid_spacing_unit="um",
            origin_coords=[0.0, 0.0, 0.0],
            origin_coords_unit="um"
        )
    except:
        img_seg = ImageSegmentation()
        imaging_plane = nwbfile.get_imaging_plane()

    im = Image.open(os.path.join(tif_file))
    tif_data = np.array(im)
    tif_data.resize(int(tif_data.shape[0]), int(tif_data.shape[1]), 1)  # The input needs to be 3D

    reference_image_series = TwoPhotonSeries(
        name=os.path.basename(tif_file),
        data=tif_data,
        imaging_plane=imaging_plane,
        timestamps=np.array([0], dtype=np.float64),
        unit='',
        comments='Single TIF file that shows the neuronal branches growth. Compare with TIF files from other times/days'
    )

    ps = img_seg.create_plane_segmentation(
        name='PlaneSegmentation',
        description='Output segmentation',
        imaging_plane=imaging_plane,
        reference_images=reference_image_series
    )

    return nwbfile


def get_branches_files(folder_name):
    identifier = os.path.basename(folder_name)
    branches_files1 = glob.glob(os.path.join(folder_name, identifier + ' for drawing', '*.csv'))
    branches_files2 = glob.glob(os.path.join(folder_name, identifier + ' for drawing', identifier + '*.xlsx'))

    branches_files = branches_files1 + branches_files2

    branches_dataframes = []
    labels = []
    for file_name in branches_files:
        if ".csv" in file_name:
            # This is hardcoded - assuming that all .csv file entries start at the same row
            matrix = pd.read_csv(file_name, header=None, on_bad_lines='warn', skiprows=[0, 1, 2, 3, 4, 5, 6, 7])
            column_names = ['Branch ' + str(i+1) for i in range(matrix.shape[1])]
            row_names = ['Time ' + str(i+1) for i in range(matrix.shape[0])]
            matrix.columns = column_names
            matrix.index = row_names

            branches_dataframes.append(matrix)
            labels.append(os.path.basename(os.path.splitext(file_name)[0]))

        elif ".xlsx" in file_name:
            xl_file = pd.ExcelFile(file_name)

            # Convert the excel sheet to a dataframe -# This is hardcoded - assuming that all .csv file entries start at the same row
            matrix = xl_file.parse(xl_file.sheet_names[0]).to_numpy()[13:, :-2].astype(float)
            column_names = ['Branch ' + str(i + 1) for i in range(matrix.shape[1])]
            row_names = ['Time ' + str(i + 1) for i in range(matrix.shape[0])]
            matrix = pd.DataFrame(data=matrix, columns=column_names, index=row_names)

            branches_dataframes.append(matrix)
            labels.append(os.path.basename(os.path.splitext(file_name)[0]))

    return branches_dataframes, labels


def add_branches_to_nwb(nwbfile, branches_matrix, label):

    branches_module = nwbfile.create_processing_module(
        name=label,
        description='neuronal branches length'
    )

    branch_growth = TimeSeries(name='Branch Growth', data=branches_matrix.to_numpy(), unit='um',
                               timestamps=np.float64(list(range(branches_matrix.shape[0]))),
                               comments=str(branches_matrix.shape[1]) + ' neuronal branches were monitored for ' + \
                                        str(branches_matrix.shape[0]) + ' timepoints',
                               description='no description'
                               )

    branches_module.add(branch_growth)

    return nwbfile


def add_axon_datasets(nwbfile, folder_name, single_excel_entry):

    if single_excel_entry['experimenter'] == "Cynthia Solek":
        tif_files = get_raw_tif_files(folder_name)
        branches_dataframes, labels = get_branches_files(folder_name)

        # A more correct approach here would be to add all tif files to the same timeseries and assign the timestamps
        # with values that reflect the intervals. However there is no standardized interval that the tif files are saved
        # (some are days, some are time 1, time 2 etc.)
        for tif_file_name in tif_files:
            nwbfile = add_raw_tif_files_to_nwb(nwbfile, tif_file_name)

        # Add the branch metrics from the excel/
        for i in range(len(branches_dataframes)):
            nwbfile = add_branches_to_nwb(nwbfile, branches_dataframes[i], labels[i])

    return nwbfile

