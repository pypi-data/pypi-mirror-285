# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 13:45:04 2023

@author: Howel Larreur
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import os
import inspect
import scipy.constants as cst
import time
from tqdm import tqdm
import warnings

# CODE TIMING DIAGNOSTIC FUNCTIONS

def timer(func):
    """
    Decorate a function with the present one to measure the time spent within the function.
    """
    def inner(*args, **kwargs):
        if not func in PERF_TIMINGS:
            PERF_TIMINGS[func] = 0.
        t_ini = time.perf_counter()
        r = func(*args, **kwargs)
        PERF_TIMINGS[func] += time.perf_counter() - t_ini
        return r
    return inner

def timer_show(tot_time=None):
    """
    Use this function to display results from timer function.
    """
    print('')
    total = sum(PERF_TIMINGS.values()) if tot_time is None else tot_time
    max_name_lenght = max([len(k.__name__) for k in PERF_TIMINGS.keys()])
    print("TOTAL TIME:".rjust(max_name_lenght), round(total, 3), '1.')
    for func, time_spent in PERF_TIMINGS.items():
        print(func.__name__.ljust(max_name_lenght), round(time_spent, 3), round(time_spent/total, 3))
    print('')

# GLOBAL VARIABLES

BETHE_CURVE_CACHE = {}
CALCULATE_ENERGY_DEPOSIT = True
CALCULATE_PARTICLES_STOPPING = True
ENERGY_BINS_DISTRIBUTION = np.linspace
ENERGY_BINS_NUMBER = 10000
ENERGY_BINS_RESIZE_TRIGGER = 100
FRONT_SPECTRA = {}
INITIAL_SPECTRUMS_LIST = []
LAYERS_LIST = []
MATERIALS_LIST = []
PERF_TIMINGS = {}
PROPAGATING_IONS_SPECIES_LIST = []
RANGE_TABLES = {}
RANGE_TABLES_MAX_ENERGY = 30.
REACTIONS_LIST = []
REAR_SPECTRA = {}
SLICES_LIST = []
SLICES_BACK_POSITIONS = []
SLICES_FRONT_POSITIONS = []

# CLASSES & FUNCTIONS

class Ion:
    def __init__(self, Z, A, mass, I=None, ionization_energy=0, name=None):
        check(A >= Z, "Number of mass < atomic number")
        self.Z = Z
        self.A = A
        self.mass = mass
        self.I = I
        self.star = ionization_energy
        self.name = f"{Z=}_{A=}" if name is None else name

    def __eq__(self, ion):
        if isinstance(ion, Ion):
            if self.__dict__ == ion.__dict__:
                return True
        return False

    def __hash__(self):
        return hash(tuple([v for v in self.__dict__.values()]))

class Layer:
    def __init__(self, material, thickness, reactions, outer_step_size=1e-8, max_step_size=1e-5, step_factor=1.01):
        """
        Declare a new layer of material in your simulation.

        Parameters
        ----------
        material : fisp.Material
            The material object, containing the properties of the material.
        thickness : scalar
            Thickness of the layer in meters.
        reactions : iterable of fisp.Reaction
            The nuclear reactions to be included in this layer.
        outer_step_size : scalar, optional
            Size of a slice at the edge of the layer. This is also the smallest size possible for any slice in
            this layer. The default is 10 nm.
        max_step_size : scalar, optional
            Maximum size allowed for an individual slice within this layer. The default is 10 um.
        step_factor : scalar, optional
            The ratio of two neighboring slices' size. The default is 1.01.

        Returns
        -------
        None.

        """
        check(isinstance(material, Material), "Layer's material must be instance of the Material class.")
        [check(isinstance(reaction, Reaction), "Layer's reactions must be instances of the Reaction class.")
         for reaction in reactions]
        [check(reaction.target in material.composition, f"No target {reaction.target.name} for given reaction in layer.")
         for reaction in reactions]
        check(0. < outer_step_size <= max_step_size, "Step sizes should be 0. < outer_step_size <= inner_step_size")
        check(step_factor >= 1., "Step factor should be >= 1.")
        check(not(step_factor == 1. and max_step_size != outer_step_size), "Can't make variable step size with unity step factor.")
        LAYERS_LIST.append(self)
        if not material in MATERIALS_LIST:
            MATERIALS_LIST.append(material)
        self.material = material
        for reaction in reactions:
            PROPAGATING_IONS_SPECIES_LIST.extend([ion for ion in reaction.types if ion not in PROPAGATING_IONS_SPECIES_LIST])
        self.thickness = thickness
        self.reactions = reactions
        for r in reactions:
            if not r in REACTIONS_LIST:
                REACTIONS_LIST.append(r)
        self.step_min = outer_step_size
        self.step_max = max_step_size
        self.step_factor = step_factor

class FakeLayer(Layer):
    def __init__(self, material):
        self.material = material

class Material:
    def __init__(self, composition, density, molar_mass, mean_excitation_potential=None, name=None, disable_warnings=False):
        """
        Declare a new type of material.

        Note: this does not introduce the material in the simulation. fisp.Layer must be used.

        Parameters
        ----------
        composition : dict: {fisp.Ion:scalar}
            The atoms composing the material and their stochyometric proportions within it.
        density : scalar
            The density of the material in kg/m^3.
        molar_mass : scalar
            The molar mass of the material in kg/mol.
        mean_excitation_potential : scalar, optional
            Mean excitation potential of the electrons in the material in MeV, to be used in Bethe's formula.
            The default value is the stochyometric average of mean excitation potential value for each atom in
            the material.
        name : str, optional
            The name given to the material for prints and plots. The default is a python pointer.

        Returns
        -------
        None.

        """
        [check(isinstance(ion, Ion), "Material must be composed from ions of the ions catalog") for ion in composition]
        check(abs(sum(composition.values()) - 1.) < 1e-9, "Material components fractions don't add up to 1.")
        self.composition = composition
        self.rho = density
        self.I = mean_excitation_potential if mean_excitation_potential is not None else sum([ion.I*fraction for ion, fraction in composition.items()])
        self.N = molar_mass
        self.Z = sum([ion.Z*fraction for ion, fraction in composition.items()])
        self.A = sum([ion.A*fraction for ion, fraction in composition.items()])
        self.name = f'{self=}'.split('=', 1)[1] if name is None else name
        if not disable_warnings:
            if density < 50.:
                warnings.warn(f'The density input for the Material {self.name} seems very low. Please check that the density used is expressed in kg/m^3.')
            if molar_mass > .9:
                warnings.warn(f'The molar mass input for the Material {self.name} seems very high. Please check that the molar mass used is expressed in kg/mol.')
            if self.I > 1e3:
                warnings.warn(f'The mean excitation potential input for the Material {self.name} seems very high. Please check that the mean excitation potential used is expressed in MeV.')

