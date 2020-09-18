import json
import requests


class Connection:
    def __init__(self, api_key, url):
        self.api_key = api_key
        self.url = url
        self.projects = None

    def get_projects(self):
        # load projects
        if self.projects is None:
            res = requests.get(self.url + 'list_projects', params={'api_key': self.api_key})
            projects = json.loads(res.text)['message']['items']
            self.projects = [Project(self, project) for project in projects]

        return self.projects


class Project:
    def __init__(self, connection, data=None):
        self.connection = connection
        if data is None:
            data = {}
        self.data = data
        self.project_name = data.get('project_name', '')
        self.num_files = int(data.get('num_files', 0))
        self.created = float(data.get('created', 0))
        self.modified = float(data.get('modified', 0))
        self.items = None

    def get_items(self):
        # load items
        def sort_by_created(item):
            return item.created

        if self.items is None:
            conn = self.connection
            res = requests.get(conn.url + 'list_files_by_project',
                               params={'api_key': conn.api_key, 'project_id': int(self.data['project_id'])})
            file_list = json.loads(res.text)['message']['items']

            file_ids = [file['file_id'] for file in file_list]
            res = requests.post(conn.url + 'get_files',
                                params={'api_key': conn.api_key}, data=json.dumps(file_ids))
            items = [Item(self.connection, item) for item in json.loads(res.text)['message']['items']]
            self.items = [item for item in items if item.completeness == 100]
            self.items.sort(key=sort_by_created)

        return self.items


class Item:
    def __init__(self, connection, data=None):
        self.connection = connection
        if data is None:
            data = {}
        self.data = data
        self.created = float(data.get('created', 0))
        self.modified = float(data.get('modified', 0))
        self.cuvette_idx = int(data.get('cuvette_idx', 0))
        self.box_code = data.get('box_code', 'XXXXXX')
        self.completeness = int(data.get('completeness', 0))
        self.results = data.get('results', {})

    def get_spectrum(self, spectrum_type):
        spectrum_names = {
            'reference_b': 'ref',
            'sample_b': 'ri1',
            'sample_d': 'ri2',
            'sample_a': 'abs'
        }
        spectrum_name = spectrum_names[spectrum_type.lower()]
        conn = self.connection
        res = requests.get(conn.url + 'get_spectrum',
                           params={'api_key': conn.api_key,
                                   'file_id': int(self.data['file_id']),
                                   'spectrum_types': ['spectrum_'+spectrum_name]})
        return json.loads(res.text)['message']['spectrum_'+spectrum_name]['spectrum']


def connect(api_key):
    return Connection(api_key, 'https://api.spectroworks.com/prod/api/')

