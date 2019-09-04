import datetime
import os
import pprint

import pandas as pd
import requests


HOST = 'https://wsn.latice.eu'
HOST = 'http://localhost:8000'  # For the developer

# Prepare the session
TOKEN = os.getenv('WSN_TOKEN') # export WSN_TOKEN=xxx
session = requests.Session()
session.headers.update({'Authorization': f'Token {TOKEN}'})


def query(
    db,                  # postgresql or clickhouse
    fields=None,         # Fields to return (all by default)
    tags=None,           # Tags to return (all by default)
    time__gte=None, time__lte=None, # Filter by time range
    limit=100,
    # Use aggregates to reduce the amount of data retrieved
    interval=None,
    interval_agg='avg',
    # Not sent to the API
    format='pandas',     # pandas or json
    verbose=0,
    **kw):

    """
    query('clickhouse', table='', ...) -> dataframe or dict
    query('postgresql', ...) -> dataframe or dict

    Retrieves data from the UiO Django system.

    Selecting data (rows)
    =====================

    First choose the database to pull data from, choices are
    clickhouse (for raw data from finse/mobile flux), and postgresql (for
    everything else). How data is selected depends on the database used.

    ClickHouse:

        query('clickhouse', table='finseflux_Biomet', ...)

    Choices for table are: finseflux_Biomet, finseflux_StationStatus,
    mobileflux_Biomet and mobileflux_StationStatus.

    PostgreSQL:

        query('postgresql', name='eddypro_Finseflux', ...)
        query('postgresql', serial=0x1F566F057C105487, ...)
        query('postgresql', source_addr_long=0x0013A2004105D4B6, ...)

    Data from PostgreSQL can be queried by any metadata information, most often
    the name is all you need.

    Selecting fields (columns)
    ==========================

    If the fields parameter is not given, all the fields will be returned. This
    is only recommended to explore the available columns, because it may be too
    slow and add a lot of work on the servers. So it is recommended to ask only
    for the fields you need, it will be much faster.

    Examples:

        query('clickhouse', table='finseflux_Biomet', fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'], ...)
        query('postgresql', name='eddypro_Finseflux', fields=['co2_flux'], ...)

    The field 'time' is always included, do not specify it. It's a Unix
    timestamp (seconds since the Unix epoch). The rows returned are ordered by
    this field.

    Selecting a time range
    ==========================

    Use the parameters time__gte and/or time__lte to define the time range of
    interest. The smaller the faster the query will run.

    These parameters expect a datetime object. If the timezone is not specified
    it will be interpreted as local time, but it's probably better to
    explicitely use UTC.

    Example:

        query(
            'clickhouse', table='finseflux_Biomet',
            fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
            time__gte=datetime.datetime(2018, 3, 1, tzinfo=datetime.timezone.utc),
            time__lte=datetime.datetime(2018, 4, 1, tzinfo=datetime.timezone.utc),
            ...
        )

    Limiting the number of rows
    ===========================

    The limit parameter defines the maximum number of rows to return. If not
    given all selected rows will be returned.

    Example:

        query(
            'clickhouse', table='finseflux_Biomet',
            fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
            time__gte=datetime.datetime(2018, 3, 1, tzinfo=datetime.timezone.utc),
            time__lte=datetime.datetime(2018, 4, 1, tzinfo=datetime.timezone.utc),
            limit=1000000,
        )

    Aggregates
    ===========================

    Instead of returning every data point, it's possible split the time range
    in intervals and return an aggregate of every field over an interval. This
    can greatly reduce the amount of data returned, speeding up the query.

    For this purpose pass the interval parameter, which defines the interval
    size in seconds. The interval is left-closed and right-open. The time
    column returned is at the beginning of the interval.

    By default the aggregate function used is the average, pass the
    interval_agg to specify a differente function.

    Example (interval size is 5 minutes):

        query(
            'clickhouse', table='finseflux_Biomet',
            fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
            time__gte=datetime.datetime(2018, 3, 1, tzinfo=datetime.timezone.utc),
            time__lte=datetime.datetime(2018, 4, 1, tzinfo=datetime.timezone.utc),
            limit=1000000,
            interval=60*5,
            interval_agg='min',
        )

    If using postgresql the available functions are: avg, count, max, min,
    stddev, sum and variance.

    If using clickhouse any aggregate function supported by ClickHouse can be
    used, see https://clickhouse-docs.readthedocs.io/en/latest/agg_functions/

    Using aggregates requires the fields paramater as well, it doesn't work
    when asking for all the fields.

    Tags (PostgreSQL only)
    ===========================

    With PostgreSQL only, you can pass the tags parameter to add metadata
    information to every row.

    Example:

        query(
            'postgresql', name='fw-001',
            fields=['latitude', 'longitude'],
            tags=['serial'],
        )

    In this example, the data from fw-001 may actually come from different
    devices, maybe the device was replaced at some point. Using the tags
    parameter we can add a column with the serial number of the devices.

    Tags don't work with aggregated values.

    Returns
    ===========================

    This function returns by default a Pandas dataframe. Use format='json' to
    return instead a Python dictionary, with the data as was sent by the server.

    Debugging
    ===========================

    Using the verbose parameter this function will print some information, useful
    for debugging. Possible values are: 0 (default), 1 and 2.
    """

    url = HOST + f'/api/query/{db}/'

    # Parameters
    if time__gte:
        time__gte = int(time__gte.timestamp())
    if time__lte:
        time__lte = int(time__lte.timestamp())

    params = {
        'limit': limit,                                 # Pagination
        'time__gte': time__gte, 'time__lte': time__lte, # Time filter
        'fields': fields,
        'tags': tags,
        'interval': interval,
    }

    # Filter inside json
    for key, value in kw.items():
        if value is None:
            params[key] = None
            continue

        if type(value) is datetime.datetime:
            value = int(value.timestamp())

        if isinstance(value, int):
            key += ':int'

        params[key] = value

    # Query
    response = session.get(url, params=params)
    response.raise_for_status()
    json = response.json()

    # Debug
    if verbose > 0:
        print(db)
        pprint.pprint(params)
        if verbose > 1:
            pprint.pprint(json)
        print()

    if format == 'json':
        return json

    if format == 'pandas':
        if json['format'] == 'sparse':
            df = pd.io.json.json_normalize(json['rows'])
        else:
            df = pd.DataFrame(json['rows'], columns=json['columns'])

        #try:
        #    df.time = pd.to_datetime(df.time, unit='s')
        #except:
        #    print('WARNING: no timestamp')

        if verbose > 0:
            print(df)

        return df


