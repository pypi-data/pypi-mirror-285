# formance-sdk-wallets

<div align="left">
    <a href="https://speakeasyapi.dev/"><img src="https://custom-icon-badges.demolab.com/badge/-Built%20By%20Speakeasy-212015?style=for-the-badge&logoColor=FBE331&logo=speakeasy&labelColor=545454" /></a>
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg" style="width: 100px; height: 28px;" />
    </a>
</div>


## 🏗 **Welcome to your new SDK!** 🏗

It has been generated successfully based on your OpenAPI spec. However, it is not yet ready for production use. Here are some next steps:
- [ ] 🛠 Make your SDK feel handcrafted by [customizing it](https://www.speakeasyapi.dev/docs/customize-sdks)
- [ ] ♻️ Refine your SDK quickly by iterating locally with the [Speakeasy CLI](https://github.com/speakeasy-api/speakeasy)
- [ ] 🎁 Publish your SDK to package managers by [configuring automatic publishing](https://www.speakeasyapi.dev/docs/advanced-setup/publish-sdks)
- [ ] ✨ When ready to productionize, delete this section from the README

<!-- Start SDK Installation [installation] -->
## SDK Installation

```bash
pip install formance-sdk-wallets
```
<!-- End SDK Installation [installation] -->

<!-- Start SDK Example Usage [usage] -->
## SDK Example Usage

### Example

```python
import formancesdkwallets
from formancesdkwallets.models import components

s = formancesdkwallets.FormanceSDKWallets(
    security=components.Security(
        formance_o_auth=components.SchemeFormanceOAuth(
            client_id="<YOUR_CLIENT_ID_HERE>",
            client_secret="<YOUR_CLIENT_SECRET_HERE>",
            token_url="<YOUR_TOKEN_URL_HERE>",
        ),
    ),
)


res = s.info()

if res is not None:
    # handle response
    pass

```
<!-- End SDK Example Usage [usage] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

### [FormanceSDKWallets SDK](docs/sdks/formancesdkwallets/README.md)

* [info](docs/sdks/formancesdkwallets/README.md#info)

### [holds](docs/sdks/holds/README.md)

* [list](docs/sdks/holds/README.md#list)
* [get](docs/sdks/holds/README.md#get)
* [confirm](docs/sdks/holds/README.md#confirm)
* [cancel](docs/sdks/holds/README.md#cancel)

### [wallets](docs/sdks/wallets/README.md)

* [list](docs/sdks/wallets/README.md#list)
* [create](docs/sdks/wallets/README.md#create)
* [get](docs/sdks/wallets/README.md#get)
* [update](docs/sdks/wallets/README.md#update)
* [credit](docs/sdks/wallets/README.md#credit)
* [debit](docs/sdks/wallets/README.md#debit)
* [summary](docs/sdks/wallets/README.md#summary)

### [balances](docs/sdks/balances/README.md)

* [create](docs/sdks/balances/README.md#create)
* [list](docs/sdks/balances/README.md#list)
* [get](docs/sdks/balances/README.md#get)
<!-- End Available Resources and Operations [operations] -->

<!-- Start Pagination [pagination] -->
## Pagination

Some of the endpoints in this SDK support pagination. To use pagination, you make your SDK calls as usual, but the
returned response object will have a `Next` method that can be called to pull down the next group of results. If the
return value of `Next` is `None`, then there are no more pages to be fetched.

Here's an example of one such pagination call:
```python
import formancesdkwallets
from formancesdkwallets.models import components

s = formancesdkwallets.FormanceSDKWallets(
    security=components.Security(
        formance_o_auth=components.SchemeFormanceOAuth(
            client_id="<YOUR_CLIENT_ID_HERE>",
            client_secret="<YOUR_CLIENT_SECRET_HERE>",
            token_url="<YOUR_TOKEN_URL_HERE>",
        ),
    ),
)


res = s.holds.list(wallet_id='<value>', cursor='<value>', page_size=768578)

if res is not None:
    while True:
        # handle items

        res = res.Next()
        if res is None:
            break


```
<!-- End Pagination [pagination] -->

<!-- Start Retries [retries] -->
## Retries

Some of the endpoints in this SDK support retries. If you use the SDK without any configuration, it will fall back to the default retry strategy provided by the API. However, the default retry strategy can be overridden on a per-operation basis, or across the entire SDK.

To change the default retry strategy for a single API call, simply provide a `RetryConfig` object to the call:
```python
import formancesdkwallets
from formancesdkwallets.models import components
from formancesdkwallets.utils import BackoffStrategy, RetryConfig

s = formancesdkwallets.FormanceSDKWallets(
    security=components.Security(
        formance_o_auth=components.SchemeFormanceOAuth(
            client_id="<YOUR_CLIENT_ID_HERE>",
            client_secret="<YOUR_CLIENT_SECRET_HERE>",
            token_url="<YOUR_TOKEN_URL_HERE>",
        ),
    ),
)


res = s.info(,
    RetryConfig('backoff', BackoffStrategy(1, 50, 1.1, 100), False))

if res is not None:
    # handle response
    pass

```

If you'd like to override the default retry strategy for all operations that support retries, you can use the `retry_config` optional parameter when initializing the SDK:
```python
import formancesdkwallets
from formancesdkwallets.models import components
from formancesdkwallets.utils import BackoffStrategy, RetryConfig

s = formancesdkwallets.FormanceSDKWallets(
    retry_config=RetryConfig('backoff', BackoffStrategy(1, 50, 1.1, 100), False),
    security=components.Security(
        formance_o_auth=components.SchemeFormanceOAuth(
            client_id="<YOUR_CLIENT_ID_HERE>",
            client_secret="<YOUR_CLIENT_SECRET_HERE>",
            token_url="<YOUR_TOKEN_URL_HERE>",
        ),
    ),
)


res = s.info()

if res is not None:
    # handle response
    pass

```
<!-- End Retries [retries] -->

<!-- Start Error Handling [errors] -->
## Error Handling

Handling errors in this SDK should largely match your expectations.  All operations return a response object or raise an error.  If Error objects are specified in your OpenAPI Spec, the SDK will raise the appropriate Error type.

| Error Object        | Status Code         | Content Type        |
| ------------------- | ------------------- | ------------------- |
| errors.WalletsError | default             | application/json    |
| errors.SDKError     | 4xx-5xx             | */*                 |

### Example

```python
import formancesdkwallets
from formancesdkwallets.models import components, errors

s = formancesdkwallets.FormanceSDKWallets(
    security=components.Security(
        formance_o_auth=components.SchemeFormanceOAuth(
            client_id="<YOUR_CLIENT_ID_HERE>",
            client_secret="<YOUR_CLIENT_SECRET_HERE>",
            token_url="<YOUR_TOKEN_URL_HERE>",
        ),
    ),
)

res = None
try:
    res = s.holds.list(wallet_id='<value>', cursor='<value>', page_size=768578)

except errors.WalletsError as e:
    # handle exception
    raise(e)
except errors.SDKError as e:
    # handle exception
    raise(e)

if res is not None:
    while True:
        # handle items

        res = res.Next()
        if res is None:
            break


```
<!-- End Error Handling [errors] -->

<!-- Start Server Selection [server] -->
## Server Selection

### Select Server by Index

You can override the default server globally by passing a server index to the `server_idx: int` optional parameter when initializing the SDK client instance. The selected server will then be used as the default on the operations that use it. This table lists the indexes associated with the available servers:

| # | Server | Variables |
| - | ------ | --------- |
| 0 | `http://localhost` | None |

#### Example

```python
import formancesdkwallets
from formancesdkwallets.models import components

s = formancesdkwallets.FormanceSDKWallets(
    server_idx=0,
    security=components.Security(
        formance_o_auth=components.SchemeFormanceOAuth(
            client_id="<YOUR_CLIENT_ID_HERE>",
            client_secret="<YOUR_CLIENT_SECRET_HERE>",
            token_url="<YOUR_TOKEN_URL_HERE>",
        ),
    ),
)


res = s.info()

if res is not None:
    # handle response
    pass

```


### Override Server URL Per-Client

The default server can also be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
import formancesdkwallets
from formancesdkwallets.models import components

s = formancesdkwallets.FormanceSDKWallets(
    server_url="http://localhost",
    security=components.Security(
        formance_o_auth=components.SchemeFormanceOAuth(
            client_id="<YOUR_CLIENT_ID_HERE>",
            client_secret="<YOUR_CLIENT_SECRET_HERE>",
            token_url="<YOUR_TOKEN_URL_HERE>",
        ),
    ),
)


res = s.info()

if res is not None:
    # handle response
    pass

```
<!-- End Server Selection [server] -->

<!-- Start Custom HTTP Client [http-client] -->
## Custom HTTP Client

The Python SDK makes API calls using the [requests](https://pypi.org/project/requests/) HTTP library.  In order to provide a convenient way to configure timeouts, cookies, proxies, custom headers, and other low-level configuration, you can initialize the SDK client with a custom `requests.Session` object.

For example, you could specify a header for every request that this sdk makes as follows:
```python
import formancesdkwallets
import requests

http_client = requests.Session()
http_client.headers.update({'x-custom-header': 'someValue'})
s = formancesdkwallets.FormanceSDKWallets(client=http_client)
```
<!-- End Custom HTTP Client [http-client] -->

<!-- Start Authentication [security] -->
## Authentication

### Per-Client Security Schemes

This SDK supports the following security schemes globally:

| Name              | Type              | Scheme            |
| ----------------- | ----------------- | ----------------- |
| `formance_o_auth` | oauth2            | OAuth2 token      |
| `bearer_auth`     | http              | HTTP Bearer       |

You can set the security parameters through the `security` optional parameter when initializing the SDK client instance. The selected scheme will be used by default to authenticate with the API for all operations that support it. For example:
```python
import formancesdkwallets
from formancesdkwallets.models import components

s = formancesdkwallets.FormanceSDKWallets(
    security=components.Security(
        formance_o_auth=components.SchemeFormanceOAuth(
            client_id="<YOUR_CLIENT_ID_HERE>",
            client_secret="<YOUR_CLIENT_SECRET_HERE>",
            token_url="<YOUR_TOKEN_URL_HERE>",
        ),
    ),
)


res = s.info()

if res is not None:
    # handle response
    pass

```
<!-- End Authentication [security] -->

<!-- Placeholder for Future Speakeasy SDK Sections -->

# Development

## Maturity

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning usage
to a specific package version. This way, you can install the same version each time without breaking changes unless you are intentionally
looking for the latest version.

## Contributions

While we value open-source contributions to this SDK, this library is generated programmatically.
Feel free to open a PR or a Github issue as a proof of concept and we'll do our best to include it in a future release!

### SDK Created by [Speakeasy](https://docs.speakeasyapi.dev/docs/using-speakeasy/client-sdks)
