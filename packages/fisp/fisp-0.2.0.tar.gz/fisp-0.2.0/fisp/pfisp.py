# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 20:01:02 2024

@author: Howel Larreur
"""

import inspect
import multiprocessing as mp
import os
import subprocess
import sys
import tqdm
from shutil import rmtree

def prun(values, model_namelist, output_directory=None, workers='auto', ignore_overwrite=False):
    """
    Runs parametric studies over several python processes distributed accross multiple CPU cores.

    Note: returns None.

    Parameters
    ----------
    values : iterable
        Values of the parametric study. These will replace the flag $parametric$ in the namelist.
    model_namelist : str
        Path to the namelist.
    output_directory : str, optional
        Output directory to keep things organised. The default is None.
    workers : int, optional
        Maximum number of processes spawned by multiprocessing.Pool. The default is 'auto', which determines it
        via os.cpu_count()//2-1. For all values of 'workers', the number of processes is capped by the number
        of values in the parametric study.
    ignore_overwrite : bool, optional
        Erase existing files if there are any. The default is False.

    Raises
    ------
    FileExistsError
        Existing simulations were not overwritten or erased, but the parametric study was aborted.

    """
    run = True
    stack = inspect.stack()
    for frameinfo in stack:
        if 'multiprocessing' in frameinfo.filename:
            run = False
            break
    if run:
        print("FISP by Howel Larreur. Prototype version.\n")
        # number of CPUs to use
        workers = min(os.cpu_count()//2-1, len(values)) if workers == 'auto' else min(workers, len(values))
        # output directory
        if output_directory is None:
            path = os.getcwd() + os.sep
        else:
            try:
                os.mkdir(output_directory)
            except FileExistsError: pass
            path = output_directory + os.sep
        # printing info
        print("Reading from namelist at " + os.path.abspath(model_namelist))
        print("Output directory: " + os.path.abspath(path) + '\n')
        # read model namelist
        with open(model_namelist, 'r') as model_file:
            list_model = model_file.readlines()
        # create new namelists and folders
        to_run = []
        for value in values:
            folder = path + str(value) + os.sep
            try:
                os.mkdir(folder)
            except FileExistsError:
                if ignore_overwrite:
                    rmtree(folder)
                    os.mkdir(folder)
                else:
                    raise FileExistsError('Trying to overwrite an existing simulation. Aborting parametric study.')
            to_run.append(folder+model_namelist+str(value))
            with open(to_run[-1], 'w') as namelist_to_run:
                for line in list_model:
                    namelist_to_run.write(line.replace('$parametric$', str(value)))
        # execute
        with tqdm.tqdm(total=len(values), desc=f'Running on {workers} CPUs', position=0) as pbar:
            def update(namelist):
                pbar.update(1)
            with mp.Pool(workers) as pool:
                out_async_objects = [pool.apply_async(_pexec, (filename,), callback=update) for filename in to_run]
                [oao.wait() for oao in out_async_objects]

def _pexec(namelist):
    directory = os.path.dirname(namelist) + os.sep
    out = subprocess.run([sys.executable, namelist], capture_output=True, text=True)
    with open(directory+'log.txt', 'w') as logfile:
        logfile.write(out.stdout)
        if len(out.stderr) > 0:
            logfile.write("ERRORS AND WARNINGS\n")
            logfile.write(out.stderr)
    return namelist
