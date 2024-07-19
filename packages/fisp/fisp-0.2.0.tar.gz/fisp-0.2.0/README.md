FISP is a 1D simulation code for the interaction of ion beams with cold solid targets. It should be seen as a less precise but much faster alternative to Monte-Carlo simulations: both types of simulations can complement each other.

Peer-reviewed paper to be published.


# Features
- Runs on a **personnal computer** with **short running times** (seconds to minutes depending on the simulation)
- **User friendly**: install as any other python package and easy to use
- **Multi-layer targets** of **any solid cold materials** of known composition
- Propagating single or **multiple spectra of any ion**
- **Reactions** between **any two nuclei** (user provides cross-section data)
- **Front and rear exiting spectra** calculation
- local **Energy deposition** calculation
- local **Number of reactions** calculation



# User guide

## Setting-up the simulation

In FISP, everything has to be manually declared. This includes atomic/ion species, materials, nuclear reactions and ion spectra.

### Ion species

Any atomic/ion species involved in a FISP simulation (in the composition of a material layer or as the product of a nuclear reaction for example) must be declared before anything else. This is done using the `Ion` class, for example let's declare an alpha particle (<sup>4</sup>He nucleus):
```
import fisp

Z = 2                 # Atomic number
A = 4                 # Mass number
mass = 3727.37941     # Ion mass energy in MeV
I = 41.8e-6           # Optionnal: mean excitation potential in MeV. Can be specified
                      # in the `Material` class instead. Less user-friendly.
ionization_energy = 0 # Optionnal: ionization energy in MeV. Useful for some simulations
                      # (see nuclear reactions part)
name = 'alpha'        # Optionnal: chose a name for plots

He4 = fisp.Ion(Z, A, mass, I=I, ionization_energy=ionization_energy, name=name)
```

### Materials

Once your ions are declared, you can add them to a material type using the `Material` class, for example with natural boron:
```
composition = {B10:.199, B11:.801} # 19.9% of boron 10 and 80.1% of boron 11, previously
                                   # declared using the Ion class
density = 2370                     # Density in kg/m^3
molar_mass = .0108135              # Molar mass in kg/mol
I = 76e-6                          # Optionnal: mean excitation potential in MeV. Default
                                   # is the average for the components of the materials.
name = 'boron'                     # Optionnal: chose a name for plots.
disable_warnings = True            # Optionnal: FISP will warn the user if there seems to
                                   # be a unit mistake on the values given for materials.
                                   # If you know better, you can disable these warnings here.

boron = fisp.Material(composition, density, molar_mass, mean_excitation_potential=I, name=name, disable_warnings=disable_warnings)
```

### Nuclear reactions

**Binary nuclear reactions**

Nuclear reactions that involve two nuclei turning into two other nuclei can be expressed as follows:
                *target (projectile, ejectile) product*
They can be declared easily using the `BinaryReaction` subclass of the main `Reaction` class, that is introduced in the next paragraph.
```
target = B11          # Boron 11, previously declared using the Ion class
projectile = H1       # proton (hydrogen 1)
ejectile = n          # neutron
product = C11         # carbon 11
data = mydata         # cross-section data. Expected format is (xdata, ydata), with xdata
                      # being the projectile energies in the lab frame, and ydata being
                      # the corresponding cross-sections in m². Yes, square meters.
name = 'p+B11->n+C11' # Optionnal: chose a name for plots.

pb11_nC11 = fisp.BinaryReaction(B11, H1, n, C11, data)
```

**Non binary nuclear reactions**

Other reactions can be declared using the `Reaction` class, which involves much more work from the user. For example with the reaction p + <sup>11</sup>B -> 3a (skipping calculations):
```
projectile = H1
target = B11
output_ions = [(He4, .5, func1), (He4, .5, func2), (He4, .5, func3), (He4, .5, func4), (He4, .5, func5), (He4, .5, func6)]
                   # Here: - He4 is the previously declared Ion object for alpha particles
                   #       - .5 stands for the number of alpha particles with a given speed.
                   #         Indeed, the reaction emits 3 alpha particles and each of these
                   #         alpha particles has a probability of one half to go forward and
                   #         one half to go backward*. At the macroscopic scale of our
                   #         simulations, large numbers law applies: it can be considered that
                   #         for each reaction, half a particle is emited in both direction.
                   #         *simplification were done here, the point is to understand. This
                   #         result is still correct though.
                   #       - func1 to func6 are user-provided functions taking as input a numpy
                   #         array containing the projectile (in our case, protons) energies.
                   #         The function must then return the *speed* of the particles created.
                   #         These speeds must be calculated in c units and in the lab frame,
                   #         with positive values indicating forward direction and negative
                   #         values indicating backward direction.
data = mydata      # cross-section data. Expected format is (xdata, ydata), with xdata
                   # being the projectile energies in the lab frame, and ydata being
                   # the corresponding cross-sections in m². Yes, square meters.
name = 'p+B11->3a' # Optionnal: chose a name for plots.

pb11_3a = fisp.Reaction(projectile, target, output_ions, data, name=name)
```
Note: only reactions between two atoms/ions are supported.

### Target layers

