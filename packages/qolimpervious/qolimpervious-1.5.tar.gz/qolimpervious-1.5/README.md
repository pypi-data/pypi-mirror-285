
# Impervious Surface Analysis

This package provides a Python class `impervious` tailored for analyzing impervious surface using ArcPy. The class is designed for Urban Institute's Quality of Life (QOL) variables.

## Installation

Install `qolimpervious` from PyPI using pip:


pip install qolimpervious

# Usage

import `pandas` as `pd`

import `arcpy`

import `qolimpervious` as `qi`

I = qi.impervious('Singlefamily_Impervious_2023','Commercial_Impervious_2023','Impervious2023')

I.intersect('NPA2023','IntersectImpervious2023')

I.exportcsv(path,'QOL_04_2023.csv')


# Methods

impervious

This class executes impervious surface analysis for Urban Institute's QOL Variables.

`__init__(self, residential, commercial, UnionOutputname)`

- residential: The residential landuse featureclass.

- commercial: The commercial landuse featureclass.

- UnionOutputname: Name of output featureclass for the union analysis.

`union(self)`

Unions the residential and commercial feature classes used for computing the total impervious surface in the city.

`dissovle(self)`

Adds a field to the Union feature class, calculates the field as 0, and dissolves the Union Feature class using the added field.

`intersect(self, NPAFeatureclass, IntersectOutput)`

NPAFeatureclass: The NPA feature class.

IntersectOutput: The output name for the intersect analysis.

Performs the intersect analysis and calculates the area of intersected features.

`exportcsv(self, OutputDirectory, Filename)`

- OutputDirectory: The directory where the CSV file will be exported.

- Filename: The name of the CSV file.

- Exports the results of the impervious surface analysis as a CSV file.

License

This project is licensed under the MIT License - see the LICENSE file for details.