if __name__ == '__main__':
    # Number of elements to return in every query
    limit = 2


    #
    # Return all the columns, usefult to know which columns exist
    #

    print('==============================================')
    response = query(
        'postgresql', name='LATICE-Flux Finse',
        limit=1,
        verbose=1,
    )

#   print('==============================================')
#   response = query(
#       'clickhouse', table='finseflux_Biomet',
#       limit=1,
#       verbose=1,
#   )

#   #
#   # Select a coupe of columns withing a time range
#   #

#   print('==============================================')
#   response = query(
#       'postgresql', name='LATICE-Flux Finse',
#       fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
#       time__gte=datetime.datetime(2018, 3, 1, tzinfo=datetime.timezone.utc),
#       time__lte=datetime.datetime(2018, 4, 1, tzinfo=datetime.timezone.utc),
#       limit=limit,
#       verbose=1,
#       #format='json',
#   )

#   print('==============================================')
#   response = query(
#       'clickhouse', table='finseflux_Biomet',
#       fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
#       time__gte=datetime.datetime(2018, 3, 1, tzinfo=datetime.timezone.utc),
#       time__lte=datetime.datetime(2018, 4, 1, tzinfo=datetime.timezone.utc),
#       limit=limit,
#       verbose=1,
#       #format='json',
#   )

#   #
#   # Select the average value in 1h intervals
#   #

#   print('==============================================')
#   response = query(
#       'postgresql', name='LATICE-Flux Finse',
#       fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
#       time__gte=datetime.datetime(2018, 3, 1, tzinfo=datetime.timezone.utc),
#       time__lte=datetime.datetime(2018, 4, 1, tzinfo=datetime.timezone.utc),
#       limit=limit,
#       interval=3600,
#       verbose=1,
#   )

#   print('==============================================')
#   response = query(
#       'clickhouse', table='finseflux_Biomet',
#       fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
#       time__gte=datetime.datetime(2018, 3, 1, tzinfo=datetime.timezone.utc),
#       time__lte=datetime.datetime(2018, 4, 1, tzinfo=datetime.timezone.utc),
#       limit=limit,
#       interval=3600,
#       verbose=1,
#   )

#   #
#   # Use a different aggregate
#   #

#   print('==============================================')
#   response = query(
#       'postgresql', name='LATICE-Flux Finse',
#       fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
#       time__gte=datetime.datetime(2018, 3, 1, tzinfo=datetime.timezone.utc),
#       time__lte=datetime.datetime(2018, 4, 1, tzinfo=datetime.timezone.utc),
#       limit=limit,
#       interval=3600,
#       interval_agg='min',
#       verbose=1,
#   )

#   print('==============================================')
#   response = query(
#       'clickhouse', table='finseflux_Biomet',
#       fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
#       time__gte=datetime.datetime(2018, 3, 1, tzinfo=datetime.timezone.utc),
#       time__lte=datetime.datetime(2018, 4, 1, tzinfo=datetime.timezone.utc),
#       limit=limit,
#       interval=3600,
#       interval_agg='min',
#       verbose=1,
#   )

    #
    # Specific to PostgreSQL, return tags
    #

#   print('==============================================')
#   response = query(
#       'postgresql',
#       fields=['bat', 'in_temp'],
#       tags=['serial'],
#       limit=limit,
#       verbose=1,
#   )
