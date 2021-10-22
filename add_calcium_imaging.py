from pynwb.ophys import TwoPhotonSeries, OpticalChannel
import xml.etree.ElementTree as ET
from pynwb import NWBHDF5IO
import numpy as np
import psutil
import h5py
import os


def get_times_thorlabs(folder_name):
    f = h5py.File(os.path.join(folder_name, 'Episode001.h5'), 'r')

    frameOutLogical = np.zeros_like(f['DI']['Frame Out'][:])
    frameOutLogical[f['DI']['Frame Out'][:] > 0] = 1

    frameOutDiff = np.diff(frameOutLogical, axis=0)

    risingEdge = np.where(frameOutDiff == 1)[0]
    fallingEdge = np.where(frameOutDiff > 1000000)[0]  # TODO - THIS IS A HACK - FIX PRECISION ERROR
    length = fallingEdge - risingEdge
    maxLen = np.max(length)
    minLen = np.min(length)

    frameOutDiff = np.diff(f['DI']['Frame Out'][:], axis=0)
    if maxLen > 1.5 * minLen:
        threshold = minLen + (maxLen - minLen) / 2
        frameOutDiff[risingEdge(length > threshold)] = 0

    frameOutDiff = np.append(0, frameOutDiff)
    indices = np.where(frameOutDiff == 2)[0]

    # Thorlabs uses 20MHz clock
    time = f['Global']['GCtr'][:] / 20000000
    timestamps = time[indices]
    timestamps = timestamps.reshape((len(timestamps),))

    return timestamps

def get_experiment_parameters_thorlabs(folder_name):
    # Get related info from experiment.xml file
    tree = ET.parse(os.path.join(folder_name, 'experiment.xml'))
    xmlroot = tree.getroot()
    for elem in xmlroot:
        if 'nyquistExWavelengthNM' in elem.attrib.keys():
            excitation_lambda = float(elem.attrib['nyquistExWavelengthNM'])
            emission_lambda = float(elem.attrib['nyquistEmWavelengthNM'])
        if 'zStreamFrames' in elem.attrib.keys():
            nSlices = int(elem.attrib['steps'])
        if 'pixelX' in elem.attrib.keys():
            ImageWidth = int(elem.attrib['pixelX'])
            ImageHeight = int(elem.attrib['pixelY'])
            grid_spacing = float(elem.attrib['pixelSizeUM'])
            heightUM = float(elem.attrib['heightUM'])
            widthUM = float(elem.attrib['widthUM'])
            origin_coords = [float(elem.attrib['offsetX']), float(elem.attrib['offsetY']), 0.0]
        if 'flybackFrames' in elem.attrib.keys():
            nFlybackFrames = float(elem.attrib['flybackFrames'])  # This value refers to how many frames are
                                                                  # "lost" while the microscope returns to
                                                                  #  the position of the 1st slice

    return excitation_lambda, emission_lambda, nSlices, \
           ImageWidth, ImageHeight, grid_spacing, origin_coords, nFlybackFrames


