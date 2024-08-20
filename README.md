# JSON Store

This project provides a Python class, `Store`, that offers object-based access to a JSON file. It allows you to easily load, manipulate, and save data in a JSON format using simple object-oriented methods.

## Features

- **Object-Based Access**: Interact with JSON data as if it were a Python object.
- **Automatic Saving**: Automatically saves changes to the JSON file if `auto_commit` is enabled.
- **Context Management**: Use Python's `with` statement to manage changes with an automatic rollback in case of an exception.
- **Intermediate Key Creation**: Automatically creates intermediate keys when setting deeply nested values.

## Usage

```python
from store import Store

# Creating a Store
store = Store('data.json')

# Set a value
store['user.name'] = 'JaneDoe'

# Get a value
print(store['user.name'])

# Deleting a Value
del store['user.name']

# Checking if a Key Exists
if 'user.name' in store:
    print("User name exists")

# Using with Context Manager
with store:
    store['user.age'] = 30
    # If an exception occurs, changes will be discarded
```

## Exception Handling

The `Store` class includes robust exception handling to ensure that errors are properly managed:

- File Errors: Handles errors related to file operations, such as reading or writing the JSON file.
- Key Errors: Provides informative messages when accessing or deleting non-existent keys.
- Type Errors: Ensures that only valid data types are used as keys and values in the JSON store.