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
print("Results:", project.results)  # List of results available in this project. 
```
 
### Items
Each project can include several items. These are your experiments and can be extracted with the `get_items` method:
```
items = project.get_items() # get all items in project
```

Like projects, items include a multitude of different data which can be accessed by the item's `data` attribute. 
The box code and cuvette number can be found in the `box_code` and `cuvette_idx` attributes. 
Calculated results are available in the items `results` attribute.
**Note**: It is not guaranteed that every project result is available in each project item. This can happen when results are added to the project after the item was created.

 ```
item = items[0] # get first item
ri = item.results['refractive_index']['value'] # get the refractive index
# print cuvette and refractive index
print(f'Cuvette: {item.box_code: >6}{item.cuvette_idx:0>2}, Refractive Index: {ri: >8}')
```

The `results` attribute is a dictionary with the result name as the key and a dictionary with the result value and unit as the value. 

**Note**: The result name is not the same as what is shown in the SpectroWorks™ web interface. The result name is the internal name of the result as it is stored in the database. E.g. "Refractive Index" is "refractive_index", "° Brix" is "convert_to_brix", etc. 

### Spectra
To extract the spectral data use the `get_spectrum` method of the item.  
Spectra are identified by whether it is a reference or sample spectrum and which side of the cuvette it was measured on. 
The sides are labeled A, B, and D. The sides refer to which side of the cuvette is facing the light source. 
For basic cuvettes only side A is used. 
 - For NanoCuvette™, side A is either of the sides perpendicular to the side that has the optical filter, arrow mark and cuvette number.
 - Side B is the side with the optical filter, arrow mark and cuvette number.
 - Side D is the side opposite to side B.

The spectrum is a list consisting of pairs of wavelengths (nm) and attenuance values (absorbance units). 

Furthermore, the `get_spectrum` method can also be used to get the simulated spectrum used by the analysis model. 
This is done by appending `_model` to the spectrum type.

The available spectrum types are:
 - `reference_A` (reference spectrum, side A)
 - `reference_B` (reference spectrum, side B)
 - `reference_D` (reference spectrum, side D)
 - `sample_A` (sample spectrum, side A)
 - `sample_B` (sample spectrum, side B)
 - `sample_D` (sample spectrum, side D)
 - `reference_B_model` (simulated spectrum for reference, side B)
 - `sample_A_model` (simulated spectrum for sample, side A)
 - `sample_B_model` (simulated spectrum for sample, side B)
 - `sample_D_model` (simulated spectrum for sample, side D)

```
spectrum = item.get_spectrum(<spectrum type>)
```


# Example script
An example script can be found in [pyspectroworks_example.py](pyspectroworks_example.py)

# Aplications
- **Analysis of water quality** - pySpectroWorks can be used to extract spectral data from water samples, which can be used to identify pollutants and contaminants.

- **Analysis of beverages** - pySpectroWorks can be used to analyze the spectral data of beverages such as wine, beer, and juice, which can provide information on their chemical composition and quality.

- **Analysis of oils and fats** - pySpectroWorks can be used to analyze the spectral data of liquid oils and fats, which can provide information on their composition and purity.

- **Analysis of biological fluids** - pySpectroWorks can be used to extract spectral data from biological fluids such as blood, urine, and saliva, which can provide information on disease diagnosis and treatment.