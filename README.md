# WSN\_client

This package contains client function to interact with the UiO Django App developed for
the Wireless Sensor Network.

Contributors by alphabetical order:

- David J. Ibanez
- Simon Filhol (simon.filhol@geo.uio.no)


## Installation

Requires Python 3.7 or later. Create a virtual environment, with conda or venv,
then install the package from the project repository:

```sh
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the package
pip install git+https://github.com/spectraphilic/wsn_client.git
```

### For development

Or clone the project first, specially if you need to change it:

```sh
# Clone the package to your computer
git clone git@github.com:spectraphilic/wsn_client.git
cd wsn_client

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the package with "pip install [path to package on your local machine]"
pip install .

# Or install a development version to your activated virtual environment
pip install --editable .
```

## Usage

```python
query('clickhouse', table='', ...) -> dataframe or dict
    query('postgresql', ...) -> dataframe or dict
```

Retrieves data from the UiO Django system.

### Selecting data (rows)

First choose the database to pull data from, choices are
clickhouse (for raw data from finse/mobile flux), and postgresql (for
everything else). How data is selected depends on the database used.

**ClickHouse:**

​    `query('clickhouse', table='finseflux_Biomet', ...)`

Choices for table are: `finseflux_Biomet, finseflux_StationStatus,
mobileflux_Biomet` and `mobileflux_StationStatus`.

**PostgreSQL:**

```python
query('postgresql', name='eddypro_Finseflux', ...)
query('postgresql', serial=0x1F566F057C105487, ...)
query('postgresql', source_addr_long=0x0013A2004105D4B6, ...)
```

Data from PostgreSQL can be queried by any metadata information, most often
the name is all you need.

### Selecting fields (columns)

If the fields parameter is not given, all the fields will be returned. This
is only recommended to explore the available columns, because it may be too
slow and add a lot of work on the servers. So it is recommended to ask only
for the fields you need, it will be much faster.

Examples:

```python
query('clickhouse', table='finseflux_Biomet', fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'], ...)
query('postgresql', name='eddypro_Finseflux', fields=['co2_flux'], ...)
```



The field 'time' is always included, do not specify it. It's a Unix
timestamp (seconds since the Unix epoch). The rows returned are ordered by
this field.

### Selecting a time range

Use the parameters `time__gte` and/or `time__lte` to define the time range of
interest. The smaller the faster the query will run.

These parameters expect a `datetime` object. If the timezone is not specified
it will be interpreted as local time, but it's probably better to
explicitly use UTC.

**Example:**

```python
query(
        'clickhouse', table='finseflux_Biomet',
        fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
        time__gte=datetime.datetime(2018, 3, 1, tzinfo=datetime.timezone.utc),
        time__lte=datetime.datetime(2018, 4, 1, tzinfo=datetime.timezone.utc),
        ...
    )
```

### Limiting the number of rows

The limit parameter defines the maximum number of rows to return. If not
given all selected rows will be returned.

**Example:**

```python
query(
        'clickhouse', table='finseflux_Biomet',
        fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
        time__gte=datetime.datetime(2018, 3, 1, tzinfo=datetime.timezone.utc),
        time__lte=datetime.datetime(2018, 4, 1, tzinfo=datetime.timezone.utc),
        limit=1000000,
    )
```

### Intervals and aggregates

Instead of returning every data point, it's possible split the time range
in intervals and return only one row per interval. This can greatly reduce
the amount of data returned, speeding up the query.

For this purpose pass the interval parameter, which defines the interval
size in seconds. The interval is left-closed and right-open.

By default the first row found within the interval will be returned. The
time column will be that of the first row. For example, if the interval
is 1 hour and the first row is at :05 then the time column will be :05

If the `interval_agg` parameter is passed, then an aggregate for every
column within the interval will be returned. The time column will be
the beginning of the interval. For example if the interval is 1h, the
time column will be :00

**Example** (interval size is 5 minutes):

```python
query(
        'clickhouse', table='finseflux_Biomet',
        fields=['LWIN_6_14_1_1_1', 'LWOUT_6_15_1_1_1'],
        time__gte=datetime.datetime(2018, 3, 1, tzinfo=datetime.timezone.utc),
        time__lte=datetime.datetime(2018, 4, 1, tzinfo=datetime.timezone.utc),
        limit=1000000,
        interval=60*5,
        interval_agg='avg',
    )
```

If using postgresql the available functions are: `avg, count, max, min,
stddev, sum and variance.`

If using clickhouse any aggregate function supported by ClickHouse can be
used, see <https://clickhouse-docs.readthedocs.io/en/latest/agg_functions/>

### Tags (PostgreSQL only)

With PostgreSQL only, you can pass the tags parameter to add metadata
information to every row.

**Example:**

```python
query(
        'postgresql', name='fw-001',
        fields=['latitude', 'longitude'],
        tags=['serial'],
    )
```

In this example, the data from fw-001 may actually come from different
devices, maybe the device was replaced at some point. Using the tags
parameter we can add a column with the serial number of the devices.

Tags don't work with aggregated values.

### Returns

This function returns by default a Pandas dataframe. Use `format='json'` to
return instead a Python dictionary, with the data as was sent by the server.

### Debugging

With `debug=True` this function will print some information, useful for
testing. `Default` is `False`