class Reaction:
    def __init__(self, input_ion, target_atom, output_ions, cross_section_object, cross_section_type='curve', name=None):
        """
        Declare a new type of nuclear reaction.

        For binary reaction - i.e. that can be expressed as target(projectile,ejectile)product, the BinaryReaction
        fisp class is a convenient tool.

        Note: this does not introduce the reaction in the simulation. fisp.Layer must be used.

        Parameters
        ----------
        input_ion : Ion
            Projectile ion, part of a propagating spectrum.
        target_atom : Ion
            Target ion, part of a layer of material.
        output_ions : iterable of iterable, each sub-iterable being (fisp.Ion, scalar, func)
            The output ions (ejectile and products) types, numbers and speeds are passed here, expected in the
            following format:             [(Ion1, number_of_ions, output_speed, ...]
            where Ion1 is an Ion created by the present reaction, number_of_ions is the number of copies of Ion1
            (with the same speed and direction) created, on average, for each occurence of the present reaction,
            and output_speed is a function of the projectiles' energies. It must accept an array as an argument
            and return an array the same shape containing the corresponding output ion speeds in c unit.
        cross_section_object : two iterables or a function
            The cross-section curve for projectile ion energies in the laboratory frame.
            If given as data points (curve): expected as one iterable for energies (in MeV) and another for corresponding
            cross-section values (in m²).
            If given as a function: expected to take an array of ion energies in the lab frame and to return an
            array of the same size containing corresponding cross-section values in m².
        cross_section_type : str, optional
            'curve' or 'function'. Refer to cross_section_object for more informations. The default is 'curve'.
        name : str, optional
            The name given to the reaction for prints and plots. The default is a list of name of each input and
            output ions, separated by |.

        Returns
        -------
        None.

        """
        check(isinstance(input_ion, Ion), "Input ion must be instance of the Ion class.")
        check(isinstance(target_atom, Ion), "Target atom must be instance of the Ion class.")
        [check(isinstance(ion[0], Ion), "Output ions must be instances of the Ion class.") for ion in output_ions]
        check(cross_section_type in ('curve', 'function'), "Cross section data type must be either curve or function.")
        self.input = input_ion
        self.target = target_atom
        self.output = output_ions
        self.cross_section_type = cross_section_type
        self.cross_section_object = cross_section_object
        self.types = [input_ion] + [ion for ion, _, _ in output_ions]
        self.name = name if name is not None else f'{input_ion.name} + {target_atom.name} -> ' + ' + '.join([oi[0].name for oi in output_ions])
        for ion, _, _ in output_ions:
            if not ion in self.types:
                self.types.append(ion)

    def cross_sections(self, energies):
        """
        Returns the cross-section for the reaction corresponding to the energy of the projectile in the lab frame.

        Parameters
        ----------
        energies : array-like
            Input energy.ies of the projectile in the lab frame.

        Returns
        -------
        array-like, same shape as input energies
            Cross-section in m² corresponding to input energies.

        """
        if self.cross_section_type == 'curve':
            return np.interp(energies, *self.cross_section_object, left=0., right=0.)
        # if self.cross_section_type == 'function':
        return self.cross_section_object(energies)

    def plot_cross_section(self, ax=None, unit='m2', **kwargs):
        """
        Plots the cross-section of the current reaction in the lab frame.

        Parameters
        ----------
        ax : matplotlib.pyplot.Axes, optional
            Axis to plot on. The default is the curretn axis obtained via plt.gca()
        unit : str, optional
            Either 'm2' of 'barn'. This is the Y axis unit of the plot. The default is 'm2'.
        **kwargs :
            Keyword arguments passed to matplotlib.pyplot.plot function.

        Returns
        -------
        matplotlib.pyplot.Axes
            The Axes the spectrum was plotted on.

        """
        if self.cross_section_type == 'curve':
            ax = plt.gca() if ax is None else ax
            ax.set_xlabel('Ion energy (lab frame) [MeV]')
            ax.set_ylabel('Cross-section ['+unit+']')
            ax.set_xscale('log')
            ax.set_yscale('log')
            energy, xsec = self.cross_section_object
            if unit == 'barn':
                xsec *= 1e28
            else:
                if unit != 'm2':
                    raise Exception('Cross-section plot unit not supported: '+unit)
            return ax.plot(energy, xsec, **kwargs)
        else:
            raise Exception('Work in progress')

class BinaryReaction(Reaction):
    def __init__(self, target, projectile, ejectile, product, cross_section_object, cross_section_type='curve', name=None):
        """
        Declare a new type of reaction, if the reaction is a binary reaction, i.e. one target, one projectile,
        one ejectile, one product. This is more convenient to use than the parent fisp.Reaction class for such
        reactions.

        Note: this does not introduce the reaction in the simulation. fisp.Layer must be used.

        Parameters
        ----------
        target : Ion
            Target ion, part of a layer of material.
        projectile : Ion
            Projectile ion, part of a propagating spectrum.
        ejectile : Ion
            Ejectile ion, produced by the reaction.
        product : Ion
            Product ion, produced by the reaction.
        cross_section_object : two iterables or a function
            The cross-section curve for projectile ion energies in the laboratory frame.
            If given as data points (curve): expected as one iterable for energies (in MeV) and another for corresponding
            cross-section values (in m²).
            If given as a function: expected to take an array of ion energies in the lab frame and to return an
            array of the same size containing corresponding cross-section values in m².
        cross_section_type : TYPE, optional
            'curve' or 'function'. Refer to cross_section_object for more informations. The default is 'curve'.
        name : str, optional
            The name given to the reaction for prints and plots. The default is a list of name of each input and
            output ions, separated by |.

        """
        check(isinstance(target, Ion), "Target must be instance of the Ion class.")
        check(isinstance(projectile, Ion), "Projectile must be instance of the Ion class.")
        check(isinstance(ejectile, Ion), "Ejectile must be instance of the Ion class.")
        check(isinstance(product, Ion), "Product must be instance of the Ion class.")
        self.input = projectile
        self.target = target
        self.cross_section_type = cross_section_type
        self.cross_section_object = cross_section_object
        self.types = [projectile, ejectile, product]
        self.name = name if name is not None else f'{target.name} ({projectile.name}, {ejectile.name}) {product.name}'
        if ejectile not in self.types:
            self.types.append(ejectile)
        if projectile not in self.types:
            self.types.append(projectile)
        REACTIONS_LIST.append(self)
        # ejectile + product energies calculation
        # Notation: pe = projectile energy
        Q = target.mass + projectile.mass - product.mass - ejectile.mass
        def com_speed(pe_lab):
            return projectile.mass/(projectile.mass+target.mass)*np.sqrt(2*pe_lab/projectile.mass)
        def energy_product_com(pe_lab):
            pe_com = pe_lab * (target.mass/(target.mass+projectile.mass))**2
            target_energy_com = pe_lab * (target.mass*projectile.mass/(target.mass+projectile.mass)**2)
            return (pe_com + target_energy_com + Q - product.star)*(ejectile.mass/(ejectile.mass+product.mass))
        def ejectile_forward(pe_lab):
            return com_speed(pe_lab) + np.sqrt(2*energy_product_com(pe_lab)*product.mass/ejectile.mass**2)
        def ejectile_backward(pe_lab):
            return com_speed(pe_lab) - np.sqrt(2*energy_product_com(pe_lab)*product.mass/ejectile.mass**2)
        def product_forward(pe_lab):
            return com_speed(pe_lab) + np.sqrt(2*energy_product_com(pe_lab)/product.mass)
        def product_backward(pe_lab):
            return com_speed(pe_lab) - np.sqrt(2*energy_product_com(pe_lab)/product.mass)
        self.output = [(ejectile, .5, ejectile_forward), (ejectile, .5, ejectile_backward),
                       (product, .5, product_forward), (product, .5, product_backward)]

