import os
import requests
import json
import pandas as pd
from typing import Union


class Brynq:
    def __init__(self, subdomain: str = None, api_token: str = None, staging: str = 'prod'):
        self.subdomain = os.getenv("BRYNQ_SUBDOMAIN", subdomain)
        self.api_token = os.getenv("BRYNQ_API_TOKEN", api_token)
        self.environment = os.getenv("BRYNQ_ENVIRONMENT", staging)

        if any([self.subdomain is None, self.api_token is None]):
            raise ValueError("Set the subdomain, api_token either in your .env file or provide the subdomain and api_token parameters")

        possible_environments = ['dev', 'prod']
        if self.environment not in possible_environments:
            raise ValueError(f"Environment should be in {','.join(possible_environments)}")

        self.url = 'https://app.brynq-staging.com/api/v2/' if self.environment == 'dev' else 'https://app.brynq.com/api/v2/'

    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self.api_token}',
            'Domain': self.subdomain
        }

    def _get_mappings(self, task_id: int) -> dict:
        """
        Get the mappings from the task in BrynQ
        :param task_id: The id of the task in BrynQ. this does not have to be the task id of the current task
        :return: A dictionary with the following structure: {mapping_title: {tuple(input): output}}
        """
        response = requests.get(url=f'{self.url}interfaces/{task_id}/data-mapping', headers=self._get_headers())

        if response.status_code != 200:
            raise ValueError(f'Error occurred while fetching mappings: {response.text}. Please always check if you have added BRYNQ_SUBDOMAIN to your .env file')

        return response.json()

    def get_mapping(self, task_id: int, mapping: str, multiple_values: str = 'raise'):
        """
        Get the mapping json from the mappings
        :param task_id: The id of the task in BrynQ. this does not have to be the task id of the current task
        :param mapping: The name of the mapping
        :param multiple_values: A string to indicate how to handle multiple input or output values. Options are 'raise' and 'concat'
        :return: The json of the mapping
        """
        # Find the mapping for the given sheet name
        mappings = self._get_mappings(task_id=task_id)
        mapping_data = next((item for item in mappings if item['name'] == mapping), None)
        if not mapping_data:
            raise ValueError(f"Mapping named '{mapping}' not found")

        result_mapping = {}
        for value in mapping_data['values']:
            if multiple_values == 'raise' and (len(value['input'].items()) > 1 or len(value['output'].items()) > 1):
                raise ValueError("Multiple input or output keys found when 'raise' strategy is specified.")

            input_values = []
            output_values = []
            for _, val in value['input'].items():
                input_values.append(val)
            for _, val in value['output'].items():
                output_values.append(val)

            if multiple_values == 'concat':
                concatenated_input = ','.join(input_values)
                concatenated_output = ','.join(output_values)
                result_mapping[concatenated_input] = concatenated_output
            else:  # Default to assuming there's only one key-value pair if not concatenating
                result_mapping[input_values[0]] = output_values[0]

        return result_mapping

    def get_mapping_as_dataframe(self, task_id: int, mapping: str, prefix: bool = False):
        """
        Get the mapping dataframe from the mappings
        :param mapping: The name of the mapping
        :param prefix: A boolean to indicate if the keys should be prefixed with 'input.' and 'output.'
        :return: The dataframe of the mapping
        """
        # Find the mapping for the given sheet name
        mappings = self._get_mappings(task_id=task_id)
        mapping_data = next((item for item in mappings if item['name'] == mapping), None)
        if not mapping_data:
            raise ValueError(f"Mapping named '{mapping}' not found")

        # Extract the values which contain the input-output mappings
        values = mapping_data['values']

        # Create a list to hold all row data
        rows = []
        for value in values:
            # Check if prefix is needed and adjust keys accordingly
            if prefix:
                input_data = {f'input.{key}': val for key, val in value['input'].items()}
                output_data = {f'output.{key}': val for key, val in value['output'].items()}
            else:
                input_data = value['input']
                output_data = value['output']

            # Combine 'input' and 'output' dictionaries
            row_data = {**input_data, **output_data}
            rows.append(row_data)

        # Create DataFrame from rows
        df = pd.DataFrame(rows)

        return df

    def get_system_credential(self, system: str, label: Union[str, list], test_environment: bool = False) -> json:
        """
        This method retrieves authentication credentials from BrynQ.
        It returns the json data if the request does not return an error code
        :param system: specifies which token is used. (lowercase)
        :param label: reference to the used label
        :param test_environment: boolean if the test environment is used
        :return json response from BrynQ
        """
        response = requests.get(url=f'{self.url}apps/{system}', headers=self._get_headers())
        response.raise_for_status()
        credentials = response.json()
        # rename parameter for readability
        if isinstance(label, str):
            labels = [label]
        else:
            labels = label
        # filter credentials based on label. All labels specified in label parameter should be present in the credential object
        credentials = [credential for credential in credentials if all(label in credential['labels'] for label in labels)]
        if system == 'profit':
            credentials = [credential for credential in credentials if credential['isTestEnvironment'] is test_environment]

        if len(credentials) == 0:
            raise ValueError(f'No credentials found for {system}')
        if len(credentials) != 1:
            raise ValueError(f'Multiple credentials found for {system} with the specified labels')

        return credentials[0]

    def refresh_system_credential(self, system: str, system_id: int) -> json:
        """
        This method refreshes Oauth authentication credentials in BrynQ.
        It returns the json data if the request does not return an error code
        :param system: specifies which token is used. (lowercase)
        :param system_id: system id in BrynQ
        :return json response from BrynQ
        """
        response = requests.post(url=f'{self.url}apps/{system}/{system_id}/refresh', headers=self._get_headers())
        response.raise_for_status()
        credentials = response.json()

        return credentials

    def get_user_data(self):
        """
        Get all users from BrynQ
        :return: A list of users
        """
        return requests.get(url=f'{self.url}users', headers=self._get_headers())

    def get_user_authorization_qlik_app(self,dashboard_id):
        """
        Get all users from BrynQ who have access to a qlik dashboard with their entities
        :return: A list of users and entities
        """
        return requests.get(url=f'{self.url}/qlik/{dashboard_id}/users', headers=self._get_headers())

    def get_role_data(self):
        """
        Get all roles from BrynQ
        :return: A list of roles
        """
        return requests.get(url=f'{self.url}roles', headers=self._get_headers())

    def create_user(self, user_data: dict) -> requests.Response:
        """
        Create a user in BrynQ
        :param user_data: A dictionary with the following structure:
        {
            "name": "string",
            "username": "string",
            "email": "string",
            "language": "string",
            "salure_connect": bool,
            "qlik_sense_analyzer": bool,
            "qlik_sense_professional": bool
        }
        :return: A response object
        """
        data = {
            "name": user_data['name'],
            "username": user_data['username'],
            "email": user_data['email'],
            "language": user_data['language'],
            "products": {
                "qlikSenseAnalyzer": user_data['qlik_sense_analyzer'],
                "qlikSenseProfessional": user_data['qlik_sense_professional']
            }
        }

        return requests.post(url=f'{self.url}users', headers=self._get_headers(), json=data)

    def update_user(self, user_id: str, user_data: dict) -> requests.Response:
        """
        Update a user in BrynQ
        :param user_id: The id of the user in BrynQ
        :param user_data: A dictionary with the following structure:
        {
            "id": "string",
            "name": "string",
            "language": "string",
            "salureconnect": bool,
            "qlik sense analyser": bool,
            "qlik sense professional": false
        }
        :return: A response object
        """
        data = {
            "name": user_data['name'],
            "username": user_data['username'],
            "email": user_data['email'],
            "language": user_data['language'],
            "products": {
                "qlikSenseAnalyzer": user_data['qlik_sense_analyzer'],
                "qlikSenseProfessional": user_data['qlik_sense_professional']
            }
        }

        return requests.put(url=f'{self.url}users/{user_id}', headers=self._get_headers(), json=data)

    def delete_user(self, user_id: str) -> requests.Response:
        """
        Delete a user in BrynQ
        :param user_id: The id of the user in BrynQ
        :return: A response object
        """
        return requests.delete(url=f'{self.url}users/{user_id}', headers=self._get_headers())

    def overwrite_user_roles(self, user_id: int, roles: list) -> requests.Response:
        """
        Overwrite the roles of a user in BrynQ
        :param user_id: The id of the user in BrynQ
        :param roles: A list of role ids
        :return: A response object
        """
        data = {
            "roles": roles
        }

        return requests.put(url=f'{self.url}users/{user_id}/roles', headers=self._get_headers(), json=data)

    def get_source_system_entities(self, system: str) -> requests.Response:
        """
        Get all entities from a source system in BrynQ
        :param system: The name of the source system
        :return: A response object
        """
        return requests.get(url=f'{self.url}source-systems/{system}/entities', headers=self._get_headers())

    def get_layers(self) -> requests.Response:
        """
        Get all layers from a source system in BrynQ
        :return: A response object
        """
        return requests.get(url=f'{self.url}organization-chart/layers', headers=self._get_headers())
