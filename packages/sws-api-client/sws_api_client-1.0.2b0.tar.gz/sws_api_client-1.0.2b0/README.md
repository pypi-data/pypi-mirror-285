# SWS API Client

This library provides the user with a set of useful tools to easily interact with the FAO SWS (Statistical Working System) REST APIs.

## Installation

The module is available on Pypi:

```bash
python -m pip install sws_api_client
```

The library requires Python 3.11+.

## Usage

To use the package the user needs to create an instance of the SwsApiClient class, provide it with the necessary parameters and execute the methods to query the specific endpoints.  

### Instantiate the client locally

There are three methods to instantiate the client:

#### 1. Pass the `sws_endpoint` and the `access_token` to the constructor

```python
from sws_api_client import SwsApiClient

sws_client = SwsApiClient(sws_endpoint="<sws_endpoint>", access_token="<access_token>")
```

#### 2. Pass to `sws_endpoint` and the `access_token` as named arguments

We need to execute the script from command line passing `--sws_endpoint` and `--access_token` as arguments:

```bash
python script.py --sws_endpoint <endpoint> --access_token <test_access_token>
```

And instantiate the client in our script with the class method `from_args`:

```python
from sws_api_client import SwsApiClient

sws_client = SwsApiClient.from_args()
```

#### 3. Create a conf file where to store the arguments

We need to create a conf file (default name: `"conf_sws_api_client.json"`) with the following structure:

```json
{
    "sws_endpoint": "https://sws.dev.fao.org",
    "sws_token": "XXX",
    "current_task_id": "XXX",
    "current_execution_id": "XXX",
    "authclient": {
        "clientId": "XXX",
        "clientSecret": "XXX",
        "tokenEndpoint": "https://fao-dev.auth.eu-west-1.amazoncognito.com/oauth2/token",
        "scope": "sws/user"
    }
}
```

And instantiate the client in our script with the class method `auto`:

```python
from sws_api_client import SwsApiClient

sws_client = SwsApiClient.auto()
```

Behind the scene it will automatically detect the fact that you are in debug mode and it will instanciate the client using the `from_conf` method

### Instantiate the client in a SWS plugin

When working withing a SWS plugin instantiate the client as:

```python
from sws_api_client import SwsApiClient

sws_client = SwsApiClient.auto()
```

Behind the scene it will automatically detect the fact that you are in a SWS plugin and it will instanciate the client using the `from_env` method

### Perform requests

To perform requests you just need to call the available methods using the SwsApiClient object, as an example:

```python
datasets = Datasets(sws_client)
dataset = datasets.get_dataset_info('aproduction')
logger.info(f"Dataset info: {dataset}")
```

more complete examples can be found in the `example` folder:

```bash
cp example/conf_sws_api_client.json.example example/conf_sws_api_client.json
# edit the file with your credentials
python3 -m venv example/.venv
source example/.venv/bin/activate
pip install -r example/requirements
python example/dataset_example.py
```

If you need to perform a test request not in debug mode, you can use the following command:
    
```bash
AWS_PROFILE=fao-dev DEBUG_MODE=FALSE SWS_USER_CREDENTIALS_SECRET_NAME=dev/sws/user_client SWS_TOKEN=YOUR_TOKEN SWS_ENDPOINT=https://sws.dev.fao.org python3 dataset_example.py
```
