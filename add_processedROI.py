from pynwb.ophys import ImageSegmentation, Fluorescence, RoiResponseSeries, DfOverF, TwoPhotonSeries
from add_calcium_imaging import get_times_thorlabs, get_experiment_parameters_thorlabs
import scipy.io
import h5py
import numpy as np
import os

# Konstantinos Nasiotis 2021


def add_to_nwb(nwbfile, folder_name, processing_to_add, save_raw_files_in_nwb):
    identifier = os.path.basename(folder_name)  # Grab the folder name

    # Load Timestamps
    time_stamps = get_times_thorlabs(folder_name)

    # Read analyzed data
    filepath = os.path.join(folder_name, identifier + ' brightness.mat')
    f_hdf5 = h5py.File(filepath)

    # Load variables used during acquisition
    excitation_lambda, emission_lambda, nSlices, \
    ImageWidth, ImageHeight, \
    grid_spacing, origin_coords, nFlybackFrames = get_experiment_parameters_thorlabs(folder_name)

    # Load already analyzed ROI info from Matlab files
    analysedFileName = os.path.join(folder_name, 'Analysed ' + identifier + ' brightness.mat')
    f_analysed = scipy.io.loadmat(analysedFileName)
    all_roi_coords = np.stack([f_analysed['AnalysedData'][0][0]['RoiCoords'][0],
                               f_analysed['AnalysedData'][0][0]['RoiCoords'][1],
                               f_analysed['AnalysedData'][0][0]['RoiCoords'][2]], axis=1)

    for iSlice in range(nSlices):
        ophys_module = nwbfile.create_processing_module(
            name='ophys' + str(iSlice),
            description='optical physiology processed data'
        )

        img_seg = ImageSegmentation()
        ophys_module.add(img_seg)

        if save_raw_files_in_nwb:
            imaging_plane = nwbfile.acquisition['TwoPhotonSeries'+str(iSlice)].imaging_plane
        else:
            imaging_plane = nwbfile.acquisition['TwoPhotonSeries'].imaging_plane

        # Get the average twophoton series to use as a reference_images
        averaged_data = []
        averaged_data = f_hdf5[f_hdf5['ImageData']['Average'][iSlice].item()][:]
        averaged_data.resize(int(averaged_data.shape[0]), int(averaged_data.shape[1]), 1)

        '''
        # If the reference image needs to be derived from the averaged tif file
        from PIL import Image
        im = Image.open(os.path.join(folder_name, 'Slice' + str(iSlice+1) + '.tif'))
        averaged_data2 = []
        averaged_data2 = np.array(im)
        averaged_data2.resize(int(averaged_data2.shape[0]), int(averaged_data2.shape[1]), 1)

        import matplotlib.pyplot as plt
        
        THE TWO ARE NOT THE SAME - THIS WOULD AFFECT THE ROI COORDINATES - STAY WITH  THE ANALYZED .MAT
        plt.imshow(averaged_data)
        plt.show()
        plt.imshow(averaged_data2)
        plt.show()
        '''

        reference_image_series = TwoPhotonSeries(
            name='Averaged_TwoPhotonSeries_Slice' + str(iSlice),
            data=averaged_data,
            imaging_plane=imaging_plane,
            timestamps=np.array([0], dtype=np.float64),
            unit=''
        )

        ps = img_seg.create_plane_segmentation(
            name='PlaneSegmentation' + str(iSlice),
            description='Output segmentation from Slice ' + str(),
            imaging_plane=imaging_plane,
            reference_images=reference_image_series  # optional
        )

        # Add ROI info from a single slice
        ROIcoords = all_roi_coords[all_roi_coords[:, 2] == iSlice+1, :]

        idx = np.zeros((np.shape(ROIcoords)[0], 1), dtype=np.int16)
        idy = np.zeros((np.shape(ROIcoords)[0], 1), dtype=np.int16)

        for iROI in range(np.shape(ROIcoords)[0]):

            # TRY THIS - TODO
            idx[iROI] = np.round(ROIcoords[iROI, 0])
            idy[iROI] = np.round(ROIcoords[iROI, 1])

            pixel_mask = []
            surrounding_center_pixel_mask = 0
            if surrounding_center_pixel_mask == 0:
                pixel_mask.append((idx[iROI][0].astype(int), idy[iROI][0].astype(int), 1))  # x,y,weight
            else:
                for ix in range(idx[iROI][0], idx[iROI][0] + surrounding_center_pixel_mask):
                    for iy in range(idy[iROI][0], idy[iROI][0] + surrounding_center_pixel_mask):
                        pixel_mask.append((ix, iy, 1))  # x,y,weight

            # add pixel mask to plane segmentation
            ps.add_roi(pixel_mask=pixel_mask)

        # Now add the fluorecense/dfoverf0 data
        rt_region = ps.create_roi_table_region(
            region=list(range(np.shape(ROIcoords)[0])),
            description='All ' + str(np.shape(ROIcoords)[0]) + ' ROIs in slice ' + str(iSlice)
        )

        if processing_to_add == 'fluorescence':
            # Load fluorescence data
            fluorescence_data = f_hdf5[f_hdf5['ImageData']['Results'][iSlice].item()][:].T

            roi_resp_series = RoiResponseSeries(
                name='RoiResponseSeries_slice' + str(iSlice),
                data=fluorescence_data,
                rois=rt_region,
                unit='lumens',
                timestamps=time_stamps
            )
            # Add to the nwb file
            fl = Fluorescence(roi_response_series=roi_resp_series)
            ophys_module.add(fl)

        elif processing_to_add == 'df_f0':
            # Load df/f0 data
            all_df_f0_data = f_analysed['AnalysedData'][0][0]['dFF0']
            df_f0_data = all_df_f0_data[all_roi_coords[:, 2]==iSlice+1, :]

            roi_resp_series = RoiResponseSeries(
                name='RoiDfOverFSeries_slice' + str(iSlice),
                data=df_f0_data,
                rois=rt_region,
                unit='lumens',
                timestamps=time_stamps
            )
            # Add everything to the nwb file
            fl = DfOverF(roi_response_series=roi_resp_series)
            ophys_module.add(fl)


        # Now add the average responses to the stimuli
        averaged_roi_data = f_analysed['AnalysedData']['Responses'][0][0][all_roi_coords[:, 2] == iSlice + 1, :]

        image_series = RoiResponseSeries(
            name='AverageROI_Responses_to_Stimuli_Slice' + str(iSlice),
            data=averaged_roi_data,
            rois=rt_region,
            timestamps=np.arange(np.shape(averaged_roi_data)[1], dtype=np.float64),
            unit=''
        )
        fl = DfOverF(roi_response_series=roi_resp_series)


    print('[3] Added ' + processing_to_add + ' to processedROI')
    return nwbfile


def add_processedROI(nwbfile, folder_name, save_raw_files_in_nwb, single_excel_entry):

    processing_to_add = 'fluorescence'  # fluorescence / df_f0

    if single_excel_entry['experimenter'] == "Cynthia Solek":
        nwbfile = add_to_nwb(nwbfile, folder_name, processing_to_add, save_raw_files_in_nwb)

    return nwbfile