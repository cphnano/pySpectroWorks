import pyspectroworks
from datetime import datetime

conn = pyspectroworks.connect('INSERT_API_KEY_HERE')  # change this to match your API key

# list projects
print('PROJECTS: ')
print('{: >3} {: >24} {: >24}'.format(' ', 'NAME', 'CREATED'))
projects = conn.get_projects()
for i, project in enumerate(projects):
    timestamp = datetime.utcfromtimestamp(project.created/1000).strftime('%Y-%m-%d %H:%M:%S')
    print('{: >3} {: >24} {: >24} '.format(i, project.project_name, timestamp))

project = projects[0]
print('\n\nOPENING PROJECT "{}":'.format(project.project_name))
# load all files in project
print('{: >6}{: >2}\t{: >8}'.format('CUVETTE', ' ', 'REFRACTIVE INDEX'))
items = project.get_items()
for item in items:
    res = item.results.get('refractive_index', {})
    ri = res.get('value', 'N/A')
    print('{: >6}{:0>2}\t{: >8}'.format(item.box_code, item.cuvette_idx, ri))

# get spectrum of a particular item
print('\n\nLOADING SPECTRUM: ')
item = items[0]
spectrum = item.get_spectrum('sample_B')
print(spectrum)
