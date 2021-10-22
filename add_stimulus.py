from pynwb.misc import AnnotationSeries
from pynwb.misc import TimeSeries
import pandas as pd
import numpy as np
import scipy
import os


def load_templates_optophysiology(stimuli_mat_file):
    # This function loads a mat file containing a structure with ALL the possible stimuli templates
    # The group of stimuli is identified by the "Code" field
    # For now there are only stimuli templates for Codes 3 and 4 (brightness and spatial frequency stimulation)
    # Use the matlab script within optophysiology_stimulus_templates folder to assign the rest

    templates = scipy.io.loadmat(stimuli_mat_file)
    stimuli_structure = templates['stimuli_structure']
    #Codes = templates['Code'][0]
    #Descriptions = templates['Description'][0]
    #stimulus_IDs = templates['stimulusID'][0]
    #stimulus_Matrices = templates['stimulusMatrix'][0]

    return stimuli_structure


def used_templates(folder_name):
    # This function checks the file "StimulusConfig.txt" to get which stimulusIDs were used during stimulation.
    # Then it retrieves the timing of each stimulus presentation from "StimulusTimes.txt"

    # Load All templates
    stimuli_structure = stimuli_structure = load_templates_optophysiology(
        os.path.join('optophysiology_stimuli_templates', 'optophysiology_stimulus_templates.mat'))

    # Load file that contains the a collection of stimulus parameters. This is used to create a "comments" string
    df_stimulus_codenames = pd.read_csv(os.path.join(folder_name, 'StimulusConfig.txt'), sep=',', header=None)

    # Log contrast value
    if df_stimulus_codenames[5][0] == 1:
        contrast_comment = 'maximum contrast'
    elif df_stimulus_codenames[5][0] == 0:
        contrast_comment = 'no contrast'
    else:
        contrast_comment = 'a contrast value of ' + str(df_stimulus_codenames[5][0]) + ', ' \
                           'where 1 is maximum contrast and 0 is no contrast'

    # Log sign of stimulus relative to background (-1 is a stimulus darker than background, 1 is brighter)
    if df_stimulus_codenames[0][1] == 1:
        contrast_sign_comment = 'brighter'
    elif df_stimulus_codenames[0][1] == -1:
        contrast_sign_comment = 'darker'

    # Finally collect the variables that are needed to be stored within the NWB File
    comments = 'Each stimulus was presented ' + str(int(df_stimulus_codenames[1][0])) + ' times. ' \
               'Each stimulation lasted ' + str(df_stimulus_codenames[3][0]) + ' seconds. ' \
               'The interstimulus period lasted ' + str(df_stimulus_codenames[4][0]) + ' seconds. ' \
               'The stimulus was presented at ' + contrast_comment + '. ' \
               'The stimulus was ' + contrast_sign_comment + ' than the background. ' \
               'The screen was ' + str(int(df_stimulus_codenames[1][1])) + 'x' + str(int(df_stimulus_codenames[2][1])) \
               + ' pixels. ' \
               'The display area was a square of ' + str(int(df_stimulus_codenames[4][1])) + ' pixels side with a ' + \
               str(int(df_stimulus_codenames[3][1])) + ' pixels y_offset from the bottom of the screen. ' \
               'The background intensity value was set at ' + str(df_stimulus_codenames[5][1]) + \
               ' (continuous from 0 (black) to 1 (white).'

    # Load file that contains the info for the presentations [index, time, stimulus type]
    df_stimulus_presentations = pd.read_csv(os.path.join(folder_name, 'StimulusTimes.txt'), sep=',', header=None)
    timestamps = np.array(df_stimulus_presentations[1])
    stimulusIDs = np.array(df_stimulus_presentations[2])

    selected_code = []
    for code in range(11):  # 11 Total experimental stimulation designs
        if np.array_equal(np.unique(stimulusIDs), np.unique(stimuli_structure[0][code][2])):  # This checks if the stimulusIDs used in the experiment match the templates
            selected_code = code
            stimulusDescription = stimuli_structure[0][code][1]
            template_stimuli = stimuli_structure[0][code][3]  # Matrix with templates e.g.: 480x800x11
            break

    if not selected_code:
        stimulusDescription = []
        template_stimuli = stimulusIDs

    return stimulusDescription, template_stimuli, timestamps, comments


def add_to_nwb(nwbfile, stimulusDescription, template_stimuli, timestamps, comments):

    if template_stimuli != []:
        stimuli_series = TimeSeries(
            name='stimuliTemplates',
            data=template_stimuli,
            timestamps=timestamps,
            comments=comments,
            unit='',
            description=str(stimulusDescription)
        )
        nwbfile.add_stimulus_template(stimuli_series)
        print('[4] Added stimulus templates')

    else:
        stimuli_series = AnnotationSeries(
            name='stimuliSeries',
            data=template_stimuli,
            timestamps=timestamps,
            comments=comments,
            description=str(stimulusDescription)
        )
        nwbfile.add_stimulus(stimuli_series)
        print('[4] Added stimulus times and codes')

    return nwbfile


def add_stimulus_optophysiology(nwbfile, folder_name, single_excel_entry):

    if single_excel_entry['experimenter'] == "Cynthia Solek":
        # Get stimulation info - Either the templates, or the codes used
        stimulusDescription, template_stimuli, timestamps, comments = used_templates(folder_name)
        # Add to NWB file
        nwbfile = add_to_nwb(nwbfile, stimulusDescription, template_stimuli, timestamps, comments)

    return nwbfile
