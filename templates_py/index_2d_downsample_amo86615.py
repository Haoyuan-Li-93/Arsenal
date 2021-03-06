import sys
import os
import numpy as np
import h5py as h5
import time
import skimage.measure as sm
import psana

sys.path.append('/reg/neh/home5/haoyuan/Documents/my_repos/Arsenal')
import arsenal
from arsenal import PsanaUtil

"""
                Notice
                
This script is designed specially for the experiment amo86615.
Because the data files for this experiment are damaged, one 
can not retrieve the data from the index, instead, one has to 
resort to the event time.
 
"""

####################################################################################################
# [USER] Specify the parameters to use
####################################################################################################
# The experiment info
exp_line = 'amo'
exp_name = 'amo86615'
user_name = 'haoyuan'
process_stage = 'scratch'
run_num_list = [182, 183, 184, 185, 186, 188, 190, 191, 192, 193, 194, 196, 197]
det_name = 'pnccdFront'

# Downsample ratio
ds_ratio = 4

# Add a tag
tag = 'selection_based_on_psocake'

####################################################################################################
# [AUTO] Loop through all the runs
####################################################################################################
for run_num in run_num_list:

    # construct the output address
    output_address = '/reg/d/psdm/{}/{}/{}/{}/experiment_data/'.format(exp_line,
                                                                       exp_name,
                                                                       process_stage,
                                                                       user_name)

    # Check the address
    if not os.path.isdir(output_address):
        os.mkdir(output_address)
    print("The output address is {}".format(output_address))

    # Construct the output file name
    output_name = '{}_run_{}_{}.h5'.format(exp_name, run_num, tag)

    # Get event index
    index_to_process = arsenal.lcls.get_cxi_pattern_idx(exp_line=exp_line,
                                                        exp_name=exp_name,
                                                        user_name=user_name,
                                                        process_stage=process_stage,
                                                        run_num=run_num)

    eventtime_to_process = arsenal.lcls.get_cxi_pattern_eventtime(exp_line=exp_line,
                                                                  exp_name=exp_name,
                                                                  user_name=user_name,
                                                                  process_stage=process_stage,
                                                                  run_num=run_num)

    fiducial = arsenal.lcls.get_cxi_pattern_fiducial(exp_line=exp_line,
                                                     exp_name=exp_name,
                                                     user_name=user_name,
                                                     process_stage=process_stage,
                                                     run_num=run_num)

    ################################################################################################
    # [AUTO] Intialize the detector and get the downsampled pattern's shape
    ################################################################################################
    # Get data source
    det, run, times, evt, info_dict = PsanaUtil.setup_exp(exp_name=exp_name,
                                                          run_num=run_num,
                                                          det_name=det_name)

    # Get pattern number
    pattern_num = index_to_process.shape[0]

    # Get the downsampled shape
    ds_exmaple = sm.block_reduce(info_dict['Example 2D'], (ds_ratio, ds_ratio), np.sum)
    ds_shape = ds_exmaple.shape

    ################################################################################################
    # [AUTO] Load and downsample all the patterns
    ################################################################################################
    with h5.File(output_address + output_name, 'w') as h5file:
        # For different batches
        batch_counter = 0

        tic = time.time()

        # Construct the shape of the holder variable
        holder_shape = (pattern_num, ds_shape[0], ds_shape[1])
        holder = np.zeros(holder_shape)

        # Extract all the patterns from this sublist
        for idx in range(pattern_num):
            et = psana.EventTime(int(eventtime_to_process[idx]),
                                 fiducial[idx])
            evt = run.event(et)
            sample = det.photons(evt, adu_per_photon=130)

            sample_ds = sm.block_reduce(sample, (ds_ratio, ds_ratio), np.sum)

            holder[idx] = sample_ds

        # save_the down sampled pattern
        h5file.create_dataset('/batch_{}_index'.format(batch_counter), data=index_to_process)
        h5file.create_dataset('/batch_{}_pattern'.format(batch_counter), data=holder)

        # Update the batch_counter
        batch_counter += 1

        toc = time.time()
        print("It takes {:.2f} seconds to process {} patterns.".format(toc - tic, pattern_num))
