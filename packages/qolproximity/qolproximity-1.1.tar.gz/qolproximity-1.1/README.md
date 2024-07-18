
# Note
This package requires 'arcpy' which is part of Esri's ArcGIS software and 
cannot be installed via pip. Please ensure you have ArcGIS installed and 
configured correctly. You can get arcpy if you install ArcGIS Pro

# Proximity Analysis with ArcPy for Urban Institute's Quality of Life Explorer

This package provides a Python class `proximity` tailored for analyzing spatial relationships in GIS, specifically designed for Urban Institute's Quality of Life explorer (QOL) spatial variables.

## Installation

Install `qolproximity` from PyPI using pip:

pip install qolproximity

## Usage

import qolproximity as qol

# Example usage for proximity to Pharmacy:
P = qol.proximity('TaxData2023', 'Pharmacy2024')

# Merge pharmacy data 
P.merge('Pharmacy', 'PharmacyUnmatched')

# Add a new field for residential proximity to pharmacy
P.addfield('ResNearPharmacy')

# Summarize the results
P.summarize('r', 'd', ProjectGDB)

# Export summarized results to a text file
P.exportcsv(path, 'QOL_46_2023.csv')

## Methods

__init__(self, tax_parcel_feature_class, proximity_feature_class): Initialize the proximity class with the tax parcel feature class and proximity feature class.

merge(self, *feature_classes_to_be_merged): Merge proximity feature classes from multiple sources into one feature class for analysis.

addfield(self, new_field_name): Add a new field to the tax parcel feature class.

summarize(self, near_residential_output_table, housing_units_table, geodatabase): Summarize residential units near the proximity feature class and export results to a geodatabase.

exporttxt(self, output_directory, final_txt_name): Export summarized results to a text file in the specified directory.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
