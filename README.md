# pySpectroWorks

Python module for loading data from SpectroWorks™.

## How does it work?
An example script can be found in [api_test.py](api_test.py)

The pySpectroWorks module is divided into 3 classes: 
 - Connection
 - Project
 - Item
 
 You must first establish a connection by using your API key. An API key can be generated from you "profile" page in SpectroWorks™.
```
import pyspectroworks
conn = pyspectroworks.connect('INSERT_API_KEY_HERE')
```

Once you have a connection instance you can extract all your projects as a list:
```
projects = conn.get_projects()
```

Each element in this list is a Project object. All data about a project is found in its 'data' attribute, however, the most useful information has its own attributes:
 - project_name (name of project)
 - num_files (number of items in project)
 - created (unix timestamp of when this project was created)
 - modified (unix timestamp of when this project was last modified)
 
 Each project can include several items. These are your experiments and can be extracted with the _get_items_ method.
 ```
project = projects[0] # get first project
items = project.get_items() # get all items in project
```

Like projects, items include a multitude of different data which can be accessed by the items 'data' attribute. 
The box code and cuvette number can be found in the 'box_code' and 'cuvette_idx' attributes. 
Calculated results are available in the items 'results' attribute.

 ```
item = items[0] # get first item
ri = item.results['refractive_index']['value'] # get the refractive index
# print cuvette and refractive index
print('Cuvette: {: >6}{:0>2}, Refractive Index: {: >8}'.format(item.box_code, item.cuvette_idx, ri))
```

If you want to extract the spectral data then you can use the _get_spectrum_ method of the item.  
The available spectrum types are:
 - 'reference_B' (B side reference spectrum)
 - 'sample_A' (A side sample spectrum)
 - 'sample_B' (B side sample spectrum)
 - 'sample_D':(D side sample spectrum)
 
```
spectrum = item.get_spectrum('sample_B')
```

The spectrum is a list consisting of pairs of wavelengths and attenuance values. 