class Spectrum:
    def __init__(self, ions_type, direction, ions_energy, ions_population):
        check(isinstance(ions_type, Ion), "Ion type of the spectrum must be an instance of the Ion class.")
        check(direction in ("front", "back"), "Spectrum shoud propagate either to the front or the back of the target.")
        check(len(ions_energy) == len(ions_population), "Ion spectrum energy and populations axis must be the same shape")
        check(bool(np.all(ions_energy > 0.)), "All energies in a Spectrum must be strictly positive")
        self.type = ions_type
        self.direction = direction
        self.energies = ions_energy
        self.populations = ions_population
        self.direction_switch = 2 * int(direction == 'back') - 1. # =1 if direction is back, =-1 if direction is front

    def add(self, spectrum):
        """
        This function should add a spectrum, given as an argument, to the current one.

        Note: The resulting spectrum is not sorted.
        """
        check(self.type == spectrum.type, "Both spectrae must be the same particle type to be added.")
        check(self.direction == spectrum.direction, "Both spectrae must propagate in the same direction")
        self.energies = np.concatenate((self.energies, spectrum.energies))
        self.populations = np.concatenate((self.populations, spectrum.populations))

    def do_reactions(self, slice_):
        """
        This function, given this step's input particles spectrums, and for every reaction in a reaction list:
        - 1/ calculates how many reactions occur with cross section data
        - 2/ calculates generated particles' energies using formulas in a reaction list
        - 3/ saves a front and back spectrum for each type of particles created; saves stopped particles.
        - 4/ removes the particles that reacted from the spectrum
        - 5/ removes spectrum bins with negative population
        """
        material = slice_.layer.material
        new_particles = False
        for reaction in [reaction for reaction in slice_.layer.reactions if self.type == reaction.input]:
            # Step 1
            cross_section = reaction.cross_sections(self.energies)
            atomic_spatial_density = cst.N_A * material.rho / material.N * material.composition[reaction.target]
            numbers_of_reactions = cross_section * atomic_spatial_density * slice_.thickness * self.populations
            slice_.reactions_numbers[reaction] = np.sum(numbers_of_reactions)
            # Step 2
            for ion, number_of_ions, speed_func in reaction.output:
                speeds = speed_func(self.energies) * self.direction_switch
                check(bool(np.all(speeds[np.nonzero(~np.isnan(speeds))] <= 1)), "Speed > c. Speeds must be expressed in c unit.")
                energies = speed_to_energy(ion, speeds)
                # Step 3
                front_indexes = np.nonzero(speeds < 0.)
                back_indexes  = np.nonzero(speeds > 0.)
                zero_indexes = np.nonzero(speeds == 0.)
                front_spectrum = Spectrum(ion, 'front', energies[front_indexes], number_of_ions*numbers_of_reactions[front_indexes])
                slice_.front_spectrums['front'][ion].add(front_spectrum)
                back_spectrum = Spectrum(ion, 'back', energies[back_indexes], number_of_ions*numbers_of_reactions[back_indexes])
                slice_.back_spectrums['back'][ion].add(back_spectrum)
                slice_.stopped[ion] += np.sum(number_of_ions*numbers_of_reactions[zero_indexes])
                # Tells the code if new propagating particles were created in the other direction
                if self.direction == 'back' and new_particles is False:
                    new_particles = len(front_indexes) != 0
                if self.direction == 'front' and new_particles is False:
                    new_particles = len(back_indexes) != 0
            # Step 4
            self.populations -= numbers_of_reactions
            # Step 5
            index_negatives = np.nonzero(self.populations <= 0.) # Index of bins with populations <= 0
            self.energies = np.delete(self.energies, index_negatives)
            self.populations = np.delete(self.populations, index_negatives)
        return new_particles

    def do_slowing(self, slice_):
        """
        Decreasing energies via stopping power and removing stopped particles.
        """
        if not CALCULATE_ENERGY_DEPOSIT and not CALCULATE_PARTICLES_STOPPING and not self.type in [r.input for r in slice_.layer.reactions]:
        # If user does not request saving energy deposit and particle stopping, the code can be optimised by erasing
        # particles whose range is too short to escape the current layer (these particles will not appear in output
        # spectrae anyway. This should be done only for particles that won't react or disintegrate.
            ranges = np.interp(self.energies,
                               RANGE_TABLES[slice_.layer.material][self.type]['energy'],
                               RANGE_TABLES[slice_.layer.material][self.type]['range'],
                               right=np.inf)
            # finding the index of the highest energy bin that will not exit the layer
            distance = slice_.distance_to_back if self.direction == 'back' else slice_.distance_to_front
            if ranges[-1] < distance:
            # managing the case when even the highest energies ions do not exit the layer
                self.energies = np.empty(0)
                self.populations = np.empty(0)
                return
            no_exit_index = np.searchsorted(ranges - distance, 0., 'right')
            # removing particle that can't exit the layer
            self.energies = self.energies[no_exit_index:]
            self.populations = self.populations[no_exit_index:]
        # Decreasing energy
        energy_difference = energy_loss(self, slice_)
        self.energies -= energy_difference
        if CALCULATE_ENERGY_DEPOSIT:
            # Calculating and saving energy deposit into current slice
            energy_deposit = energy_difference * self.populations
            slice_.energy_deposit += np.sum(energy_deposit)
        # Finding particles with <= 0 energy (= finding index of lowest positive energy bin)
        zero_index = np.searchsorted(self.energies, 0., 'right')
        # Saving them in slice's stopped particles data
        if CALCULATE_PARTICLES_STOPPING:
            slice_.stopped[self.type] += np.sum(self.populations[:zero_index])
        # Removing them from spectrum
        self.energies = self.energies[zero_index:]
        self.populations = self.populations[zero_index:]

    def erase(self):
        """
        Erases the current spectrum.
        """
        self.energies = np.empty(0)
        self.populations = np.empty(0)

    def histogram(self, bins=400):
        """
        Histogram values for the current spectrum.

        Parameters
        ----------
        bins : int, optional
            Number of bins of the histogram. The default is 400.

        Returns
        -------
        bins_centers : numpy.Array
            Energy value for each bin.
        populations_per_MeV : numpy.Array
            Population per MeV value for each bin.

        """
        if self.energies.size > 0:
            energy_borders = borders(self.energies)
            bins_borders = np.linspace(energy_borders[0], energy_borders[-1], bins+1)
            bins_centers = .5 * (bins_borders[:-1] + bins_borders[1:])
            bin_sizes = np.diff(bins_borders)
            bins_populations = []
            for i, (l, r) in enumerate(zip(bins_borders[:-1], bins_borders[1:])):
                bins_populations.append(self.integrate(l, r))
            populations_per_MeV = bins_populations / bin_sizes
        else:
            bins_centers = np.empty(0)
            populations_per_MeV = np.empty(0)
        return bins_centers, populations_per_MeV

    def integrate(self, lowcut=0, highcut=np.inf):
        """
        Integrates the current spectrum from lowcut to highcut.

        Parameters
        ----------
        lowcut : scalar, optional
            Lower bound of the integral. The default is 0.
        highcut : scalar, optional
            Upper bound of the integral. The default is np.inf.

        Returns
        -------
        float
            Value of the integral.

        """
        check(0 <= lowcut <= highcut, "Integral borders should be 0 <= lowcut <= highcut")
        # Doing easy cases
        if self.energies.size == 0:
            return 0.
        if (lowcut < self.energies[0]) and (highcut > self.energies[-1]): # Integration over full spectrum
            return np.sum(self.populations)
        if lowcut == highcut:
            return 0.
        # Doing non-trivial cases
        integral = 0.
        bins_borders = borders(self.energies)
        left = np.searchsorted(bins_borders, lowcut, 'right') - 1
        right = min(np.searchsorted(bins_borders, highcut, 'left'), len(bins_borders)-1)
        # Managing when the integration interval is within one bin
        if right - left == 1:
            covering = (highcut - lowcut) / (bins_borders[right] - bins_borders[left])
            return covering * self.populations[left]
        # Managing when lowcut lands in between two bins
        if lowcut > bins_borders[left]:
            covering = (bins_borders[left+1] - lowcut) / (bins_borders[left+1] - bins_borders[left])
            integral += covering * self.populations[left]
            left += 1
        # Managing when highcut lands in between two bins
        if highcut < bins_borders[right]:
            covering = (highcut - bins_borders[right-1]) / (bins_borders[right] - bins_borders[right-1])
            integral += covering * self.populations[right-1]
            right -= 1
        integral += np.sum(self.populations[left:right])
        return integral

    def push(self, slice_):
        """
        Saving results in the other side of the slice
        """
        if self.direction == 'back':
            spectrum_other_side = slice_.back_spectrums['back'][self.type]
        elif self.direction == 'front':
            spectrum_other_side = slice_.front_spectrums['front'][self.type]
        spectrum_other_side.add(Spectrum(self.type, self.direction, self.energies, self.populations))

    def plot(self, bins=400, ax=None, **kwargs):
        """
        Plots the current spectrum.

        Parameters
        ----------
        bins : int, optional
            Number of bins for the histogram. The default is 400.
        ax : matplotlib.pyplot.Axes, optional
            Axis to plot on. The default is the curretn axis obtained via plt.gca()
        **kwargs :
            Keyword arguments passed to matplotlib.pyplot.plot function.

        Returns
        -------
        matplotlib.pyplot.Axes
            The Axes the spectrum was plotted on.

        """
        ax = plt.gca() if ax is None else ax
        if kwargs.get('label') is None:
            kwargs['label'] = self.type.name
        ax.set_xlabel('Ion energy [MeV]')
        ax.set_ylabel('Ion population [/MeV]')
        bins_centers, populations_per_MeV = self.histogram(bins)
        return ax.plot(bins_centers, populations_per_MeV, **kwargs)

    def resize(self):
        """
        This functions resizes the (energy axis of the) spectrum in order for it to keep its original shape. Any former
        bin's population number landing between two new energy bins is divided between these two bins.
        """
        # Bins border values for current grid
        former_borders = borders(self.energies)
        # Bin sizes for current grid
        former_sizes = np.diff(former_borders)
        # Creating new energy grid
        new_energies = ENERGY_BINS_DISTRIBUTION(self.energies[0], self.energies[-1], ENERGY_BINS_NUMBER)
        # Finding borders for new grid
        new_borders = borders(new_energies, left=former_borders[0])
        # Creating population array
        new_populations = np.zeros(ENERGY_BINS_NUMBER)
        # For each bin of the former energy grid, finding which new bins its population belongs to (with proportions)
        # First, determining new borders between which this calculation is useful for each former bin.
        left = np.searchsorted(new_borders, former_borders[:-1], 'right') - 1
        right = np.searchsorted(new_borders, former_borders[1:], 'left')
        for i, population in enumerate(self.populations): # For each old bin...
            # Calculate fraction of covering of the old bin by the new bins.
            for left_index in range(left[i], right[i]): # For each new bin...
                # case where the old bin is included in new bin: covering = 100%, directly distribute populations
                if new_borders[left_index] <= former_borders[i] and new_borders[left_index+1] >= former_borders[i+1]:
                    new_populations[left_index] += population
                else: # covering = intersection of the old and new bin / width of old bin
                    intersection = min(former_borders[i+1], new_borders[left_index+1]) - max(former_borders[i], new_borders[left_index])
                    covering = intersection / former_sizes[i]
                    # Distribute new population
                    new_populations[left_index] += population * covering
        # Saving results
        self.energies = new_energies
        self.populations = new_populations

    def save(self, name, bins=400):
        """
        Saves the current spectrum as a .csv file containing histogram data in this format:
            bin_center_energy [MeV], population [/MeV]

        Parameters
        ----------
        name : str
            Name of the file. The extension '.csv' is added if it is not already present.
        bins : int, optional
            Number of bins for the histogram. The default is 400.

        """
        directory = os.path.dirname(inspect.stack()[1].filename) + os.sep
        basename = name+'.csv' if name[-4:] != '.csv' else name
        name = directory + basename
        bin_center_energy, population_per_MeV = self.histogram(bins)
        try:
            with open(name, 'x') as file:
                file.write('bin_center_energy [MeV], population [/MeV]\n')
                for e, p in zip(bin_center_energy, population_per_MeV):
                    file.write(f'{e}, {p}\n')
        except FileExistsError:
            if ask_overwrite(name):
                self.save_csv(basename, bins)

    def sort(self):
        """
        Sorts the current spectrum in energy.

        """
        indexes = np.argsort(self.energies)
        self.energies = self.energies[indexes]
        self.populations = self.populations[indexes]

