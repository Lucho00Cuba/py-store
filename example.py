from store import Store

# Initialize Store with a path to a JSON file
store = Store('data.json')

# Set a value
store.username = "JohnDoe"

# Get a value
print(store.username)

# Delete a value
del store.username

# Use as a dictionary
store['user.name'] = "JaneDoe"
print(store['user.name'])


if 'metadata.user.name' in store:
    del store['metadata.user.name']
if not 'metadata.user.name' in store:
    print("NOT FOUND!")
store['metadata.user.name'] = "Lucho"
if 'metadata.user.name' in store:
    print(store['metadata.user.name'])
store['metadata.user.pass'] = "*****"

# Context manager for temporary changes
with store:
    store.temp_value = "Temporary"
    print(store.temp_value)
# temp_value is discarded after the `with` block ends