def add_calcium_imaging_thorlabs(nwbfile, folder_name, save_raw_files_in_nwb):

    # nwbfile: identifier for the nwbfile
    # folder_name: folder that contains the calcium imaging dataset
    # save_raw_files_in_nwb: flag (true/false) to indicate if the raw data should be saved on the nwb file
    # processing_to_add: fluorescence/df_f0 , indicates which timeseries to save on the nwb file

    identifier = os.path.basename(folder_name)

    # Load Timestamps
    time_stamps = get_times_thorlabs(folder_name)
    fps = np.float(1/(time_stamps[1] - time_stamps[0]))

    # Load variables used during acquisition
    excitation_lambda, emission_lambda, nSlices, \
    ImageWidth, ImageHeight, \
    grid_spacing, origin_coords, nFlybackFrames = get_experiment_parameters_thorlabs(folder_name)

    # Create a device
    device = nwbfile.create_device(
        name="Microscope",
        description="Two-photon microscope",
        manufacturer="Thorlabs"
    )
    optical_channel = OpticalChannel(
        name="OpticalChannel",
        description="an optical channel",
        emission_lambda=emission_lambda
    )

    if save_raw_files_in_nwb:
        imaging_plane = nwbfile.create_imaging_plane(
            name="ImagingPlane",
            optical_channel=optical_channel,
            description="Cell nucleus imaging",
            device=device,
            excitation_lambda=excitation_lambda,
            indicator="GCAMP6s",
            location="cell nucleus",
            grid_spacing=[grid_spacing, grid_spacing],
            grid_spacing_unit="um",
            origin_coords=origin_coords,
            origin_coords_unit="um"
        )
    else:
        imaging_plane = nwbfile.create_imaging_plane(
            name="ImagingPlane",
            optical_channel=optical_channel,
            imaging_rate=fps,
            description="Cell nucleus imaging",
            device=device,
            excitation_lambda=excitation_lambda,
            indicator="GCAMP6s",
            location="cell nucleus",
            grid_spacing=[grid_spacing, grid_spacing],
            grid_spacing_unit="um",
            origin_coords=origin_coords,
            origin_coords_unit="um"
        )

    # Add binary file or just a link to it on the NWB file
    if save_raw_files_in_nwb:
        rawFileName = os.path.join(folder_name, 'Image_0001_0001.raw')

        # Get size of the file in pixels (take into account the 2 byte uint16 precision)
        file_size_in_pixels = int(os.path.getsize(rawFileName)/2)

        # Get the available ram - partially loading larger segments from a binary file improves performance
        total_time_stamps = 0

        total_frames = int(file_size_in_pixels / (ImageWidth * ImageHeight))


        # Append each slice sequentially to the NWB file - REALLY INEFFICIENT - READS THE RAW FILE nSLices TIMES
        # BUT HAVENT FOUND A WAY TO APPEND NEW CHUNKS TO EXISTING TIMESERIES


        ####for iSlice in range(nSlices):
        print('contact NWB team for appending more than 2 acquisition objects')  # TODO
        for iSlice in range(2):

            leftover_frames = total_frames

            print('Slice: ' + str(iSlice) + ' - Total frames: ' + str(leftover_frames))

            fseek_multiplier = 0
            i = 0
            while leftover_frames > 0:
                memory = psutil.virtual_memory()
                available_memory_in_bytes = memory.free
                #nFramesToLoad = int(
                #    np.floor(available_memory_in_bytes / (ImageWidth * ImageHeight * 2 * (nSlices + nFlybackFrames)))) * (
                #                            nSlices + nFlybackFrames) - 2000 * (nSlices + nFlybackFrames)

                nFramesToLoad = 1000 * (nSlices + nFlybackFrames)

                chunksize_in_pixels = ImageWidth * ImageHeight * nFramesToLoad

                segmented_data = []  # Initialize variable (It also empties it)

                with open(rawFileName, "rb") as f:
                    f.seek(((total_frames - leftover_frames) * ImageWidth * ImageHeight * 2) * fseek_multiplier)

                    if leftover_frames <= nFramesToLoad:
                        chunksize_in_pixels = leftover_frames * (ImageWidth * ImageHeight)
                        nFramesToLoad = leftover_frames
                        leftover_frames = nFramesToLoad

                    # Segmented data holds the info in this format: height x width x time x slices/planes
                    segmented_data = np.fromfile(f, count=chunksize_in_pixels, dtype='uint16').reshape(
                        (int(nFramesToLoad / (nSlices + nFlybackFrames)), (nSlices + nFlybackFrames), ImageWidth,
                         ImageHeight)).transpose(2, 3, 0, 1)  # The Matlab loader is using unsigned int16 little endian

                    # Keep just a single slice
                    if i == 0:
                        segmented_data_single_slice = []
                        segmented_data_single_slice = np.squeeze(segmented_data[:, :, :, iSlice])
                    else:
                        segmented_data_single_slice = np.append(segmented_data_single_slice,
                                                            np.squeeze(segmented_data[:, :, :, iSlice]), axis=2)
                    del segmented_data
                    total_time_stamps += int(nFramesToLoad / (nSlices + nFlybackFrames))

                    leftover_frames = leftover_frames - nFramesToLoad
                    print('[' + str(i) + ']' + ' nFramesToLoad: ' + str(nFramesToLoad) +
                          '\t\t\tLeftover: ' + str(leftover_frames))
                fseek_multiplier = 1
                i = i + 1

            # Add the data
            image_series = TwoPhotonSeries(
                name='TwoPhotonSeries_Slice' + str(iSlice),
                data=np.squeeze(segmented_data_single_slice),
                imaging_plane=imaging_plane,
                timestamps=time_stamps,
                unit='normalized amplitude'
            )

            if iSlice == 0:
                nwbfile.add_acquisition(image_series)
                with NWBHDF5IO(os.path.join(folder_name, identifier + '.nwb'), 'w') as io:
                    io.write(nwbfile)
            else:
                io = NWBHDF5IO(os.path.join(folder_name, identifier + '.nwb'), mode='a')
                nwbfile = io.read()
                nwbfile.add_acquisition(image_series)
                io.write(nwbfile)
                io.close()

    else:
        # If external data are used, store only the path to the raw file
        image_series = TwoPhotonSeries(
            name='TwoPhotonSeries',
            dimension=[ImageWidth, ImageHeight],
            external_file=['Image_0001_0001.raw'],
            imaging_plane=imaging_plane,
            starting_frame=[0],
            format='external',
            timestamps=time_stamps,
        )
        nwbfile.add_acquisition(image_series)

    print('[2] Added calcium imaging')
    return nwbfile
