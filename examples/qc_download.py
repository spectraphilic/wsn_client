# Standard Library
import os

# Requirements
import pandas as pd
import requests


HOST = os.getenv('API_HOST', 'https://wsn.latice.eu')
KEY = os.environ['API_KEY'] # This MUST be provided as an environment variable


if __name__ == '__main__':
    # Download the data
    headers = {'Authorization': f'Api-Key {KEY}'}
    response = requests.get(f'{HOST}/api/qc/download/', headers=headers)
    response.raise_for_status()

    # Create dataframes from the data
    data = response.json()
    for node in data['results']:
        print('name={name} lat={lat} lng={lng}'.format(**node))
        df = pd.DataFrame.from_dict(node['data'])
        print(df)
        print()