class Slice:
    def __init__(self, layer, thickness):
        self.layer = layer
        self.thickness = thickness
        try: # position of previous slice
            self.front_position = SLICES_LIST[-1].back_position
        except IndexError: # if no previous slice, it's first slice
            self.front_position = 0.
        self.distance_to_back = layer.stop - self.front_position
        self.back_position = self.front_position + self.thickness
        self.distance_to_front = self.back_position - layer.start
        self.front_spectrums = {direction:{ion:Spectrum(ion, direction, np.empty(0), np.empty(0))
                                     for ion in PROPAGATING_IONS_SPECIES_LIST}
                          for direction in ("front", "back")}
        self.stopped = {ion:0. for ion in PROPAGATING_IONS_SPECIES_LIST}
        self.reactions_numbers = {}
        self.energy_deposit = 0.
        self.index = len(SLICES_LIST)
        SLICES_LIST.append(self)

class FakeSlice(Slice):
    def __init__(self, thickness, material):
        self.thickness = thickness
        self.layer = FakeLayer(material)

def ask_overwrite(filename):
    """
    Asks the user whether to overwrite existing file or not. If the users says yes, erases the file. Else, raise
    FileExistError.

    Parameters
    ----------
    filename : str
        The name of the file in question

    Raises
    ------
    FileExistsError
        The user refused to overwrite.

    Returns
    -------
    bool
        Returns True if user accepted to overwrite.

    """
    answer = input(filename + ' already exists. Overwrite existing file? (y/n) ')
    if answer == 'y':
        os.remove(filename)
        return True
    if answer == 'n':
        raise FileExistsError(f'File {filename} already exists.')
    print("Please answer y or n.")
    return ask_overwrite(filename)

def bethe_CSDA(spectrum, material):
    """
    Returns the energy loss in MeV/m corresponding to each energy in the input spectrum.
    Takes into account particle and material nature. Requires sorted energy spectrum.
    Uses a precalculated table as cache to greatly speed up the calculation.
    """
    # Check if cache exists and is large enought
    try:
        calculate_cache = BETHE_CURVE_CACHE[material][spectrum.type]['energies'][-1] < spectrum.energies[-1]
        # equals True if the cache is not covering high enought energies
    except KeyError: # No spectrum yet for this material
        calculate_cache = True
        if material in BETHE_CURVE_CACHE:
            BETHE_CURVE_CACHE[material][spectrum.type] = {}
        else:
            BETHE_CURVE_CACHE[material] = {spectrum.type:{}}
    if calculate_cache: # cache does not exist or is not high-energy enought, create cache
        # cache calculation parameters
        energy_multiplier = .505 # starts at .505 because first iteration of the loop multiplies this by 2, and we need slightly > 1.
        density_multiplier = 10
        peak_not_reached = True
        # factors that will not change with the energy spectrum, thus that we can precalculate only once
        m_e = cst.physical_constants['electron mass energy equivalent in MeV'][0]
        electron_density = cst.N_A * material.Z * material.rho / material.A / cst.physical_constants['molar mass constant'][0]
        prefactor = 4*np.pi/(m_e*1.602e-13)*electron_density*spectrum.type.Z**2*(cst.e**2/4/np.pi/cst.epsilon_0)**2/1.602e-13
        while peak_not_reached:
            energy_multiplier *= 2.
            energies = np.geomspace(1e-2, max(1e-2, energy_multiplier*spectrum.energies[-1]), density_multiplier*ENERGY_BINS_NUMBER)
            beta_sq = 1. - (energies / spectrum.type.mass + 1.)**(-2)
            loss_from_Bethe = prefactor / beta_sq * (np.log(2*m_e/material.I*beta_sq/(1.-beta_sq))-beta_sq)
            # Bethe formula is not good at low energy (routhly at ion energies under the maximum of the stopping power peak).
            # Thus, for ion energies under the stopping power peak, we set the energy loss equal to the stopping power peak's
            # (this is equivalent to a Constant Slowing Down Approximation, aka CSDA).
            index_peak = np.argmax(loss_from_Bethe)
            # Making sure that the peak has been reached. Otherwise increase max energy of the spectrum and try again.
            if index_peak != loss_from_Bethe.size - 1: # peak at last value == not reached
                peak_not_reached = False
        # CSDA
        loss_from_Bethe[:index_peak] = loss_from_Bethe[index_peak]
        BETHE_CURVE_CACHE[material][spectrum.type]['energies'] = energies
        BETHE_CURVE_CACHE[material][spectrum.type]['stop_power'] = loss_from_Bethe
    # At this point, cache exists and can be used for our spectrum
    return np.interp(spectrum.energies,
                     BETHE_CURVE_CACHE[material][spectrum.type]['energies'],
                     BETHE_CURVE_CACHE[material][spectrum.type]['stop_power'])

