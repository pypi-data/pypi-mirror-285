# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 15:53:42 2024

@author: Howel Larreur
"""
# classes
from .fisp import Ion, Layer, Material, Reaction, BinaryReaction

# simulation parameters
from .fisp import set_energy_bins, set_simulation, input_spectrum, reset

# data extraction
from .fisp import RANGE_TABLES as range_tables
from .fisp import REACTIONS_LIST as reactions_list
from .fisp import extract_created_ions, extract_energy_deposition, extract_nuclear_reations, extract_stopped_ions
from .fisp import FRONT_SPECTRA as front_spectra
from .fisp import REAR_SPECTRA as rear_spectra

# plotting functions
from .fisp import plot_energy_deposition, plot_nuclear_reactions, plot_range, plot_stopped_ions, plot_stopping_power,\
                 plot_target

# printing functions
from .fisp import print_created_ions

# saving functions
from .fisp import save_energy_deposition, save_created_ions, save_nuclear_reactions, save_range, save_stopped_ions,\
                  save_stopping_power

# running functions
from .fisp import run
from .pfisp import prun
