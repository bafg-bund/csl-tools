
# Preparation of standard
A solution is made with 100 µg/L in MeOH or other solvent if needed. The purity of the standard is included in the calculation of the dilution if the purity of the standard is less than 95%. The mass of counter-ions is removed when preparing salts. 

# Chromotography method
Use the same method as would be used in your labs NTS monitoring measurements. This method must be included in the Table X in chrom_methods.md document (in preparation). If it is missing from that document please contact ntsportal@bafg.de.

# MS2 experiment settings
For the acquisition of standards, instead of DDA (data dependent acquision or IDA, information dependent Acquisition, or dynamically selected ions for fragmentation), as is set for NTS, several product ion scans are defined for the m/z of the analyte in advance. In the case of SCIEX TripleTOFs the collision energy (CE) settings are in V, however this may depend on your instrument. Therefore please provide the units used for CE for your data. For Orbitrap users, please do not use normalized collision energies (NCE). Example acquision settings on a SCIEX TripleTOF are as follows: a total of 16 scans are defined with varying collision energies (10 to 150 V), plus one scan with a collision energy of 40 V and a collision energy spread of 15 V (spectra at 25, 40, and 55 V are averaged). To ensure comparability, it would be beneficial that the method you choose adheres as close as possible to these settings.

# Data preparation and export
Please refer to the software specific SOPs. If your software is not listed, please contact ntsportal@bafg.de to develop a new SOP.
