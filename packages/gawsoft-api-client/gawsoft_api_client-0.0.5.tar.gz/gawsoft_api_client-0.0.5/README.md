# Overall
Rest API client for Python

Simple REST API client for Python

## Installation

Use the package manager pip to install our client in Python.

```bash
pip install gawsoft-api-client
```

OR
```bash
pip3 install gawsoft-api-client
```

## Usage
Write your client api
```python
from gawsoft.api_client import Request, Response


class Client(Request):
    def __init__(
        self,
        api_key: str,
        api_version: str ='',
        api_host: str = 'http://httpbin.org',
        user_agent: str = 'Example Api Python client'
     ):
        super().__init__(api_key, api_version, api_host, user_agent)

    def info(self, link: str, params: dict = {}) -> Response:
        return self.request(link, 'POST', params)


c = Client("abc")
response = c.info("delay/1")
print(response.status_code)
print(response.data())
```


## Tests
```sh
make test
make mypy
```

## Release
```sh
bin/release.sh
```

## License
[MIT](https://choosealicense.com/licenses/mit/)