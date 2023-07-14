import json
import requests
from datetime import datetime
from typing import Dict, List, Tuple
from math import sqrt


class Connection:
    def __init__(self, api_key: str, url: str):
        """
        Initializes Connection object.
        :param api_key: str, API key for the connection.
        :param url: str, URL of the connection.
        """
        self.api_key = api_key
        self.url = url
        self.projects = None

    def get_projects(self) -> list:
        """
        Returns a list of projects.
        :return: list of Project objects.
        """
        # load projects
        if self.projects is None:
            res = requests.get(self.url + 'list_projects', params={'api_key': self.api_key})
            if res.status_code != 200:
                raise ConnectionError(json.loads(res.text)['message'])
            projects = json.loads(res.text)['message']['items']
            self.projects = [Project(self, project) for project in projects]

        return self.projects


class Project:
    def __init__(self, connection: Connection, data: dict = None):
        """
        Initializes Project object.
        :param connection: Connection object.
        :param data: dict, data for the project.
        """
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

    def __str__(self) -> str:
        """
        Returns a string representation of the project.
        :return: str, string representation of the project.
        """
        timestamp = datetime.utcfromtimestamp(self.created).strftime('%Y-%m-%d %H:%M:%S')
        return f'{self.project_name}   {self.num_files} items   {timestamp}'

    def get_items(self) -> list:
        """
        Returns a list of items.
        :return: list of Item objects.
        """
        # load items
        def sort_by_created(item: Item) -> float:
            return item.created

        if self.items is None:
            conn = self.connection
            res = requests.get(conn.url + 'list_files_by_project',
                               params={'api_key': conn.api_key,
                                       'project_id': int(self._project_id),
                                       'max_files': 1000})
            data = json.loads(res.text)['message']
            if res.status_code != 200:
                raise ConnectionError(data)
            file_list = data['items']

            while 'last_key' in data.keys():
                last_key = int(data['last_key'])
                res = requests.get(conn.url + 'list_files_by_project',
                                   params={'api_key': conn.api_key,
                                           'project_id': int(self._project_id),
                                           'max_files': 1000,
                                           'last_key': last_key})
                data = json.loads(res.text)['message']
                if res.status_code != 200:
                    raise ConnectionError(data)
                file_list.extend(data['items'])

            file_ids = [file['file_id'] for file in file_list]
            res = requests.post(conn.url + 'get_files',
                                params={'api_key': conn.api_key}, data=json.dumps(file_ids))

            data = json.loads(res.text)['message']
            if res.status_code != 200:
                raise ConnectionError(data)

            items = data['items']

            while data['unprocessed']:
                file_ids = data['unprocessed']
                res = requests.post(conn.url + 'get_files',
                                    params={'api_key': conn.api_key}, data=json.dumps(file_ids))

                data = json.loads(res.text)['message']
                if res.status_code != 200:
                    raise ConnectionError(data)
                items.extend(data['items'])

            items = [Item(self.connection, item, self) for item in items]
            self.items = [item for item in items if item.completeness == 100 and not item.hidden]
            self.items.sort(key=sort_by_created)

        return self.items


class Item:
    def __init__(self, connection: 'Connection', data: Dict = None, project: 'Project' = None):
        """
        Item class constructor.
        Args:
            connection: A Connection object.
            data: A dictionary containing data about the item.
            project: A Project object, if the item is associated with a project.
        """
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
        self.user_note = data.get('user_note', '')
        self.reference_name = data.get('ref_name', '')
        self.reference_ri = self.c1_to_n(data.get('ref_c1', 0.0))

        # get size distribution result and convert to nm, %
        size_dist_res = data.get('size_distribution_result', {})
        radii = size_dist_res.get('radii', [])
        vol = size_dist_res.get('size_distribution_vol', [])
        dia_nm = [r * 2 * (10 ** 9) for r in radii]
        vol_pct = [v * 100 for v in vol]
        self.size_distribution = list(zip(dia_nm, vol_pct))

        # add input variables to results
        if self.project:
            for result in self.project.results:
                result_id = result['result_id']
                self.results[result_id] = self.results.get(result_id, {})  # use empty dict for results not in item
                if 'input_variables' not in result.keys():
                    continue
                for key, val in result['input_variables'].items():
                    self.results[result_id][key] = val

        self.sample_attributes = {}
        sample_attributes = data.get('input_tags', {})
        for key, val in sample_attributes.items():
            self.sample_attributes[key] = val['value']

    @staticmethod
    def c1_to_n(c1):
        n_water = 1.3332153809611258
        pmt_water = n_water ** 2
        pmt = 1 + (pmt_water - 1) * c1
        return sqrt(pmt)

    def __repr__(self):
        d = {
            'file_id': self._file_id,
            'project_id': self._project_id,
            'created': self.created,
            'modified': self.modified,
            'cuvette_idx': self.cuvette_idx,
            'box_code': self.box_code,
            'results': self.results,
            'sample_attributes': self.sample_attributes,
            'user_note': self.user_note,
            'reference_name': self.reference_name,
            'reference_ri': self.reference_ri
        }
        return str(d)

    def get_size_distribution(self) -> List[Tuple[float, float]]:
        """
        Returns the size distribution data for the item.
        """
        return self.size_distribution

    def get_spectrum(self, spectrum_type: str) -> List[float]:
        """
        Returns the spectrum data for the item.
        Args:
            spectrum_type: A string representing the type of spectrum to retrieve.
        Raises:
            KeyError: If the spectrum type is not recognized.
            ConnectionError: If the request to retrieve the spectrum fails.
        """
        conn = self.connection
        spectrum_names = {
            'reference_a': 'ref_a',
            'reference_b': 'ref',
            'reference_d': 'ref_d',
            'sample_b': 'ri1',
            'sample_d': 'ri2',
            'sample_a': 'abs'
        }
        simulated_spectrum_names = {
            'reference_b_model': 'ref',
            'sample_b_model': 'sample',
            'sample_d_model': 'ri2',
            'sample_a_model': 'abs'
        }
        spectrum_type = spectrum_type.lower()

        if spectrum_type in spectrum_names.keys():
            spectrum_name = spectrum_names[spectrum_type]
            res = requests.get(conn.url + 'get_spectrum',
                               params={'api_key': conn.api_key,
                                       'file_id': int(self._file_id),
                                       'spectrum_types': ['spectrum_'+spectrum_name]})
            data = json.loads(res.text)['message']
            if res.status_code != 200:
                raise ConnectionError(data)
            return data['spectrum_'+spectrum_name]['spectrum']

        if spectrum_type in simulated_spectrum_names.keys():
            spectrum_name = simulated_spectrum_names[spectrum_type]
            res = requests.get(conn.url + 'get_simulated_spectrum',
                               params={'api_key': conn.api_key,
                                       'file_id': int(self._file_id),
                                       'spectrum_types': [spectrum_name]})
            data = json.loads(res.text)['message']
            if res.status_code != 200:
                raise ConnectionError(data)
            return data[spectrum_name]['spectrum']

        raise KeyError('No such spectrum')


def connect(api_key: str, stage: str = 'prod') -> Connection:
    """Connect to Spectroworks API using API key and stage.

    Args:
        api_key (str): API key for the Spectroworks API.
        stage (str, optional): Stage of the API. Defaults to 'prod'.

    Returns:
        Connection: A Connection object that can be used to interact with the API.
    """
    return Connection(api_key, f'https://api.spectroworks.com/{stage}/api/')

