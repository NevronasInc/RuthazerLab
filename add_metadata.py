from pynwb import NWBFile
from pynwb.file import Subject
import numpy as np
import pandas as pd
import datetime
import pathlib
import pyabf
import glob
import os

# Konstantinos Nasiotis 2021


def get_metadata_from_excel(identifier, excel_fname):
    xl_file = pd.ExcelFile(excel_fname)

    # Convert the excel sheet to a dataframe
    df_excel = {sheet_name: xl_file.parse(sheet_name) for sheet_name in xl_file.sheet_names}
    df_excel['Sheet1'] = df_excel['Sheet1'].replace(np.nan, '', regex=True)  # Get rid of nan values

    # Get the row of the excel sheet that correspond to that identifier
    i_row_from_excel = np.where(df_excel['Sheet1']['Identifier'].str.lower() == identifier.lower())[0]

    if len(i_row_from_excel) < 1:
        raise NameError('No identifier from the excel sheet corresponds to the folder you selected. \
                         Is the folder named correctly?')

    # Selected entry from excel that corresponds to the identifier of the dataset selected
    entry_from_excel = df_excel['Sheet1'].loc[i_row_from_excel]

    experimenter = entry_from_excel['Experimenter'].to_string(index=False)
    virus = entry_from_excel['Virus'].to_string(index=False)
    experiment_type = entry_from_excel['Experiment type'].to_string(index=False)  # Calcium Imaging, daily axon imaging, dynamic axon imaging, ephys
    species = entry_from_excel['Species'].to_string(index=False)
    subject_id = entry_from_excel['Subject_id'].to_string(index=False)
    sex = entry_from_excel['Sex'].to_string(index=False)
    age = entry_from_excel['Age'].to_string(index=False)
    subject_description = entry_from_excel['Subject Description'].to_string(index=False)
    experiment_description = entry_from_excel['Experiment Description'].to_string(index=False)
    general_notes = entry_from_excel['General Notes 1'].to_string(index=False) + ' | ' + \
                    entry_from_excel['General Notes 2'].to_string(index=False) + ' | ' + \
                    entry_from_excel['General Notes 3'].to_string(index=False)
    if general_notes == ' |  | ':
        general_notes = ''
    related_publications = entry_from_excel['Related Publications'].to_string(index=False)

    single_excel_entry = {'experimenter': experimenter,
                          'virus': virus,
                          'experiment_type': experiment_type,
                          'species': species,
                          'subject_id': subject_id,
                          'sex': sex,
                          'age': age,
                          'subject_description': subject_description,
                          'experiment_description': experiment_description,
                          'general_notes': general_notes,
                          'related_publications': related_publications
                          }

    return single_excel_entry


def add_to_nwb(single_excel_entry, start_time, identifier):
    subject = Subject(subject_id=single_excel_entry['subject_id'],
                      age=single_excel_entry['age'],
                      description=single_excel_entry['subject_description'],
                      species=single_excel_entry['species'],
                      sex=single_excel_entry['sex'])

    nwbfile = NWBFile(
            session_description=single_excel_entry['experiment_type'],
            session_start_time=start_time,
            experimenter=single_excel_entry['experimenter'],
            lab='Ruthazer Lab',
            institution='McGill University',
            experiment_description=single_excel_entry['experiment_description'],
            identifier=identifier,
            subject=subject,
            virus=single_excel_entry['virus'],
            related_publications=single_excel_entry['related_publications'],
            notes=single_excel_entry['general_notes']
    )

    print('[1] Added metadata')

    return nwbfile


def add_metadata(folder_name, excel_fname):
    # Get the identifier of the dataset to be used
    identifier = os.path.basename(folder_name)  # Grab the folder name
    single_excel_entry = get_metadata_from_excel(identifier, excel_fname)

    message = single_excel_entry['experiment_type'] + ' dataset collected by ' + single_excel_entry['experimenter']
    print(message)
    print('-' * len(message))

    if single_excel_entry['experiment_type'].lower() == 'calcium imaging':
        fname = pathlib.Path(os.path.join(folder_name, 'Image_0001_0001.raw'))
        start_time = datetime.datetime.fromtimestamp(fname.stat().st_mtime).astimezone()

    elif single_excel_entry['experiment_type'].lower() == 'ephys':
        file_name = []
        for file in glob.glob(os.path.join(folder_name, "*.abf")):
            file_name.append(file)

        if len(file_name) > 1:
            print('More than one .abf files present in this folder. Selecting the first one')

        abf = pyabf.ABF(file_name[0])
        start_time = abf.abfDateTime.astimezone()

    elif 'axon imaging' in single_excel_entry['experiment_type'].lower():
        tif_files = glob.glob(os.path.join(folder_name, identifier + ' for drawing', '*.tif'))
        fname = pathlib.Path(tif_files[0])
        start_time = datetime.datetime.fromtimestamp(fname.stat().st_mtime).astimezone()

    nwbfile = add_to_nwb(single_excel_entry, start_time, identifier)

    return nwbfile, single_excel_entry
