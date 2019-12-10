import datetime
import os
import time

import pandas as pd
import requests


HOST = 'https://wsn.latice.eu'
#HOST = 'http://localhost:8000'  # For the developer

# Prepare the session
TOKEN = os.getenv('WSN_TOKEN') # export WSN_TOKEN=xxx
session = requests.Session()
session.headers.update({'Authorization': f'Token {TOKEN}'})


def query(
    db,                                # postgresql or clickhouse
    table=None,                        # clickhouse table name
    fields=None,                       # Fields to return: all by default
    tags=None,                         # postgresql metadata fields (none by default)
    time__gte=None, time__lte=None,    # Time range
    limit=100,                         # Limit
    interval=None, interval_agg=None,  # Aggregates
    format='pandas',                   # pandas or json
    time_index=True,                   # return pandas dataframe with time as index. Only valid if format 'pandas' is selected
    debug=False,
    **kw                               # postgresql filters (name, serial, ...)
    ):

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

    Intervals and aggregates
    ===========================

    Instead of returning every data point, it's possible split the time range
    in intervals and return only one row per interval. This can greatly reduce
    the amount of data returned, speeding up the query.

    For this purpose pass the interval parameter, which defines the interval
    size in seconds. The interval is left-closed and right-open.

    By default the first row found within the interval will be returned. The
    time column will be that of the first row. For example, if the interval
    is 1 hour and the first row is at :05 then the time column will be :05

    If the interval_agg parameter is passed, then an aggregate for every
    column within the interval will be returned. The time column will be
    the beginning of the interval. For example if the interval is 1h, the
    time column will be :00

    Example (interval size is 5 minutes):

        query(
            'clickhouse', table='finseflux_Biomet',
            fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
            time__gte=datetime.datetime(2018, 3, 1, tzinfo=datetime.timezone.utc),
            time__lte=datetime.datetime(2018, 4, 1, tzinfo=datetime.timezone.utc),
            limit=1000000,
            interval=60*5,
            interval_agg='avg',
        )

    If using postgresql the available functions are: avg, count, max, min,
    stddev, sum and variance.

    If using clickhouse any aggregate function supported by ClickHouse can be
    used, see https://clickhouse-docs.readthedocs.io/en/latest/agg_functions/

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

    With debug=True this function will print some information, useful for
    testing. Default is False.
    """

    t0 = time.perf_counter()

    url = HOST + f'/api/query/{db}/'

    # Parameters
    if time__gte:
        time__gte = int(time__gte.timestamp())
    if time__lte:
        time__lte = int(time__lte.timestamp())

    if interval_agg == 'mean':
        interval_agg = 'avg'

    params = {
        'table': table,
        'fields': fields,
        'tags': tags,
        'time__gte': time__gte, 'time__lte': time__lte,
        'limit': limit,
        'interval': interval, 'interval_agg': interval_agg,
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

    data = json
    if format == 'pandas':
        if data['format'] == 'sparse':
            data = pd.io.json.json_normalize(data['rows'])
        else:
            data = pd.DataFrame(data['rows'], columns=data['columns'])


        if time_index:
            try:
                data.set_index(pd.to_datetime(data.time, unit='s'), inplace=True)
            except:
                print('WARNING: no timestamp available. Set time_index=False')

    t1 = time.perf_counter()

    # Debug
    if debug:
        size = response.headers['Content-Length']
        print(f'{response.request.url}')
        print(f'Returns {size} bytes in {(t1-t0):.2f} seconds')
        #import pprint; pprint.pprint(json)
        print()
        print(data)
        print()

    return data


if __name__ == '__main__':
    time_left = datetime.datetime(2018, 3, 1, tzinfo=datetime.timezone.utc)
    time_right = datetime.datetime(2018, 4, 1, tzinfo=datetime.timezone.utc)
    limit = 2

    #
    # Return all the columns, usefult to know which columns exist
    #
    print(' ALL COLUMNS '.center(72, '='))
    response = query('postgresql', name='LATICE-Flux Finse',
                     time__gte=time_left, time__lte=time_right,
                     limit=1, debug=True)
    response = query('clickhouse', table='finseflux_Biomet',
                     time__gte=time_left, time__lte=time_right,
                     limit=1, debug=True)

    #
    # Select a couple of columns within a time range
    #
    print(' SELECTED COLS IN TIME-RANGE '.center(72, '='))
#   response = query('postgresql', name='LATICE-Flux Finse',
#                    fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
#                    time__gte=time_left, time__lte=time_right,
#                    limit=limit, debug=True)
    response = query('clickhouse', table='finseflux_Biomet',
                     fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
                     time__gte=time_left, time__lte=time_right,
                     limit=limit, debug=True)

    #
    # Select the first row within 1h intervals
    #
    print(' FIRST ROW IN 1H INTERVALS '.center(72, '='))
#   response = query('postgresql', name='LATICE-Flux Finse',
#                    fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
#                    time__gte=time_left, time__lte=time_right,
#                    interval=3600,
#                    limit=limit, debug=True)
    response = query('clickhouse', table='finseflux_Biomet',
                     fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
                     time__gte=time_left, time__lte=time_right,
                     interval=3600,
                     limit=limit, debug=True)

    #
    # Select the average value in 1h intervals
    #
    print(' AVERAGE IN 1H INTERVALS '.center(72, '='))
#   response = query('postgresql', name='LATICE-Flux Finse',
#                    fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
#                    time__gte=time_left, time__lte=time_right,
#                    interval=3600, interval_agg='avg',
#                    limit=limit, debug=True)
    response = query('clickhouse', table='finseflux_Biomet',
                     fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
                     time__gte=time_left, time__lte=time_right,
                     interval=3600, interval_agg='avg',
                     limit=limit, debug=True)

    #
    # Use a different aggregate
    #
    print(' MINIMUM IN 1H INTERVALS '.center(72, '='))
#   response = query('postgresql', name='LATICE-Flux Finse',
#                    fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
#                    time__gte=time_left, time__lte=time_right,
#                    interval=3600, interval_agg='min',
#                    limit=limit, debug=True)
    response = query('clickhouse', table='finseflux_Biomet',
                     fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
                     time__gte=time_left, time__lte=time_right,
                     interval=3600, interval_agg='min',
                     limit=limit, debug=True)

    #
    # Specific to PostgreSQL, return tags
    #
    print(' TAGS '.center(72, '='))
    response = query('postgresql', fields=['bat', 'in_temp'],
                     tags=['serial'],
                     limit=limit, debug=True)
