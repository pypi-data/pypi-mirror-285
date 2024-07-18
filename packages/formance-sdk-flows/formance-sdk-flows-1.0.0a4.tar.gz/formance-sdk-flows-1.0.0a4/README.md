# formance-sdk-flows

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
pip install formance-sdk-flows
```
<!-- End SDK Installation [installation] -->

<!-- Start SDK Example Usage [usage] -->
## SDK Example Usage

### Example

```python
import formancesdkflows
from formancesdkflows.models import components

s = formancesdkflows.FormanceSDKFlows(
    security=components.Security(
        bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
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

### [FormanceSDKFlows SDK](docs/sdks/formancesdkflows/README.md)

* [info](docs/sdks/formancesdkflows/README.md#info)

### [instances](docs/sdks/instances/README.md)

* [list](docs/sdks/instances/README.md#list)
* [get](docs/sdks/instances/README.md#get)
* [abort](docs/sdks/instances/README.md#abort)
* [send](docs/sdks/instances/README.md#send)
* [get_history](docs/sdks/instances/README.md#get_history)
* [get_stage_history](docs/sdks/instances/README.md#get_stage_history)

### [triggers](docs/sdks/triggers/README.md)

* [list](docs/sdks/triggers/README.md#list)
* [create](docs/sdks/triggers/README.md#create)
* [get](docs/sdks/triggers/README.md#get)
* [delete](docs/sdks/triggers/README.md#delete)
* [list_occurences](docs/sdks/triggers/README.md#list_occurences)
* [test](docs/sdks/triggers/README.md#test)

### [workflows](docs/sdks/workflows/README.md)

* [list](docs/sdks/workflows/README.md#list)
* [create](docs/sdks/workflows/README.md#create)
* [get](docs/sdks/workflows/README.md#get)
* [delete](docs/sdks/workflows/README.md#delete)
* [run](docs/sdks/workflows/README.md#run)
<!-- End Available Resources and Operations [operations] -->

<!-- Start Pagination [pagination] -->
## Pagination

Some of the endpoints in this SDK support pagination. To use pagination, you make your SDK calls as usual, but the
returned response object will have a `Next` method that can be called to pull down the next group of results. If the
return value of `Next` is `None`, then there are no more pages to be fetched.

Here's an example of one such pagination call:
```python
import formancesdkflows
from formancesdkflows.models import components

s = formancesdkflows.FormanceSDKFlows(
    security=components.Security(
        bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
    ),
)


res = s.instances.list(workflow_id='<value>', running=False, cursor='<value>', page_size=768578)

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
import formancesdkflows
from formancesdkflows.models import components
from formancesdkflows.utils import BackoffStrategy, RetryConfig

s = formancesdkflows.FormanceSDKFlows(
    security=components.Security(
        bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
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
import formancesdkflows
from formancesdkflows.models import components
from formancesdkflows.utils import BackoffStrategy, RetryConfig

s = formancesdkflows.FormanceSDKFlows(
    retry_config=RetryConfig('backoff', BackoffStrategy(1, 50, 1.1, 100), False),
    security=components.Security(
        bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
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

| Error Object     | Status Code      | Content Type     |
| ---------------- | ---------------- | ---------------- |
| errors.FlowError | default          | application/json |
| errors.SDKError  | 4xx-5xx          | */*              |

### Example

```python
import formancesdkflows
from formancesdkflows.models import components, errors

s = formancesdkflows.FormanceSDKFlows(
    security=components.Security(
        bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
    ),
)

res = None
try:
    res = s.instances.list(workflow_id='<value>', running=False, cursor='<value>', page_size=768578)

except errors.FlowError as e:
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
import formancesdkflows
from formancesdkflows.models import components

s = formancesdkflows.FormanceSDKFlows(
    server_idx=0,
    security=components.Security(
        bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
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
import formancesdkflows
from formancesdkflows.models import components

s = formancesdkflows.FormanceSDKFlows(
    server_url="http://localhost",
    security=components.Security(
        bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
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
import formancesdkflows
import requests

http_client = requests.Session()
http_client.headers.update({'x-custom-header': 'someValue'})
s = formancesdkflows.FormanceSDKFlows(client=http_client)
```
<!-- End Custom HTTP Client [http-client] -->

<!-- Start Authentication [security] -->
## Authentication

### Per-Client Security Schemes

This SDK supports the following security schemes globally:

| Name              | Type              | Scheme            |
| ----------------- | ----------------- | ----------------- |
| `bearer_auth`     | http              | HTTP Bearer       |
| `formance_o_auth` | oauth2            | OAuth2 token      |

You can set the security parameters through the `security` optional parameter when initializing the SDK client instance. The selected scheme will be used by default to authenticate with the API for all operations that support it. For example:
```python
import formancesdkflows
from formancesdkflows.models import components

s = formancesdkflows.FormanceSDKFlows(
    security=components.Security(
        bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
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

While we value open-source contributions to this SDK, this library is generated programmatically. Any manual changes added to internal files will be overwritten on the next generation. 
We look forward to hearing your feedback. Feel free to open a PR or an issue with a proof of concept and we'll do our best to include it in a future release. 

### SDK Created by [Speakeasy](https://docs.speakeasyapi.dev/docs/using-speakeasy/client-sdks)
