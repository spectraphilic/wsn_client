# Standard Library
import datetime
import os

# Requirements
import pandas as pd
import requests


HOST = os.getenv('API_HOST', 'https://wsn.latice.eu')
KEY = os.environ['API_KEY'] # This MUST be provided as an environment variable

if __name__ == '__main__':
    # These may be input to the program
    name = 'sw-001'
    since = datetime.datetime(2020, 1, 1)
    until = datetime.datetime(2021, 1, 1)

    # Variables
    headers = {'Authorization': f'Api-Key {KEY}'}
    url = f'{HOST}/api/qc/download/{name}/'

    # Filter by time range (optional)
    since = int(since.timestamp())
    until = int(until.timestamp())
    url = f'{url}?time__gte={since}&time__lt={until}'

    # Download the data
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Create dataframe from the data
    data = response.json()
    df = pd.DataFrame.from_dict(data)
    print(df)
    print()
