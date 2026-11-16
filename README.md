# pySpectroWorks

[![PyPI](https://img.shields.io/pypi/v/pyspectroworks)](https://pypi.org/project/pyspectroworks/)
[![Python](https://img.shields.io/pypi/pyversions/pyspectroworks)](https://pypi.org/project/pyspectroworks/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

pySpectroWorks is a Python module for loading your data from SpectroWorks™:
projects, measurements, calculated results and spectra.

## Contents

- [Installation](#installation)
- [Quick start](#quick-start)
- [Projects](#projects)
- [Items](#items)
- [Results](#results)
- [Spectra](#spectra)
- [Size distribution](#size-distribution)
- [Good to know](#good-to-know)
- [Examples](#examples)
- [Applications](#applications)

## Installation

```sh
pip install pyspectroworks requests
```

Requires Python 3.7 or newer.

## Quick start

You need an API key. Create one in SpectroWorks™ on your profile page, under
**Access Tokens**.

```python
import pyspectroworks

conn = pyspectroworks.connect("INSERT_API_KEY_HERE")

for project in conn.get_projects():
    print(project)

project = conn.get_projects()[0]
for item in project.get_items():
    ri = item.results.get("refractive_index", {}).get("value", "N/A")
    print(f"Cuvette: {item.box_code}{item.cuvette_idx:0>2}, Refractive Index: {ri}")
```

## Projects

`conn.get_projects()` returns all your projects as a list of `Project` objects.

| Attribute | Content |
| --- | --- |
| `project_name` | Name of the project |
| `num_files` | Number of items in the project |
| `created` | When the project was created, as a Unix timestamp in seconds |
| `modified` | When the project was last modified, as a Unix timestamp in seconds |
| `results` | List of the results set up in this project |

```python
from datetime import datetime

project = conn.get_projects()[0]
print("Project name:", project.project_name)
print("Number of items:", project.num_files)
print("Created:", datetime.fromtimestamp(project.created))
```

## Items

Each project holds a number of items. These are your measurements.
`project.get_items()` returns them as a list of `Item` objects, oldest first.

| Attribute | Content |
| --- | --- |
| `box_code`, `cuvette_idx` | Box code and cuvette number of the cuvette used |
| `created`, `modified` | Unix timestamps in seconds |
| `results` | Calculated results, see [Results](#results) |
| `sample_attributes` | The sample attributes entered for this item, as a dictionary of name and value |
| `user_note` | The note written on the item |
| `reference_name` | Name of the reference used |
| `reference_ri` | Refractive index of the reference |

```python
items = project.get_items()
item = items[0]
print(item)  # prints all of the above
```

## Results

`item.results` is a dictionary. The key is the result name, and the value is a
dictionary with the result `value` and `unit`.

```python
ri = item.results["refractive_index"]["value"]
```

**Note**: The result name is the internal name, not the one shown in the
SpectroWorks™ web interface. For example "Refractive Index" is
`refractive_index` and "° Brix" is `convert_to_brix`. Print
`item.results.keys()` to see the names in your project.

**Note**: Not every result is available in every item. This happens when a
result is added to the project after the item was created. The entry is then
an empty dictionary, so use `.get("value")` when you loop over many items.

## Spectra

`item.get_spectrum(spectrum_type)` returns a spectrum as a list of pairs of
wavelength (nm) and attenuance (absorbance units).

```python
spectrum = item.get_spectrum("sample_B")
```

A spectrum is identified by whether it is a reference or a sample, and by which
side of the cuvette faced the light source:

- **Side A** is either of the sides perpendicular to the side with the optical
  filter, arrow mark and cuvette number. Basic cuvettes only use side A.
- **Side B** is the side with the optical filter, arrow mark and cuvette number.
- **Side D** is the side opposite to side B.

Add `_model` to get the simulated spectrum used by the analysis model.

| Spectrum type | Measured | Simulated |
| --- | --- | --- |
| Reference, side A | `reference_A` | |
| Reference, side B | `reference_B` | `reference_B_model` |
| Reference, side D | `reference_D` | |
| Sample, side A | `sample_A` | `sample_A_model` |
| Sample, side B | `sample_B` | `sample_B_model` |
| Sample, side D | `sample_D` | `sample_D_model` |

The spectrum type is not case sensitive. An unknown type raises `KeyError`.

## Size distribution

For items with a particle size analysis, `item.get_size_distribution()` returns
a list of pairs of particle diameter (nm) and volume (%). The list is empty
when the item has no size distribution.

## Good to know

- `get_items()` only returns items that are complete and not hidden.
- Projects and items are loaded once and then kept. To see new data, create a
  new connection with `pyspectroworks.connect()`.
- When SpectroWorks™ rejects a request, for example because the API key is
  wrong, a `ConnectionError` is raised with the message from the server.

## Examples

- [pyspectroworks_example.py](pyspectroworks_example.py): lists projects, items
  and one spectrum.
- [Demo-education.ipynb](Demo-education.ipynb): a Jupyter notebook that also
  plots spectra.

## Applications

- **Analysis of water quality** - pySpectroWorks can be used to extract spectral data from water samples, which can be used to identify pollutants and contaminants.

- **Analysis of beverages** - pySpectroWorks can be used to analyze the spectral data of beverages such as wine, beer, and juice, which can provide information on their chemical composition and quality.

- **Analysis of oils and fats** - pySpectroWorks can be used to analyze the spectral data of liquid oils and fats, which can provide information on their composition and purity.

- **Analysis of biological fluids** - pySpectroWorks can be used to extract spectral data from biological fluids such as blood, urine, and saliva, which can provide information on disease diagnosis and treatment.
