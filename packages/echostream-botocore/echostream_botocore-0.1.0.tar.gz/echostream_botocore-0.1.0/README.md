# echostream-botocore

Provides a `botocore.session.Session` implementation for accessing EchoStream Tenant resources

This package provides two primary mechanisms to create a `botocore.session.Session` object in your EchoStream Tenant; `ApiSession` or `AppSession`. These session objects will automatically refresh both your Cognito credentials and your botocore credentials (using the EchoStream AppSync API).

> Note: Version >= 0.1.0 requires Python 3.12

## Installation
```bash
pip install echostream-botocore
```

## Common parameters
| Parameter | ENV VAR | Description | Required |
| - | - | - | - |
| `appsync_endpoint` | `APPSYNC_ENDPOINT` | The EchoStream AppSync endpoint | If `cognito` not provided |
| `client_id` | `CLIENT_ID` | The Cognito Client Id for the provided `user_pool_id` | If `cognito` not provided |
| `cognito` | N/A | A [`pycognito.Cognito`]((https://github.com/pvizeli/pycognito#cognito-utility-class)) object | If other parameters are not provided |
| `duration` | N/A | The length of time that the underlying credentials should be good for in seconds; shoudl be greater than `900` | Defaults to `3600` |
| `password` | `PASSWORD` | The password associated with `username` | If `cognito` not provided |
| `tenant` | `TENANT` | The name of the EchoStream Tenant | Yes |
| `user_pool_id` | `USER_POOL_ID` | The Cognito User Pool Id | If `cognito` not provided |
| `username` | `USER_NAME` | The username of the `ApiUser` | If `cognito` not provided |


## ApiSession
`ApiSession` objects are used to gain a Tenant-level `botocore.session.Session` in your Tenant using an EchoStream `ApiUser`.

`ApiSession`s may be created using a [`pycognito.Cognito`](https://github.com/pvizeli/pycognito#cognito-utility-class) instance or via a combination of environment variables and parameters. The environment variables or parameters are interchangeable. All parameters/environment variables are required if a  `Cognito` object is not provided. If a `Cognito` object is provided, then all parameters/environment varaiables are ignored and it is assumed that the `Cognito` object references an `ApiUser`.

### Usage (assuming correct ENV setup)
```python
from boto3 import Session
from echostream_botocore import ApiSession

session = Session(
    botocore_session=ApiSession(),
    region_name="us-east-1"
)

ddb_client = session.client("dynamodb")
...
```

## AppSession
`AppSession` objects are used to gain a App-level `botocore.session.Session` in your Tenant using an EchoStream `AppUser`.

`AppSession`s may be created using a [`pycognito.Cognito`](https://github.com/pvizeli/pycognito#cognito-utility-class) instance or via a combination of environment variables and parameters. The environment variables or parameters are interchangeable. All parameters/environment variables are required if a  `Cognito` object is not provided. If a `Cognito` object is provided, then all parameters/environment varaiables are ignored and it is assumed that the `Cognito` object references an `AppUser`.

### Additional Parameters
| Parameter | ENV VAR | Description | Required |
| - | - | - | - |
| `app` | `APP` | The name of the EchoStream App | Yes |

### Usage (assuming correct ENV setup)
```python
from boto3 import Session
from echostream_botocore import AppSession

session = Session(
    botocore_session=AppSession(),
    region_name="us-east-1"
)

ddb_client = session.client("dynamodb")
...
```
