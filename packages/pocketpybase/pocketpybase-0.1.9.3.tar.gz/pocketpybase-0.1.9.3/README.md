# PocketBase Python Client

A Python client for interacting with PocketBase, a backend for your next SaaS and Mobile app.

## Installation

To install the PocketBase Python client, use pip:

```
pip install pocketpybase
```

## Usage

First, import and initialize the PocketBase client:

```python
from pocketbase import PocketBase

pb = PocketBase('https://your-pocketbase-url.com', 'your_username', 'your_password')
```

### Records

#### Creating a record

```python
record = {
    'field1': 'value1',
    'field2': 'value2'
}
created_record = pb.create_record('your_collection_name', record, token=None, expand="", fields="")
```

#### Getting all records

```python
records = pb.get_all_records('your_collection_name', token=None, page=1, perPage=30, sort="", filter="", expand="", fields="", skipTotal=False)
```

#### Getting a record by ID

```python
record = pb.get_record_by_id('your_collection_name', 'record_id', token=None, expand="", fields="")
```

#### Updating a record

```python
updated_record = {
    'field1': 'new_value1',
    'field2': 'new_value2'
}
pb.update_record('your_collection_name', 'record_id', updated_record, token=None, expand="", fields="")
```

#### Deleting a record

```python
pb.delete_record('your_collection_name', 'record_id', token=None)
```

### Collections

#### Creating a collection

```python
collection_name = 'new_collection'
db_type = 'base'
schema = [
    {
        'name': 'field1',
        'type': 'text',
        'required': True
    },
    {
        'name': 'field2',
        'type': 'number',
        'required': False
    }
]
pb.create_collection(collection_name, db_type, schema, fields="")
```

#### Listing collections

```python
collections = pb.list_collections(page=1, perPage=30, sort="", filter="", fields="", skipTotal=False)
```

#### Transactions

```python
@pb.transaction("test")
def update_test(collection, record_id, increment):
    record = collection.get_record_by_id(record_id)
    record["test"] = record.get("test", 0) + increment
    updated_record = collection.update_record(record_id, record)
    return updated_record
```

### Authentication

#### Getting an authentication token

```python
token = pb.get_token()
```

#### Refreshing an authentication token

```python
token = pb.auth_refresh(token)
```

## Features

- Create, read, update, and delete records
- Create and manage collections
- Authenticate and retrieve tokens
- Support for pagination, sorting, filtering, and field selection
- Easily extensible for additional PocketBase features

## Parameters

Most methods support the following optional parameters:

- `token`: Authentication token
- `page`: Page number for pagination
- `perPage`: Number of items per page
- `sort`: Sorting criteria
- `filter`: Filtering criteria
- `expand`: Related collections to expand
- `fields`: Specific fields to return
- `skipTotal`: Whether to skip total count calculation

## Dependencies

- httpx

## License

[MIT License](LICENSE)
