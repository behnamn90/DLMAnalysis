# DLMAnalysis
Analysis tools for domain-level model (DLM) simulations. This is an accompanying package for the main DLM code, which is written in C++:<br>
https://github.com/behnamn90/DLM

Together, they are used to produce all the results in my doctoral thesis:<br>
https://ora.ox.ac.uk/objects/uuid:23ca884b-f547-4458-9e43-494fd6c2f6a3

## Functionalities:
- Convert cadnano files (https://cadnano.org/) to input files used in DLM simulations.
- Run batch DLM simulations. This requires the excecutable from C++ code.
- Analyse batch simulation results; these are large datasets that describe DNA origami trajectories.
- Plot melting and annealing curves.
- Plot the state of individual strands during the simulation.
- Create movies of the trajectory the origami follows.

### Simulation Types:
- Simulate the folding/unfolding of DNA origami under annealing/melting protocol, with the temperature typically decreased/increased between $~100^\degree C$ to $~40^\degree C$.
- Simulate folding/unfolding of DNA origami at a set temperature.
- Perform biased simulations and extract free energy profiles as a function of observables.
- Simulate displacement of one staple set with another.

## Usage:
See the [`demo.ipynb`](demo.ipynb) for some basic usage. Note that the project is designed to run on computer clusters and produces large datasets. Some pre-analysed data is included here to demonstrate the usage.

