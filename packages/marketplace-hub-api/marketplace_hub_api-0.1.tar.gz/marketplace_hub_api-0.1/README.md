# [![API-HUB](https://zylalabs.com/img/logo-removebg-preview.png)](https://zylalabs.com)

**API-HUB Python SDK** - Find, Connect and Manage APIs
All with a single account, single API key, and single SDK.

## Key Features:

- **Built for Developers:** Tailored for developers, ensuring ease of use and seamless integration.
- **Powerful JSON API:** Robust JSON API designed for accurate and efficient data retrieval.
- **User-Friendly Documentation:** Navigate through our comprehensive documentation for a smooth integration process.
- **Specialized Support:** Count on our dedicated support team for assistance tailored to your specific needs.


## Documentation

<!-- For detailed information on API endpoints, usage, and integration guidelines, check our [API Documentation](https://www.metals-api.com/documentation). -->

Start using API-HUB today. Visit [Zylalabs.com](https://zylalabs.com) and integrate in just minutes!


## Installation

You can install API-HUB Python SDK with pip.

```bash
pip ahi_hub
```

## Usage

The API-HUB Python SDK is a wrapper around the [requests](https://docs.python-requests.org/en/master/) library. API-HUB supports a GET request for now.

Sign-up to API-HU-API to [get your API key](https://zylalabs.com/register) and some credits to get started.

### Making the GET request

```python
>>> from api_hub.client import ApiHubClient

>>> client = ApiHubClient(access_key='REPLACE-WITH-YOUR-ACCESS-KEY')

>>> response = client.get_data_no_params(url)
```

### Request Example

```python
>>> from api_hub.client import ApiHubClient

>>> client = ApiHubClient(access_key='REPLACE-WITH-YOUR-ACCESS-KEY')

>>> response = client.get_data_no_params("https://zylalabs.com/api/392/exercise+database+api/309/list+of+body+parts")
```

### Response Example

```json
    [
    "waist",
    "upper legs",
    "back",
    "lower legs",
    "chest",
    "upper arms",
    "cardio",
    "shoulders",
    "lower arms",
    "neck"
    ]
```

### AVAILABLE METHODS

```python
>>> get_data_no_params(url: str)
```

