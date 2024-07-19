
# Aggregate Data Analysis with ArcPy

This package provides a Python class `aggregate` tailored for analyzing and aggregating spatial data using ArcPy. The class is designed for Urban Institute's Quality of Life (QOL) variables, offering methods for merging, spatial joining, and exporting data to CSV files.

## Installation

Install `aggregate` from PyPI using pip:


pip install aggqol

# Usage

import aggqol as ag

A = ag.aggregate()

A.withinNPA('NPA','Banks','BanksNPA')

A.withNPAID('CreditUnion','NPA', 'CreditNPAID')

## Methods

Methods
`__init__(self, InFeatureClass)`

Initialize the aggregate class with the input feature class.

`merge(self, *FeatureClassesToBeMerged)`

Combine feature classes from multiple sources into one feature class for analysis.

`withinNPA(self, NPA, OutputName)`

Aggregate all points feature classes that are completely contained by an NPA polygon.

`withNPAID(self, NPA, OutputName)`
Assign NPA ID to all point feature classes that are completely within an NPA.

`exportcsv(self, OutputDirectory, PopulationFile, PopulationColumn, FileName)`

Export the results to a CSV file, joining population data and calculating summary statistics.

## Additonal Information

- The aggregate class is initialized with no arguments.This class has two methods:
    - The *withinNPA* method: This method aggregates point features classes that are completely contained by each NPA 
      The withinNPA method takes two arguments: 
       - NPA feature class
       - Point feature class to be aggregated
       - Name of output feature class
        
    - The *withNPAID* method: This method assign NPA IDs to point feature classes that are completely within each NPA
       - Point feature classes 
       - NPA feature class 
       - Name of output feature class

License
This project is licensed under the MIT License - see the LICENSE file for details.