def borders(energies, left=None):
    """
    From center values of bins, returns the border values of theses bins.

    Parameters
    ----------
    energies : numpy Array
        Center values of the bins.
    left : scalar, optional
        First value of the bins' borders. The default is max(0, 2*energies[0] - energies[1]).

    Returns
    -------
    r : numpy array
        The energy bins' borders.

    """
    left = max(0, 2*energies[0] - energies[1]) if left is None else left
    r = np.insert(np.empty_like(energies), 0, left)
    r[1:-1] = .5 * (energies[1:] + energies[:-1])
    r[-1] = energies[-1]
    return r

def check(condition, error_text):
    """
    Checks if a condition is True. It not, raises the error text.

    Parameters
    ----------
    condition : bool
        The condition.
    error_text : str
        The error text.

    """
    if condition is False:
        raise Exception(error_text)

def create_range_tables():
    """
    Creates range tables to be use for simulation optimization.
    """
    with tqdm(total=len(MATERIALS_LIST)*len(PROPAGATING_IONS_SPECIES_LIST), disable=None) as pbar:
        for material in MATERIALS_LIST:
            dx = min([slice_.thickness for slice_ in SLICES_LIST if slice_.layer.material == material])
            RANGE_TABLES[material] = {}
            for ion in PROPAGATING_IONS_SPECIES_LIST:
                pbar.update(1)
                RANGE_TABLES[material][ion] = {'energy':[], 'range':[]}
                if ion.Z == 0: # neutron
                    RANGE_TABLES[material][ion]['energy'] = np.array([0.])
                    RANGE_TABLES[material][ion]['range'] = np.array([np.inf])
                    continue
                x = 0.
                fake_spectrum = Spectrum(ion, 'back', np.array([RANGE_TABLES_MAX_ENERGY]), np.empty(1))
                while fake_spectrum.energies[0] > 0.:
                    RANGE_TABLES[material][ion]['energy'].append(fake_spectrum.energies[0])
                    RANGE_TABLES[material][ion]['range'].append(x)
                    x += dx
                    fake_slice = FakeSlice(dx, material)
                    fake_spectrum.energies[0] -= energy_loss(fake_spectrum, fake_slice)[0]
                RANGE_TABLES[material][ion]['energy'].reverse()
                RANGE_TABLES[material][ion]['range'].reverse()
                RANGE_TABLES[material][ion]['energy'] = np.array(RANGE_TABLES[material][ion]['energy'])
                RANGE_TABLES[material][ion]['range'] = x - np.array(RANGE_TABLES[material][ion]['range'])

def energy_loss(spectrum, slice_):
    """
    This function should calculate the energy loss of a spectrum (in the present version, using Bethe formula).
    """
    stopping_power = bethe_CSDA(spectrum, slice_.layer.material)
    return slice_.thickness * stopping_power

def extract_created_ions():
    """
    Calculates the number of ions of each species created in the simulation.

    Returns
    -------
    data : dict: {Ion:float}
        The number of created ions.

    """
    data = {}
    for slice_ in SLICES_LIST:
        for reaction, n_reactions in slice_.reactions_numbers.items():
            for ion, n_ions, _ in reaction.output:
                if not ion in data:
                    data[ion] = 0.
                data[ion] += n_ions * n_reactions
    return data

def extract_energy_deposition():
    """
    Returns the energy deposited in each slice during the simulation.

    Returns
    -------
    xdata : numpy array
        Slice position (center of the slice) (m)
    ydata : nympy array
        Energy deposited (MeV)

    """
    xdata = .5 * (np.array(SLICES_FRONT_POSITIONS) + np.array(SLICES_BACK_POSITIONS))
    ydata = np.array([slice_.energy_deposit/slice_.thickness for slice_ in SLICES_LIST])
    return xdata, ydata

def extract_nuclear_reations():
    """
    Returns the number of reaction of each type that occured in each slice.

    Returns
    -------
    xdata : numpy array
        Slice position (center of the slice) (m)
    ydata : dict: {Reaction:list}
        For each reaction, its number of occurences in each slice.

    """
    xdata = .5 * (np.array(SLICES_FRONT_POSITIONS) + np.array(SLICES_BACK_POSITIONS))
    ydata = {reaction:[] for reaction in REACTIONS_LIST}
    for slice_ in SLICES_LIST:
        for reaction in REACTIONS_LIST:
            if reaction in slice_.reactions_numbers:
                ydata[reaction].append(slice_.reactions_numbers[reaction]/slice_.thickness)
            else:
                ydata[reaction].append(np.nan)
    return xdata, ydata

def extract_stopped_ions():
    """
    Returns the number of ions of each type that stopped in each slice.

    Returns
    -------
    xdata : numpy array
        Slice position (center of the slice) (m)
    ydata : dict: {Ion:list}
        For each reaction, its number of occurences in each slice.

    """
    if CALCULATE_PARTICLES_STOPPING:
        xdata = .5 * (np.array(SLICES_FRONT_POSITIONS) + np.array(SLICES_BACK_POSITIONS))
        ydata = {ion:[] for ion in PROPAGATING_IONS_SPECIES_LIST}
        for slice_ in SLICES_LIST:
            for ion in slice_.stopped:
                    ydata[ion].append(slice_.stopped[ion])
        return xdata, ydata
    else:
        print("Ions' stopping was not calculated")

