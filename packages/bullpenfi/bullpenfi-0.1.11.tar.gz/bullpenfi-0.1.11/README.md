# bullpenfi

## Authentication

Some functions in this package require authentication using an API key.

### Usage Example

```python
from bullpenfi.module1 import example_function, restricted_function

api_key = "your-valid-api-key-1"

try:
    print(example_function(api_key))
    print(restricted_function(api_key))
except PermissionError as e:
    print(e)
```