Now that materials and reactions have been declared, one can construct the target geometry using the `Layer` class. Indeed, FISP supports multi-layer target, each layer being a different material.
```
material = boron              # the Material object previously declared composing the layer
thickness = 100e-6            # the thickness of the layer in m
reactions = pb11_C11, pb11_3a # the previously declared nuclear reactions occuring within the layer
outer_step_size = 1e-8        # the step size of the code on the layer's borders in m
max_inner_step_size = 1e-6    # the maximum allowed step size of the code within the layer in m
step_factor = 1.01            # the ratio between the sizes of two consecutive steps. Indeed, as
                              # inner steps have less influence on the calculation's results, the
                              # code makes them larger to speed up the calculation.

fisp.Layer(material, thickness, reactions, outer_step_size, max, inner_step_size, step_factor)
```
One additionnal layer is added to the simulation each time the `Layer` class is called. The order the the layers in the simulated target is the order in which the user declares the layers.
The reset the layers, see the `reset` function below.


### Ion beam

An ion beam (spectrum) can be added anywhere inside the target using the `input_spectrum` function:
```
ions_type = H1            # Previously declared nature type of ions
position = 0.             # Start position of the spectrum in m
direction = 'back'        # Propagation direction of the spectrum ('front'/'back' is
                          # towards the front/back of the target)
energy_data = mydataE     # the spectrum energy bins values in MeV
population_data = lydataP # corresponding ion populations in /MeV 

fisp.input_spectrum(ions_type, position, direction, energy_data, population_data)
```

## Additional parameters and functions

### Set energy bins

The `set_energy_bins` function can be used to tune the parameters of the simulation regarding the energy bins: the number of bins, their distribution and the resizing trigger.
```
import numpy as np
# These are the defaults values
number = 10000
distribution = np.linspace
resize_trigger = 100

fisp.set_energy_bins(number, distribution, resize_trigger)
```

### Set simulation

The `set_simulation` function tells FISP wether to calculate the location of energy deposit and stopped particles within the target.
```
# These are the default values
calculate_energy_deposit = True
calculate_particles_stopping = True

fisp.set_simulation(calculate_energy_deposit, calculate_particles_stopping)
```
If **both** calculations are turned off, the simulation speed is greatly increased in most cases.

## Calling the run function

At this point, the simulation parameters and input are completely done. The run function should be called, and what it returns (the slices informations from the simulation) must be saved to allow for post-processing.
```
slices = fisp.run()
```

## Setting-up the post-processing

FISP embarks tools for prost-processing the simulations. They should be placed under the `run` function in the user's python file.

For more information about a function listed here, please consult its docstring.

### Plotting functions

FISP includes several plotting functions: `plot_energy_deposition`, `plot_nuclear_reactions`, `plot_range`, `plot_stopped_ions`, `plot_stopping_power`, `plot_target`.

The `Spectrum` class has it own plotting method: `plot'. The `Reaction` class also has its own plotting method: `plot_cross_section`.

### Printing function

FISP includes one printing function: `print_created_ions'.

### Data Saving

FISP includes functions to save data as csv files: `save_energy_deposition`, `save_created_ions`, `save_nuclear_reactions`, `save_range`, `save_stopped_ions`, `save_stopping_power` and the `Spectrum` class method `save`.

### Data extraction

For more flexibility, it is possible to access data from FISP inside Python:
- Data: `range_tables`, `reactions_list`, `front_spectra`, 'rear_spectra`
- Functions: 'extract_created_ions', 'extract_energy_deposition', 'extract_nuclear_reations', 'extract_stopped_ions'

## Resetting

At the end of the Python file, the `reset` function should be called. If not done, parametric studies or any following simulations in the same console will yield nonsensic results.

## Parametric studies
The original purpose of FISP is to include parametric studies. Thus, a function to run parametric studies is included. It works by running multiple Python interpeters at the same time with different parameters. Thus, the user needs to provide a functionning FISP namelist. In this namelist must be the flag $parametric$ for the value to replace, for example:
```
my_thickness = $parametric$
```
This flag will be replaced by a value of the parametric study for each simulation. To run a parametric study, user has to execute a separate python file:
```
import fisp

values = [1e-3, 2e-3, 3e-3]       # Values of the parametric study that replace the $parametric$ flag
namelist = 'namelist_parallel.py' # Name of the namelist file to run (the one with the $parametric$ flag)
output = 'test'                   # Optionnal: output directory. Default is current working directory.
cpu = 1                           # Optionnal: number of CPU cores to use. Note: as FISP is high-demanding
                                  # on memory bandwidth, using a lot of core does not scale well.
ignore_overwrite = True           # Tells wether to delete past simulations if they exist in the same directory.

fisp.prun(values, namelist, output_directory=output, workers=cpu, ignore_overwrite=ignore_overwrite)

```


# Changelog

### Version **0.2.0**
Added documentation.
Changed default nuclear reactions names.
Not necessary anymore to save the output from `fisp.run` and search though it to find exiting spectra: just read from `fisp.front_spectra` and `fisp.rear_spectra`.
`Spectrum` class method `save_csv` method is now named `save`.

### Version **0.1.1**
Overwriting files at the end of simulations now works.

### Version **0.1**
Initial release.