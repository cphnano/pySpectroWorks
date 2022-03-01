import json
import requests
from datetime import datetime


class Connection:
    def __init__(self, api_key, url):
        self.api_key = api_key
        self.url = url
        self.projects = None

    def get_projects(self):
        # load projects
        if self.projects is None:
            res = requests.get(self.url + 'list_projects', params={'api_key': self.api_key})
            if res.status_code != 200:
                raise ConnectionError(json.loads(res.text)['message'])
            projects = json.loads(res.text)['message']['items']
            self.projects = [Project(self, project) for project in projects]

        return self.projects


class Project:
    def __init__(self, connection, data=None):
        self.connection = connection
        if data is None:
            data = {}
        self._project_id = data['project_id']
        self.project_name = data.get('project_name', '')
        self.num_files = int(data.get('num_files', 0))
        self.created = float(data.get('created', 0)) / 1000
        self.modified = float(data.get('modified', 0)) / 1000
        self.results = data.get('results', [])
        self.items = None

    def __str__(self):
        timestamp = datetime.utcfromtimestamp(self.created).strftime('%Y-%m-%d %H:%M:%S')
        return f'{self.project_name}   {self.num_files} items   {timestamp}'

    def get_items(self):
        # load items
        def sort_by_created(item):
            return item.created

        if self.items is None:
            conn = self.connection
            res = requests.get(conn.url + 'list_files_by_project',
                               params={'api_key': conn.api_key, 'project_id': int(self._project_id)})
            if res.status_code != 200:
                raise ConnectionError(json.loads(res.text)['message'])
            file_list = json.loads(res.text)['message']['items']

            file_ids = [file['file_id'] for file in file_list]
            res = requests.post(conn.url + 'get_files',
                                params={'api_key': conn.api_key}, data=json.dumps(file_ids))
            if res.status_code != 200:
                raise ConnectionError(json.loads(res.text)['message'])
            items = [Item(self.connection, item, self) for item in json.loads(res.text)['message']['items']]
            self.items = [item for item in items if item.completeness == 100 and not item.hidden]
            self.items.sort(key=sort_by_created)

        return self.items


class Item:
    def __init__(self, connection, data=None, project=None):
        self.connection = connection
        if data is None:
            data = {}
        self._file_id = data['file_id']
        self._project_id = data['project_id']
        self.project = project
        self.created = float(data.get('created', 0)) / 1000
        self.modified = float(data.get('modified', 0)) / 1000
        self.cuvette_idx = int(data.get('cuvette_idx', -1))
        self.box_code = data.get('box_code', None)
        self.completeness = int(data.get('completeness', 0))
        self.hidden = bool(data.get('file_hidden', False))
        self.results = data.get('results', {})

        # add input variables to results
        if self.project:
            for result in self.project.results:
                input_variables = result.get('input_variables', {})
                result_id = result['result_id']
                for key, val in input_variables.items():
                    if not self.results[result_id]:
                        self.results[result_id] = {}
                    self.results[result_id][key] = val

        self.sample_attributes = {}
        sample_attributes = data.get('input_tags', {})
        for key, val in sample_attributes.items():
            self.sample_attributes[key] = val['value']

    def get_spectrum(self, spectrum_type):
        conn = self.connection
        spectrum_names = {
            'reference_a': 'ref_a',
            'reference_b': 'ref',
            'reference_d': 'ref_d',
            'sample_b': 'ri1',
            'sample_d': 'ri2',
            'sample_a': 'abs'
        }
        spectrum_type = spectrum_type.lower()

        if spectrum_type in spectrum_names.keys():
            spectrum_name = spectrum_names[spectrum_type]
            res = requests.get(conn.url + 'get_spectrum',
                               params={'api_key': conn.api_key,
                                       'file_id': int(self._file_id),
                                       'spectrum_types': ['spectrum_'+spectrum_name]})
            if res.status_code != 200:
                raise ConnectionError(json.loads(res.text)['message'])
            return json.loads(res.text)['message']['spectrum_'+spectrum_name]['spectrum']
        raise KeyError('No such spectrum')


def connect(api_key, stage='prod'):
    return Connection(api_key, f'https://api.spectroworks.com/{stage}/api/')
