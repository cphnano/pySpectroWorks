# pySpectroWorks

pySpectroWorks is a Python module for loading data from SpectroWorks™. This readme file provides a brief introduction to the module and how it can be used.

## Getting started

Installation:

```
pip install pyspectroworks
```

Import the module and establish a connection to SpectroWorks™ using your API key:
```
import pyspectroworks

api_key = "INSERT_API_KEY_HERE"
conn = pyspectroworks.connect(api_key)
```

## Usage

Once you have a connection instance you can extract all your projects as a list:
```
projects = conn.get_projects()
```

Each element in this list is a `Project` object. All data about a project is found in its `data` attribute, however, the most useful information has its own attributes:
```
project = projects[0]  # get first project
print("Project name:", project.project_name)
print("Number of items:", project.num_files)
print("Created:", project.created)  # unix timestamp of when this project was created
print("Last modified:", project.modified)  # unix timestamp of when this project was last modified
```
 
Each project can include several items. These are your experiments and can be extracted with the `get_items` method:
```
items = project.get_items() # get all items in project
```

Like projects, items include a multitude of different data which can be accessed by the item's `data` attribute. 
The box code and cuvette number can be found in the `box_code` and `cuvette_idx` attributes. 
Calculated results are available in the items `results` attribute.

 ```
item = items[0] # get first item
ri = item.results['refractive_index']['value'] # get the refractive index
# print cuvette and refractive index
print(f'Cuvette: {item.box_code: >6}{item.cuvette_idx:0>2}, Refractive Index: {ri: >8}')
```

To extract the spectral data use the `get_spectrum` method of the item.  
The available spectrum types are:
 - `reference_B` (B side reference spectrum)
 - `sample_A` (A side sample spectrum)
 - `sample_B` (B side sample spectrum)
 - `sample_D` (D side sample spectrum)
 
```
spectrum = item.get_spectrum('sample_B')
```

The spectrum is a list consisting of pairs of wavelengths and attenuance values. 

# Example script
An example script can be found in [api_test.py](api_test.py)

# Aplications
- **Analysis of water quality** - pySpectroWorks can be used to extract spectral data from water samples, which can be used to identify pollutants and contaminants.

- **Analysis of beverages** - pySpectroWorks can be used to analyze the spectral data of beverages such as wine, beer, and juice, which can provide information on their chemical composition and quality.

- **Analysis of oils and fats** - pySpectroWorks can be used to analyze the spectral data of liquid oils and fats, which can provide information on their composition and purity.

- **Analysis of biological fluids** - pySpectroWorks can be used to extract spectral data from biological fluids such as blood, urine, and saliva, which can provide information on disease diagnosis and treatment.