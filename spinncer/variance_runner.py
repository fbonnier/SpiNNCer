"""
Batch runner adapted from '
'https://github.com/pabogdan/neurogenesis/blob/master/synaptogenesis/batch_argparser.py'
'and '
'https://github.com/pabogdan/neurogenesis/blob/master/synaptogenesis/batch_runner.py
"""

import subprocess
import os
import numpy as np
import sys
import hashlib
import pylab as plt
from spinncer.batch_argparser import *
import shutil
import spinncer as x

base_path = os.path.dirname(x.__file__)

currrent_time = plt.datetime.datetime.now()
string_time = currrent_time.strftime("%H%M%S_%d%m%Y")

if args.suffix:
    suffix = args.suffix
else:
    suffix = hashlib.md5(string_time.encode('utf-8')).hexdigest()

# Some constants
NO_CPUS = args.no_cpus
MAX_CONCURRENT_PROCESSES = args.max_processes or 10

POISSON_PHASE = 0
PERIODIC_PHASE = 1
PHASES_NAMES = ["poisson", "periodic"]
PHASES_ARGS = [None, "--periodic_stimulus"]
# Both phases
# PHASES = [POISSON_PHASE, PERIODIC_PHASE]


PHASES = [POISSON_PHASE]  # Only Poisson phase
# PHASES = [PERIODIC_PHASE]  # Only PERIODIC phase

concurrently_active_processes = 0

no_runs = np.arange(5)
# Compute total number of runs
total_runs = no_runs.size * len(PHASES)

parameters_of_interest = {
    'n_run': no_runs,
    'phase': PHASES,
}

dataset = "scaffold_full_dcn_400.0x400.0_v3.hdf5"

log_calls = []

# making a directory for this experiment
# dir_name = "variance_testing_POISSON_stim_3_@{}".format(suffix)
dir_name = "variance_testing_{}_@{}".format(PHASES_NAMES[PHASES[0]], suffix)
# dir_name = "variance_testing_PERIODIC_@{}".format(suffix)
# dir_name = "variance_testing_3_loop_PERIODIC_@{}".format(suffix)
print("=" * 80)
print("TOTAL RUNS", total_runs)
if not os.path.isdir(dir_name):
    print("MKDIR", dir_name)
    os.mkdir(dir_name)
else:
    print("FOLDER ALREADY EXISTS. RE-RUNNING INCOMPLETE JOBS.")
print("CHDIR", dir_name)
os.chdir(dir_name)
print("GETCWD", os.getcwd())
print("-" * 80)

loops = [3, 4, 5, 7, 9]

params = {}

for phase in PHASES:
    for n_run in no_runs:
        curr_params = {'n_run': n_run,
                       'phase': phase}
        filename = "spinn_400x400" \
                   "_run_{}" \
                   "_{}" \
                   "_@{}".format(n_run,
                                 PHASES_NAMES[phase],
                                 suffix)

        params[filename] = curr_params


        concurrently_active_processes += 1
        null = open(os.devnull, 'w')
        print("Run ", concurrently_active_processes, "...")

        call = [sys.executable,
                os.path.join(base_path, 'cerebellum_experiment.py'),
                '--input', dataset,
                '-o', filename,
                # '--f_peak', str(150),
                # '--stim_radius', str(140),
                # '--f_peak', str(200),
                # '--stim_radius', str(130),
                # '--spike_seed', str(31415926),
                # '--id_seed', str(31415926),
                '-s', os.path.join(base_path, "400x400_stimulus_3.npz"),
                '--r_mem',
                '--loops_grc', str(loops[n_run]), # str(10),
                '--id_remap', 'grid'
                ]

        if PHASES_ARGS[phase] is not None:
            call.append(PHASES_ARGS[phase])

        # if args.additional_params is not None:
        #     print("Additional parameters passed through to individual simulations:", args.additional_params)
        #     for element in args.additional_params:
        #         split_ap = element.split(" ")
        #         for token in split_ap:
        #             call.append(token)
        print("CALL", call)
        log_calls.append((call, filename, curr_params))

        # making a directory for this individual experiment
        prev_run = True
        if os.path.isdir(filename) and os.path.isfile(
                os.path.join(filename, "structured_provenance.csv")):
            print("Skipping", filename)
            continue
        elif not os.path.isdir(filename):
            os.mkdir(filename)
            prev_run = False
        os.chdir(filename)
        print("GETCWD", os.getcwd())
        shutil.copyfile("../../spynnaker.cfg", "spynnaker.cfg")
        if (concurrently_active_processes % MAX_CONCURRENT_PROCESSES == 0
                or concurrently_active_processes == total_runs):
            # Blocking
            with open("results.out", "wb") as out, open("results.err", "wb") as err:
                subprocess.call(call, stdout=out, stderr=err)
            print("{} sims done".format(concurrently_active_processes))
        else:
            # Non-blocking
            with open("results.out", "wb") as out, open("results.err", "wb") as err:
                subprocess.Popen(call, stdout=out, stderr=err)
        os.chdir("..")
        print("=" * 80)
print("All done!")

end_time = plt.datetime.datetime.now()
total_time = end_time - currrent_time
np.savez_compressed("batch_{}".format(suffix),
                    parameters_of_interest=parameters_of_interest,
                    total_time=total_time,
                    log_calls=log_calls)

sys.stdout.flush()

analysis_call = [
    sys.executable,
    os.path.join(base_path, 'provenance_analysis.py'),
    '-i', "../" + dir_name,
    '--group_on', 'n_run',

]
with open("prov_analysis.out", "wb") as out, open("prov_analysis.err", "wb") as err:
    subprocess.call(analysis_call, stdout=out, stderr=err)


