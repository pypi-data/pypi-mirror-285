# Python Wrapper for the XBRLUS API

This is a library to make requests to the [XBRL US](https://xbrl.us) API.

See the documentation of the API [here](https://xbrlus.github.io/xbrl-api)

## Usage
```py
from xbrluspy import XBRLUSClient, EntityEndpoint

client = XBRLUSClient(
  #get credentials and put them here
  grant_type="password"
)

entity = EntityEndpoint(client)
result = entity.search(
  params={
  "entity.cik": "000031222"
  },
  fields=[
    "entity.id"
  ])
print(result["data"][0]["entity.id"])
```
## Future work
- Creation of datastructures to obtain type-safe data cleanly
- Implementation for Cube, Facts and dimension endpoints are incomplete and will be completed the next version.