def initiate_slices_and_spectrae():
    """
    Initialises the simulation.
    """
    layer_start = 0.
    layer_stop = 0.
    # CREATION OF SLICES
    for layer in LAYERS_LIST:
        layer_start = layer_stop
        layer_stop += layer.thickness
        layer.start = layer_start
        layer.stop = layer_stop
        # determination of slices' size map
        distance = 0.
        power = -1
        while distance <= layer.thickness / 2.: # finding with how many slices half thickness is reached
            power += 1
            distance += min(layer.step_min * layer.step_factor**power, layer.step_max)
        # oops, too far! back one step
        power -= 1
        distance -= min(layer.step_min * layer.step_factor**power, layer.step_max)
        fill_distance = layer.thickness - 2*distance # distance left to fill
        # actual creation of slices
        for p in range(power+1):
            Slice(layer, min(layer.step_min * layer.step_factor**p, layer.step_max))
        if fill_distance <= 0.: # no need to fill
            pass
        elif fill_distance <= layer.step_max: # one filler slice
            Slice(layer, fill_distance)
        else: # space to fill needs two filler slices
            Slice(layer, fill_distance/2.)
            Slice(layer, fill_distance/2.)
        for p in range(power, -1, -1):
            Slice(layer, min(layer.step_min * layer.step_factor**p, layer.step_max))
    # SLICES MISS THEIR REAR SPECTRUM. ADDING IT.
    for i, slice_ in enumerate(SLICES_LIST[:-1]):
        slice_.back_spectrums = SLICES_LIST[i+1].front_spectrums
    SLICES_LIST[-1].back_spectrums = {direction:{ion:Spectrum(ion, direction, np.empty(0), np.empty(0))
                                                for ion in PROPAGATING_IONS_SPECIES_LIST}
                                      for direction in ("front", "back")}
    # LISTING SLICES POSITIONS
    global SLICES_FRONT_POSITIONS, SLICES_BACK_POSITIONS
    SLICES_FRONT_POSITIONS = [slice_.front_position for slice_ in SLICES_LIST]
    SLICES_BACK_POSITIONS = [slice_.back_position for slice_ in SLICES_LIST]
    # SETTING UP INITIAL SPECTRAE
    [set_spectrum(position, spectrum) for position, spectrum in INITIAL_SPECTRUMS_LIST]

def input_spectrum(ions_type, position, direction, ions_energies, ions_populations_per_MeV):
    """
    Use this function to tell FISP to include a spectrum in the simulation.

    Parameters
    ----------
    ions_type : fisp.Ion
        The type of ion in the spectrum.
    position : scalar
        The position (in m) within the target where to insert the spectrum.
    direction : str
        "front" or "back". Direction of propagation of the spectrum relative to the target.
    ions_energies : array-like
        The lab frame energies of the datapoints of the spectrum (in MeV).
    ions_populations_per_MeV : array-like
        The corresponding amplitude datapoints.

    """
    check(isinstance(ions_type, Ion), "Ion type of the spectrum must be an instance of the Ion class.")
    check(direction in ("front", "back"), "Spectrum shoud propagate either to the front or the back of the target.")
    check(len(ions_energies) == len(ions_populations_per_MeV), "Ion spectrum energy and populations axis must be the same shape")
    check(bool(np.all(ions_energies > 0.)), "All energies in a Spectrum must be strictly positive")
    # sorting
    sorter = np.argsort(ions_energies)
    ions_energies = ions_energies[sorter]
    ions_populations_per_MeV = ions_populations_per_MeV[sorter]
    # creating energy bins
    energies = ENERGY_BINS_DISTRIBUTION(ions_energies[0], ions_energies[-1], ENERGY_BINS_NUMBER)
    populations_per_MeV = np.interp(energies, ions_energies, ions_populations_per_MeV)
    # conversion from particles/energy to particles/bin
    bin_sizes = np.diff(np.insert(energies, 0, max(0, 2*energies[0] - energies[1])))
    populations = populations_per_MeV * bin_sizes
    # appending to initials spectrae list
    INITIAL_SPECTRUMS_LIST.append((position, Spectrum(ions_type, direction, energies, populations)))
    # adding ion to propagating ions list
    if not ions_type in PROPAGATING_IONS_SPECIES_LIST:
        PROPAGATING_IONS_SPECIES_LIST.append(ions_type)

def plot_energy_deposition(ax=None, **kwargs):
    """
    If the energy deposit was calculated, plots the energy deposited in each slice during the simulation.

    Parameters
    ----------
    ax : matplotlib.pyplot.Axes, optional
        Axis to plot on. The default is the curretn axis obtained via plt.gca()
    **kwargs :
        Keyword arguments passed to matplotlib.pyplot.plot function.

    """
    if CALCULATE_ENERGY_DEPOSIT:
        ax = plt.gca() if ax is None else ax
        ax.set_xlabel('Position in target [m]')
        ax.set_ylabel('Energy deposition [MeV/m]')
        ax.set_title('Energy deposition')
        ax.plot(*extract_energy_deposition(), **kwargs)
        ax.set_yscale('log')
    else:
        print('Energy deposition was not calculated.')

def plot_nuclear_reactions(which='all', ax=None, **kwargs):
    """
    Returns the number of reaction of each type that occured in each slice.

    Parameters
    ----------
    which : str or iterable of fisp.Reaction, optional
        Which reactions to plot. The default is 'all'.
    ax : matplotlib.pyplot.Axes, optional
        Axis to plot on. The default is the curretn axis obtained via plt.gca()
    **kwargs :
        Keyword arguments passed to matplotlib.pyplot.plot function.

    """
    reactions_to_plot = REACTIONS_LIST if which == 'all' else [r for r in REACTIONS_LIST if r in which]
    ax = plt.gca() if ax is None else ax
    ax.set_xlabel('Position in target [m]')
    ax.set_ylabel('Density of reactions [/m]')
    ax.set_title('Densities of reactions')
    ax.set_yscale('log')
    xdata, ydata = extract_nuclear_reations()
    [ax.plot(xdata, ydata[reaction], label=reaction.name, **kwargs) for reaction in reactions_to_plot]
    ax.legend()

def plot_range(ax=None, **kwargs):
    """
    If the ranges were calculated, plots the ranges of all particles of the simulation in all materials of the
    simulation with respect to their energy.

    Parameters
    ----------
    ax : matplotlib.pyplot.Axes, optional
        Axis to plot on. The default is the curretn axis obtained via plt.gca()
    **kwargs :
        Keyword arguments passed to matplotlib.pyplot.plot function.

    """
    if not CALCULATE_ENERGY_DEPOSIT and not CALCULATE_PARTICLES_STOPPING:
        ax = plt.gca() if ax is None else ax
        for material in RANGE_TABLES:
            for ion in RANGE_TABLES[material]:
                if ion.Z == 0: # neutron
                    continue
                ax.plot(RANGE_TABLES[material][ion]['energy'], RANGE_TABLES[material][ion]['range'],
                        label=f'{ion.name} range in {material.name}', **kwargs)
        ax.set_title("Ion ranges")
        ax.set_xlabel('Ion energy [MeV]')
        ax.set_ylabel('Ion range [m]')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend()
    else:
        print('Ranges were not calculated')

def plot_stopped_ions(ax=None, **kwargs):
    """
    Plots the number of ions of each type that stopped in each slice.

    Parameters
    ----------
    ax : matplotlib.pyplot.Axes, optional
        Axis to plot on. The default is the curretn axis obtained via plt.gca()
    **kwargs :
        Keyword arguments passed to matplotlib.pyplot.plot function

    """
    if CALCULATE_PARTICLES_STOPPING:
        ax = plt.gca() if ax is None else ax
        ax.set_xlabel('Position in target [m]')
        ax.set_ylabel('Number ions [/m]')
        ax.set_title('Ions stopped in target')
        ax.set_yscale('log')
        xdata, ydata = extract_stopped_ions()
        [ax.plot(xdata, ydata[ion], label=ion.name, **kwargs) for ion in PROPAGATING_IONS_SPECIES_LIST]
        ax.legend()
    else:
        print("Ions' stopping was not calculated.")

