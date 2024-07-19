
# Voter Participation Analysis for QOL

This package provides a Python class `voters` for analyzing voter participation rate for Urban Institute's Quality of Life (QOL) variables. It includes methods for spatial joining, summarizing voter data by NPA (Neighborhood Planning Area), and exporting the results to a CSV file.

# Installation

Install `voters` from PyPI using pip:


pip install qolvoters


# Usage
import pandas as pd 
import arcpy
import qolvoters as vt

# Example usage:
voter_analysis = vt.voters('GeocodedVoterPointAddresses', 'NPA_FeatureClass', 'SummaryTable')

# Summarize voter data by NPA
voter_analysis.summary('ActiveVoters', 'Join_Count')

# Export summarized results to a CSV file
voter_analysis.export('OutputDirectory', 'VoterParticipationSummary.csv')

# Methods 

`__init__(self, voterparticipation, NPA, SummaryTableName)`

Initialize the voters class with the following parameters:

* voterparticipation: Geocoded voter participation feature class.

* NPA: NPA feature class.

* SummaryTableName: Name of the summary table for voters in each NPA.

Assign NPA IDs to each voter by performing a spatial join between the voter participation feature class and the NPA feature class.

`summary(self, *FieldsToBeSummarized)`

Compute the summary of all voters within each NPA. Takes parameters for the fields to be summarized (e.g., active voters field and the 'Join_Count' field).

`export(self, OutputDirectory, FinalCSVName)`

Export the results of the voter participation analysis to a CSV file. Renames columns and computes additional fields before exporting the final CSV file.

# License

This project is licensed under the MIT License - see the LICENSE file for details.