# Standard Library
import copy
import datetime
import json
import os
import pprint

# Requirements
import pandas as pd
import requests


HOST = os.getenv('API_HOST', 'https://wsn.latice.eu')
KEY = os.environ['API_KEY'] # This MUST be provided as an environment variable

# Input data
NAME = 'test'
RECORDS = [
    {
        'time': '2019-04-06 15:00:00',
        'temperature': 22.6875, 'temperature_qc': False,
        'humidity': 12.080078125, 'humidity_qc': False,
        'air_pressure': 103088.1640625, 'air_pressure_qc': False,
        'snow_depth': 2165.0, 'snow_depth_qc': False,
    },
    {
        'time': '2019-04-06 15:10:00',
        'temperature': 22.875, 'temperature_qc': False,
        'humidity': 11.994140625, 'humidity_qc': False,
        'air_pressure': 103092.3125, 'air_pressure_qc': False,
        'snow_depth': 1203.0, 'snow_depth_qc': False,
    },
    {
        'time': '2019-04-06 15:20:00',
        'temperature': 23.4375, 'temperature_qc': False,
        'humidity': 10.7353515625, 'humidity_qc': False,
        'air_pressure': 103091.2421875, 'air_pressure_qc': False,
        'snow_depth': 1910.0, 'snow_depth_qc': False,
    },
]


def get_records():
    records = copy.deepcopy(RECORDS)
    for row in records:
        dt = datetime.datetime.strptime(row['time'], '%Y-%m-%d %H:%M:%S')
        row['time'] = int(dt.timestamp())

    return records


if __name__ == '__main__':
    # Build the dataframe
    records = get_records()
    df = pd.DataFrame.from_records(records)
    print('\nTHIS IS THE DATAFRAME:')
    print(df)

    # Output the dataframe as JSON records
    data = df.to_dict(orient='records')
    data = [{
        'name': NAME,
        'data': data,
    }]
    print('\nTHIS IS THE DATA THAT WILL BE SENT:')
    pprint.pprint(data)

    # Upload the data
    headers = {'Authorization': f'Api-Key {KEY}'}
    response = requests.post(f'{HOST}/api/qc/upload/', json=data, headers=headers)
    response.raise_for_status()
    print('\nTHIS IS THE RESPONSE FROM THE SERVER:')
    pprint.pprint(response.json())