def plot_stopping_power(ax=None, **kwargs):
    """
    Plots the stopping power curves calculated and used in this simulation.

    Parameters
    ----------
    ax : matplotlib.pyplot.Axes, optional
        Axis to plot on. The default is the curretn axis obtained via plt.gca()
    **kwargs :
        Keyword arguments passed to matplotlib.pyplot.plot function.

    """
    ax = plt.gca() if ax is None else ax
    for material in BETHE_CURVE_CACHE:
        for ion in BETHE_CURVE_CACHE[material]:
            if ion.Z == 0: # neutron
                continue
            energies = BETHE_CURVE_CACHE[material][ion]['energies']
            stopping_power = BETHE_CURVE_CACHE[material][ion]['stop_power']
            ax.plot(energies, stopping_power, label=f'{ion.name} in {material.name}', **kwargs)
    ax.set_xlabel('Ion energy [MeV]')
    ax.set_ylabel('Stopping power [MeV/m]')
    ax.set_title('Stopping powers')
    ax.legend()
    ax.set_xscale('log')
    ax.set_yscale('log')

def plot_target():
    """
    Plot the layout of the target: the diferent layers and their slices' thickness with respect to their position.

    """
    fig, ax = plt.subplots()
    ax.set_title('Target geometry')
    ax.set_xlabel('Position [m]')
    ax.set_ylabel("Slices's size [m]")
    ax.set_yscale('log')
    positions = .5 * (np.array(SLICES_FRONT_POSITIONS) + np.array(SLICES_BACK_POSITIONS))
    size = [slice_.thickness for slice_ in SLICES_LIST]
    ax.plot(positions, size, 'k-', lw=.1)
    # Attribute colors to materials
    colordict = {}
    availcolors = list(mcolors.TABLEAU_COLORS)
    navailcolors = len(availcolors)
    for i, material in enumerate(MATERIALS_LIST):
        colordict[material] = availcolors[i%navailcolors]
    colors = [colordict[slice_.layer.material] for slice_ in SLICES_LIST]
    ax.scatter(positions, size, .4, colors, '|')

def print_created_ions():
    """
    Prints the number of ions of each species created in the simulation.

    """
    data = extract_created_ions()
    if len(data) == 0:
        print('No created ions\n')
    else:
        print("\nCREATED IONS:")
        max_name_length = max([len(ion.name) for ion in data])
        [print(ion.name.ljust(max_name_length), f'{data[ion]:.3g}') for ion in data]
        print('')

def reverse_slices_list():
    """
    Reverses slices positions and indexes in SLICES_LIST
    """
    SLICES_LIST.reverse()
    for i, slice_ in enumerate(SLICES_LIST):
        slice_.index = i

def reset(range_tables=True, perf_timings=True):
    """
    Resets all values of the current simulation: only the parameters are left, all target geometry and input
    spectrae is deleted.

    Parameters
    ----------
    range_tables : bool, optional
        Decide wether or not reseting range tables. The default is True.
    perf_timings : bool, optional
        Decide wether or not reseting function timings. The default is True.

    """
    global INITIAL_SPECTRUMS_LIST, LAYERS_LIST, MATERIALS_LIST, PERF_TIMINGS, PROPAGATING_IONS_SPECIES_LIST, \
           RANGE_TABLES, REACTIONS_LIST, SLICES_LIST, SLICES_BACK_POSITIONS, SLICES_FRONT_POSITIONS, FRONT_SPECTRA,\
           REAR_SPECTRA
    if range_tables:
        RANGE_TABLES = {}
    if perf_timings:
        PERF_TIMINGS = {}
    INITIAL_SPECTRUMS_LIST = []
    LAYERS_LIST = []
    MATERIALS_LIST = []
    PROPAGATING_IONS_SPECIES_LIST = []
    REACTIONS_LIST = []
    SLICES_LIST = []
    SLICES_BACK_POSITIONS = []
    SLICES_FRONT_POSITIONS = []

def run():
    """
    The function to call to trigger the FISP simulation, once all setup is done.

    """
    print("FISP by Howel Larreur. Prototype version.\n")
    print("Initialising simulation.")
    # CREATING TARGET CALCULATION STEPS AND INITIAL SPECTRAE
    initiate_slices_and_spectrae()
    # if energy deposit & particle stopping calculation is not requested,
    # calculates a range table for all propragating particles in all materials
    if not CALCULATE_ENERGY_DEPOSIT and not CALCULATE_PARTICLES_STOPPING:
        print('Calculating range tables.')
        create_range_tables()
    print("\nInitialisation done. Running simulation.")
    simulate()
    return SLICES_LIST

def save_energy_deposition(filename):
    """
    Saves the energy deposition inside each slice of the simulation to a csv file in the following format:
        center position of the slice [m], deposited energy [MeV]

    Parameters
    ----------
    filename : str
        Name of the file. The extension '.csv' is added if it is not already present.

    """
    if CALCULATE_ENERGY_DEPOSIT:
        directory = os.path.dirname(inspect.stack()[1].filename) + os.sep
        filename = filename+'.csv' if filename[-4:] != '.csv' else filename
        name = directory + filename
        try:
            with open(name, 'x') as file:
                file.write('position [m], energy deposition [MeV/m]\n')
                for p, e in zip(*extract_energy_deposition()):
                    file.write(f'{p}, {e}\n')
        except FileExistsError:
            if ask_overwrite(name):
                save_energy_deposition(filename)
    else:
        print('Energy deposition was not calculated.')

def save_created_ions(filename):
    """
    Saves the number of ions of each species created in the simulation to a csv file with the following format:
        ion, number of reated ions

    Parameters
    ----------
    filename : str
        Name of the file. The extension '.csv' is added if it is not already present.

    """
    directory = os.path.dirname(inspect.stack()[1].filename) + os.sep
    filename = filename+'.csv' if filename[-4:] != '.csv' else filename
    name = directory + filename
    data = extract_created_ions()
    try:
        with open(name, 'x') as file:
            for ion in data:
                file.write(f'{ion.name}, {data[ion]}\n')
    except FileExistsError:
        if ask_overwrite(name):
            save_created_ions(filename)

def save_nuclear_reactions(filename):
    """
    Saves the number of reaction of each type that occured in each slice to a csv file with this format:
        reaction, positition [m], density of reactions [/m]


    Parameters
    ----------
    filename : str
        Name of the file. The extension '.csv' is added if it is not already present.

    """
    directory = os.path.dirname(inspect.stack()[1].filename) + os.sep
    filename = filename+'.csv' if filename[-4:] != '.csv' else filename
    name = directory + filename
    try:
        with open(name, 'x') as file:
            file.write('reaction, position [m], density of reactions [/m]\n')
            position, data = extract_nuclear_reations()
            for reaction, number in data.items():
                for p, n in zip(position, number):
                    file.write(f'{reaction.name}, {p}, {n}\n')
    except FileExistsError:
        if ask_overwrite(name):
            save_nuclear_reactions(filename)

def save_range(filename):
    """
    If the ranges were calculated, saves the ranges of all particles of the simulation in all materials of the
    simulation with respect to their energy to a csv file with the following format:
        material, ion, energy [MeV], range [m]

    Parameters
    ----------
    filename : str
        Name of the file. The extension '.csv' is added if it is not already present.

    """
    if not CALCULATE_ENERGY_DEPOSIT and not CALCULATE_PARTICLES_STOPPING:
        directory = os.path.dirname(inspect.stack()[1].filename) + os.sep
        filename = filename+'.csv' if filename[-4:] != '.csv' else filename
        name = directory + filename
        try:
            with open(name, 'x') as file:
                file.write('material, ion, energy [MeV], range [m]\n')
                for material, subdict in RANGE_TABLES.items():
                    for ion, subsubdict in subdict.items():
                        for energy, ion_range in zip(subsubdict['energy'], subsubdict['range']):
                            file.write(f'{material.name}, {ion.name}, {energy}, {ion_range}\n')
        except FileExistsError:
            if ask_overwrite(name):
                save_range(filename)
    else:
        print('Ranges were not calculated')

