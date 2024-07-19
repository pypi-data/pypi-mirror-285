# Altissimo Python package

## Classes

### Firestore
#### Usage
```
from altissimo.firestore import Firestore

f = Firestore(project=project, credentials=credentials, database=database)

# get a list of dicts from a Firestore Collection
items = f.get_collection("collection")
```

### SecretManager
#### Usage
```
from altissimo.secretmanager import SecretManager

s = SecretManager(project=project, credentials=credentials)

# get the value of a SecretManager Secret Version
secret = s.get_secret(secret, version="latest", project=project)
```

## Modules

### Tools
#### Usage
```
from altissimo.tools import chunks

# get successive chunks of 5 items from list
for chunk in chunks(my_list, 5):
    # process the chunk
    pass
```

* `chunks(list, n)`: Return successive n-sized chunks from list.
* `list_to_dict(list, key="id")`: Return a dict of items by key from list.
