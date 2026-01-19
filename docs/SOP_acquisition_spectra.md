# Acquisition of spectral data for contributors

## Preparation of standard
Prepare a solution with a concentration of 100 µg/L in MeOH (or another suitable solvent, if required). If the purity of the standard is below 95%, include the purity correction in your dilution calculation. When preparing salts, exclude the mass of counter-ions from the calculation.

## Chromatography method
Use the same chromatography method that is used in your laboratory’s NTS monitoring measurements.

This method must be listed in Table X of the chrom_methods.md document (in preparation). If your method is not listed, please contact ntsportal@bafg.de.

## MS² experiment settings
To ensure data comparability, the acquisition method should match these example settings as closely as possible. For the acquisition of standards, do not use DDA (Data-Dependent Acquisition), IDA (Information-Dependent Acquisition), or dynamically selected ions for fragmentation as used in NTS measurements. Instead, define multiple product ion scans for the m/z of the analyte in advance. 

Example acquisition settings:
- Define a total of 16 scans with collision energies ranging from 10 to 150 V.
- Include one additional scan with CE = 40 V and a collision energy spread (CES) of 15 V (spectra at 25, 40, and 55 V are averaged).
     
General notes:
- Please note that CE units may differ depending on your instrument; specify the units used in your data submission.

Notes for SCIEX TripleTOF instruments:
- Collision Energy (CE) settings are given in volts (V).

Notes for Orbitrap instruments:
- Do not use normalized collision energy (NCE).

## Data preparation and export
Refer to [this guideline](SOP_contribution_spectra.md) for the requirements of the export format. 
If your software is not listed, please contact ntsportal@bafg.de for assistance.