def save_stopped_ions(filename):
    """
    Saves the number of ions of each type that stopped in each slice with the format:
        position [m], ion, number of ions

    Parameters
    ----------
    filename : str
        Name of the file. The extension '.csv' is added if it is not already present.

    """
    if CALCULATE_PARTICLES_STOPPING:
        directory = os.path.dirname(inspect.stack()[1].filename) + os.sep
        filename = filename+'.csv' if filename[-4:] != '.csv' else filename
        name = directory + filename
        try:
            with open(name, 'x') as file:
                file.write('position [m], ion, number of ions\n')
                xdata, ydata = extract_stopped_ions()
                for ion in PROPAGATING_IONS_SPECIES_LIST:
                    for x, n in zip(xdata, ydata[ion]):
                        file.write(f'{x}, {ion.name}, {n}\n')
        except FileExistsError:
            if ask_overwrite(name):
                save_stopped_ions(filename)
    else:
        print("Ions' stopping was not calculated.")

def save_stopping_power(filename):
    """
    Saves the stopping power curves calculated and used in this simulation to a csv file with the format:
        material, ion, energy [MeV], stopping power [MeV/m]

    Parameters
    ----------
    filename : str
        Name of the file. The extension '.csv' is added if it is not already present.

    """
    directory = os.path.dirname(inspect.stack()[1].filename) + os.sep
    filename = filename+'.csv' if filename[-4:] != '.csv' else filename
    name = directory + filename
    try:
        with open(name, 'x') as file:
            file.write('material, ion, energy [MeV], stopping power [MeV/m]\n')
            for material, subdict in BETHE_CURVE_CACHE.items():
                for ion, subsubdict in subdict.items():
                    for energy, stpow in zip(subsubdict['energies'], subsubdict['stop_power']):
                        file.write(f'{material.name}, {ion.name}, {energy}, {stpow}\n')
    except FileExistsError:
        if ask_overwrite(name):
            save_stopping_power(filename)

def set_energy_bins(number=None, distribution=None, resize_trigger=None):
    """
    Sets the energy bin properties of the simulation.

    Parameters
    ----------
    number : int, optional
        The minimul number of bins of the energy spectrae. The default is 10 000.
    distribution : function, optional
        The energy bins distribution. The default is np.linspace.
        Must accept the same arguments as numpy.linspace and return in the same format.
    resize_trigger : scalar, optional
        If a spectrum gets too large (too much different energy bins values) during the simulation, it is resized
        to "number" values: too large is when the spectrum's size exceeds "resize_trigger" times "number".
        The default is 100.

    Returns
    -------
    None.

    """
    global ENERGY_BINS_DISTRIBUTION, ENERGY_BINS_NUMBER, ENERGY_BINS_RESIZE_TRIGGER
    if number is not None:
        ENERGY_BINS_NUMBER = number
    if distribution is not None:
        ENERGY_BINS_DISTRIBUTION = distribution
    if resize_trigger is not None:
        ENERGY_BINS_RESIZE_TRIGGER = resize_trigger

def set_simulation(calculate_energy_deposit, calculate_particles_stopping):
    """
    Set general parameters for the simulation.

    Note: When both arguments are set to False, this allows the code to use non-negligible optimizations.

    Parameters
    ----------
    calculate_energy_deposit : bool
        Tells FISP wether to save the energy depositing within each slice or not.
    calculate_particles_stopping : bool
        Tells FISP wether to save the number of particles stopping in each slice.

    """
    global CALCULATE_ENERGY_DEPOSIT, CALCULATE_PARTICLES_STOPPING
    check(isinstance(calculate_energy_deposit, bool), "CALCULATE_ENERGY_DEPOSIT must be set to a bool value")
    check(isinstance(calculate_particles_stopping, bool), "CALCULATE_PARTICLES_STOPPING must be set to a bool value")
    CALCULATE_ENERGY_DEPOSIT = calculate_energy_deposit
    CALCULATE_PARTICLES_STOPPING = calculate_particles_stopping

def set_spectrum(position, spectrum):
    """
    This function
    finds the slice index coresponding to the desired position
    saves the spectrum into this slice
    target needs to be defined before using this function
    """
    if (spectrum.direction == 'front') and (position < SLICES_BACK_POSITIONS[0]):
        SLICES_LIST[0].front_spectrums[spectrum.direction][spectrum.type].add(spectrum)
    elif (spectrum.direction == 'back') and (position > SLICES_FRONT_POSITIONS[-1]):
        SLICES_LIST[-1].back_spectrums[spectrum.direction][spectrum.type].add(spectrum)
    elif (spectrum.direction == 'back'):
        index = np.searchsorted(SLICES_FRONT_POSITIONS, position)
        SLICES_LIST[index].front_spectrums[spectrum.direction][spectrum.type].add(spectrum)
    elif (spectrum.direction == 'front'):
        index = np.searchsorted(SLICES_BACK_POSITIONS, position)
        SLICES_LIST[index].back_spectrums[spectrum.direction][spectrum.type].add(spectrum)
    else:
        raise Exception("Direction of the spectrum must be back or front.")

def simulate():
    """
    Once initialization is done. Starts simulation.
    """
    continue_passes = True
    pass_counter = 0
    while continue_passes is True:
        continue_passes = False
        pass_counter += 1
        for direction in ('back', 'front'):
            print(f'Pass {pass_counter}, {direction} direction')
            if direction == 'front':
                reverse_slices_list()
            for slice_ in tqdm(SLICES_LIST, disable=None, maxinterval=.5):
                # Defining side of the slice that spectrae should be taken from
                if direction == 'back':
                    spectrums_list = slice_.front_spectrums['back'].values()
                else: # if direction == 'front'
                    spectrums_list = slice_.back_spectrums['front'].values()
                # Doing calculations for each spectrum that is not empty
                for spectrum in spectrums_list:
                    size = spectrum.energies.size
                    if size == 0:
                        continue
                    spectrum.sort() # Sorts every time (even when not resizing) because somehow this makes the code faster.
                                    # This is now mantatody because some functions assume sorted spectrae
                    if size > ENERGY_BINS_RESIZE_TRIGGER * ENERGY_BINS_NUMBER:
                        spectrum.resize()
                    spectrum.energies = spectrum.energies
                    spectrum.populations = spectrum.populations
                    spectrum.do_slowing(slice_)
                    new_particles = spectrum.do_reactions(slice_)
                    spectrum.push(slice_)
                    spectrum.erase()
                    if new_particles is True:
                        continue_passes = True
            if direction == 'front':
                reverse_slices_list()
    print("\nCalculation done.")
    # Sorting and resizing all spectrums at the end
    for spectrums in ([slice_.front_spectrums for slice_ in SLICES_LIST] + [SLICES_LIST[-1].back_spectrums]):
        for direction in ('back', 'front'):
            for spectrum in [s for s in spectrums[direction].values() if s.energies.size != 0]:
                spectrum.sort()
                spectrum.resize()
    # outputting exiting spectra
    for ion in SLICES_LIST[0].front_spectrums['front']:
        FRONT_SPECTRA[ion] = SLICES_LIST[0].front_spectrums['front'][ion]
    for ion in SLICES_LIST[-1].back_spectrums['back']:
        REAR_SPECTRA[ion] = SLICES_LIST[-1].back_spectrums['back'][ion]

def speed_to_energy(ion, speed):
    """
    Calculates kinetic energy of the particles from their speed using relativistic formula.
    """
    speed_sq = speed**2 #speed in c unit
    gamma = 1./np.sqrt(1. - speed_sq)
    return gamma**2 / (gamma + 1.) * ion.mass * speed_sq
