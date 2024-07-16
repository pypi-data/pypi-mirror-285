# pyIsotherm: A Comprehensive Python Library for Adsorption Isotherm Parameter Estimation

## Overview

The `pyIsotherm` library is a powerful Python tool designed to facilitate the estimation of adsorption isotherm parameters using Particle Swarm Optimization (PSO). It supports seven isotherm models: Langmuir, Langmuir-Freundlich (Sips), Toth, BET, BET-Aranovich, GAB, and Langmuir Multisite. This library is ideal for researchers working on adsorption studies, offering a simple, fast, and free method to obtain fundamental parameters.

## Features

- **Support for Multiple Isotherm Models**: Langmuir, Sips, Toth, BET, BET-Aranovich, GAB, and Langmuir Multisite.
- **Particle Swarm Optimization (PSO)**: Efficient parameter estimation using PSO.
- **Data Loading**: Load experimental data from `.xlsx` or `.csv` files.
- **Plotting Capabilities**: Visualize experimental and simulated isotherms.
- **Error Analysis**: Comprehensive error analysis, including absolute, quadratic, mean, and standard deviation of errors.
- **Kruskal-Wallis Test**: Statistical test to compare medians of experimental and simulated data.

## Installation

Install the `pyIsotherm` library via pip:

```sh
pip install pyIsotherm
```

## Usage

### Loading Experimental Data

Load data from a `.csv` or `.xlsx` file:

```python
from pyIsotherm.Load import load

isotherm = load('data.xlsx')
```

### Estimating Isotherm Parameters

Estimate parameters using the `estimate` function:

```python
from pyIsotherm.Estimation import estimate

result = estimate(p=[1, 2, 3], qe=[0.1, 0.2, 0.3], model='langmuir')
```

### Plotting Isotherms

Plot the experimental and simulated isotherms:

```python
result.plot()
```

### Error Analysis

Print various error analyses:

```python
result.error_all()
```

## Isotherm Models

<img width="500" alt="Formulas" src="https://github.com/evandronk/pyIsotherm/blob/main/formulas.jpeg?raw=true">

## Classes and Methods

### `Isotherm`

The `Isotherm` class represents the isotherm data:

```python
class Isotherm:
    def __init__(self, p, q):
        # Initialize with pressure and quantity adsorbed lists.
        
    def plot(self):
        # Plot the isotherm data.
```

### `Particle`

The `Particle` class is used in PSO for parameter estimation:

```python
class Particle:
    def __init__(self, param):
        # Initialize with parameter ranges.
        
    def update_velocity(self, swarm_best_position):
        # Update particle velocity.
        
    def update_position(self):
        # Update particle position.
```

### `Result`

The `Result` class encapsulates the estimation results:

```python
class Result:
    def __init__(self, parameters, fitness, exp_isotherm, sim_isotherm):
        # Initialize with parameters, fitness, and isotherms.
        
    def plot(self, export=False, extension='png', only_exp=False, only_sim=False, legend=False):
        # Plot the isotherms.
        
    def error_all(self):
        # Print all error analyses.
        
    def kruskal(self):
        # Perform Kruskal-Wallis test.
```

## Example

```python
from pyIsotherm.Load import load
from pyIsotherm.Estimation import estimate

# Load experimental data
isotherm = load('data.xlsx')

# Estimate parameters
result = estimate(p=isotherm.p, qe=isotherm.q, model='langmuir')

# Plot the isotherms
result.plot()

# Print error analysis
result.error_all()

# Perform Kruskal-Wallis test
result.kruskal()
```

## References

The theoretical background and model equations implemented in the `pyIsotherm` library are based on the extensive research and publications in the field of adsorption.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on the code of conduct, and the process for submitting pull requests.

---

With `pyIsotherm`, streamline your adsorption isotherm studies with robust parameter estimation and comprehensive data analysis tools. Happy researching!
