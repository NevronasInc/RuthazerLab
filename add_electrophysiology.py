from pynwb.icephys import VoltageClampStimulusSeries, VoltageClampSeries
import numpy as np
import pyabf
import glob
import os

# Konstantinos Nasiotis 2021

def add_to_nwb(nwbfile, abf, iSweep):

    # The device and electrode are added only once
    try:
        device = nwbfile.create_device(name='Acquisition: Axopatch 200B (Molecular Devices) - Digitization: Digidata 1220')
        # Add electrode
        electrode = nwbfile.create_icephys_electrode(
            name="elec0",
            description='glass pipette',
            device=device
        )
    except:
        device = nwbfile.get_device()
        electrode = nwbfile.get_ic_electrode()

    # Get the stimulation of the sweep
    abf.setSweep(sweepNumber=iSweep, channel=1)

    stimulus = VoltageClampStimulusSeries(
        name='voltage_clamp_stimulus_sweep' + str(iSweep),
        data=abf.sweepY,
        starting_time=abf.sweepTimesSec[iSweep],
        rate=np.float(abf.dataRate),
        electrode=electrode,
        gain=1.0,
        sweep_number=iSweep,
    )

    # Get the intracellular response
    abf.setSweep(sweepNumber=iSweep, channel=0)
    response = VoltageClampSeries(
        name='voltage_clamp_response_sweep' + str(iSweep),
        data=abf.sweepY,
        starting_time=abf.sweepTimesSec[iSweep],
        rate=np.float(abf.dataRate),
        electrode=electrode,
        gain=1.0,
        capacitance_slow=np.nan,
        resistance_comp_correction=np.nan,
        sweep_number=iSweep,
    )

    rowindex = nwbfile.add_icephys_repetition(sequential_recordings=[0], id=int(iSweep))
    nwbfile.add_intracellular_recording(
        electrode=electrode,
        stimulus=stimulus,
        response=response,
        id=int(iSweep)
    )

    return nwbfile


def add_ephys(nwbfile, folder_name):

    # Get the filename
    file_name = []
    for file in glob.glob(os.path.join(folder_name, "*.abf")):
        file_name.append(file)
    if len(file_name) > 1:
        print('More than one .abf files present in this folder. Selecting the first one')
    abf = pyabf.ABF(file_name[0])
    # abf.headerLaunch()

    for iSweep in range(abf.sweepCount):
        # Add the data to nwb
        nwbfile = add_to_nwb(nwbfile, abf, np.uint32(iSweep))

    print("[2] Added Voltage Clamp series")

    return nwbfile

