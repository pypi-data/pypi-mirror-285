# py-bw-vault-api-unofficial

[![PyPI version](https://badge.fury.io/py/py-bw-vault-management-api-client.svg)](https://badge.fury.io/py/py-bw-vault-management-api-client)
![GitLab License](https://img.shields.io/gitlab/license/grey-panther%2Fpy-bw-vault-api-unofficial)


An unofficial Python wrapper around the [BitWarden Vault Management API](https://bitwarden.com/help/vault-management-api/) (the one exposed by the [BitWarden CLI](https://bitwarden.com/help/cli/) - ie. when running `bw serve`). Licensed under the LGPL v2.1 license (see LICENSE). Auto-generated from the OpenAPI definition file provided by BitWarden using [openapi-python-client](https://pypi.org/project/openapi-python-client/).

## Usage
First, create a client. localhost / 8087 are the default host / port used by `bw serve`, but it can be customized by the `--hostname` and `--port` arguments:

```python
from vault_management_api_client import Client

client = Client(base_url="http://localhost:8087")
```

Now call your endpoint and use your models:

```python
from vault_management_api_client.models import MyDataModel
from vault_management_api_client.api.my_tag import get_my_data_model
from vault_management_api_client.types import Response

with client as client:
    my_data: MyDataModel = get_my_data_model.sync(client=client)
    # or if you need more info (e.g. status_code)
    response: Response[MyDataModel] = get_my_data_model.sync_detailed(client=client)
```

Or do the same thing with an async version:

```python
from vault_management_api_client.models import MyDataModel
from vault_management_api_client.api.my_tag import get_my_data_model
from vault_management_api_client.types import Response

async with client as client:
    my_data: MyDataModel = await get_my_data_model.asyncio(client=client)
    response: Response[MyDataModel] = await get_my_data_model.asyncio_detailed(client=client)
```

For a list of API calls, see the [BitWarden Vault Management API documentation](https://bitwarden.com/help/vault-management-api/).

Things to know:
1. Every path/method combo becomes a Python module with four functions:
    1. `sync`: Blocking request that returns parsed data (if successful) or `None`
    1. `sync_detailed`: Blocking request that always returns a `Request`, optionally with `parsed` set if the request was successful.
    1. `asyncio`: Like `sync` but async instead of blocking
    1. `asyncio_detailed`: Like `sync_detailed` but async instead of blocking

1. All path/query params, and bodies become method arguments.
1. If your endpoint had any tags on it, the first tag will be used as a module name for the function (my_tag above)
1. Any endpoint which did not have a tag will be in `vault_management_api_client.api.default`


## Building / publishing this package
This project uses [Poetry](https://python-poetry.org/) to manage dependencies  and packaging.  Here are the basics:
1. Update the metadata in pyproject.toml (e.g. authors, version)
1. If you're using a private repository, configure it with Poetry
    1. `poetry config repositories.<your-repository-name> <url-to-your-repository>`
    1. `poetry config http-basic.<your-repository-name> <username> <password>`
1. Publish the client with `poetry publish --build -r <your-repository-name>` or, if for public PyPI, just `poetry publish --build`

If you want to install this client into another project without publishing it (e.g. for development) then:
1. If that project **is using Poetry**, you can simply do `poetry add <path-to-this-client>` from that project
1. If that project is not using Poetry:
    1. Build a wheel with `poetry build -f wheel`
    1. Install that wheel from the other project `pip install <path-to-wheel>`
