# Data Description

## Overview
This example demonstrates analysis of cosmic microwave background (CMB) temperature data to investigate cosmological parameters and early universe physics.

## Data Sources

### Primary Data
- **Planck 2018 CMB Temperature Maps**: Full-sky temperature maps from the Planck satellite mission
- **Format**: HEALPix FITS files with NSIDE=2048
- **Coverage**: Full sky with masked regions (Galaxy, point sources)
- **Noise**: Instrumental noise maps included

### Supporting Data
- **Planck Power Spectra**: Pre-computed angular power spectra (C_ℓ)
- **BAO Measurements**: Baryon Acoustic Oscillation distance measurements from SDSS
- **Local H0 Measurements**: Hubble constant measurements from Cepheid variables

## Available Tools

### Python Libraries
- **healpy**: HEALPix map manipulation and visualization
- **numpy/scipy**: Numerical analysis and statistics
- **matplotlib**: Plotting and visualization
- **emcee**: MCMC sampling for parameter estimation
- **CLASS/CAMB**: Boltzmann solvers for theoretical predictions (via Python wrappers)

### Computational Resources
- Local workstation with 32GB RAM
- 16 CPU cores for parallel processing
- GPU available for accelerated computations

## Research Context

### Scientific Domain
Observational cosmology, specifically CMB physics and parameter estimation.

### Key Questions
1. Can we improve constraints on cosmological parameters using novel analysis techniques?
2. Are there subtle systematic effects in CMB data that could bias parameter estimates?
3. What do anomalies in CMB data (e.g., hemispherical asymmetry) tell us about early universe physics?

### Constraints
- Analysis should be reproducible with publicly available data
- Computational time should be reasonable (days, not weeks)
- Methods should be complementary to existing Planck collaboration analyses

### Background
The CMB is a snapshot of the universe at 380,000 years after the Big Bang. Its temperature fluctuations encode information about:
- Cosmological parameters (H0, Ωm, Ωb, etc.)
- Initial conditions and inflation
- Dark matter and dark energy properties

Current challenges include:
- Tension between early and late universe measurements of H0
- Anomalies at large angular scales
- Foreground contamination (Galaxy, point sources)
- Systematic uncertainties in instruments
