# LookerAPI Python Library

This Python library allows you to connect to Looker, run queries, and retrieve data as pandas DataFrames. This simplifies the process of interacting with Looker's API and makes it easier to analyze data using pandas.

## Installation

To use this library, you need to have the Looker SDK installed. You can install it using pip:

```sh
pip install looker-sdk
pip install pandas
```
# Usage
## Setup
1. Configuration:
    Create a configuration file (e.g., looker.ini) with your Looker API credentials. The configuration file should look something like this:

    ```ini
    [Looker]
    base_url=https://your.looker.instance
    client_id=your_client_id
    client_secret=your_client_secret
    ```

2. Initialize the Connection:
    ```python
    from LookerDF import Connect
    looker_ini_path = 'path_to_your_looker.ini'
    connection = Connect(looker_ini_path)
    ```

# Running Queries
1. Simple Query:
```python
from your_library_name import GetData

df = GetData.get_query(
    sdk=connection.sdk,
    model='your_model',
    view='your_view',
    sort_by='your_sort_field',
    sort_type='desc',
    limit=100,
    fields=['field1', 'field2'],
    filters={'field': 'value'}
)

print(df)
```
2. Look Query:
```python
df = GetData.get_look(
    sdk=connection.sdk,
    look_id=123,
    limit=100
)

print(df)
```
# Classes and Methods
## Connect Class
### Methods:
`__init__(looker_ini_path)`: Initializes the connection to Looker using the provided ini file.
`make_sdk(looker_ini_path)`: Creates the Looker SDK instance.

## GetData Class
### Static Methods:
`get_query(sdk, model, view, sort_by, sort_type='', is_total, fields, filters, limit=500)`: Runs a Looker query and returns the data as a pandas DataFrame.
`get_look(sdk, look_id, limit=500)`: Retrieves data from a Looker Look and returns it as a pandas DataFrame.

# Example
Here's a complete example of how to use the library:

```python
import pandas as pd
from your_library_name import Connect, GetData

# Initialize connection
looker_ini_path = 'path_to_your_looker.ini'
connection = Connect(looker_ini_path)

# Run a query
df = GetData.get_query(
    sdk=connection.sdk,
    model='your_model',
    view='your_view',
    sort_by='your_sort_field',
    sort_type='desc', 
    limit=100,
    fields=['field1', 'field2'],
    filters={'field': 'value'}
)

print(df)

# Get data from a Look
df = GetData.get_look(
    sdk=connection.sdk,
    look_id=123,
    limit=100
)

print(df)
```


