# Hoptico Python Client (`pyhoptico`)

This is the Python client for the Hoptico web service.

## Usage

```py
from pyhoptico import HopticoClient
auth_token = 'secret_....'
c = HopticoClient(auth_token)
c.search_beverages('Arrogant')
```