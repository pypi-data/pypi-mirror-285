import logging
from os import environ
from threading import RLock
from typing import Any

from botocore.credentials import Credentials, DeferredRefreshableCredentials
from botocore.session import Session
from gql import Client as GqlClient
from gql import gql
from gql.transport.requests import RequestsHTTPTransport
from graphql import DocumentNode
from pycognito import Cognito
from pycognito.utils import RequestsSrpAuth


def getLogger() -> logging.Logger:
    """
    Returns "echostream-botocore" logger
    """
    return logging.getLogger("echostream-botocore")


getLogger().addHandler(logging.NullHandler())


class EchoStreamSession(Session):
    def __init__(
        self,
        *,
        credentials_key: str,
        document: DocumentNode,
        variable_values: dict[str, Any],
        appsync_endpoint: str = None,
        client_id: str = None,
        cognito: Cognito = None,
        duration: int = None,
        password: str = None,
        user_pool_id: str = None,
        username: str = None,
    ):
        super().__init__()
        lock = RLock()

        if not cognito:
            getLogger().info(
                f"Creating Cognito authentication for user {username} in {user_pool_id}:{client_id}"
            )
            client_id = client_id or environ["CLIENT_ID"]
            user_pool_id = user_pool_id or environ["USER_POOL_ID"]
            username = username or environ["USER_NAME"]
            cognito = Cognito(
                client_id=client_id,
                user_pool_id=user_pool_id,
                username=username,
            )
            try:
                cognito.authenticate(password=password or environ["PASSWORD"])
            except Exception:
                getLogger().exception(
                    f"Unable to authenticate user {username} in {user_pool_id}:{client_id}"
                )
                raise

        gql_client = GqlClient(
            fetch_schema_from_transport=True,
            transport=RequestsHTTPTransport(
                auth=RequestsSrpAuth(cognito=cognito, http_header_prefix=""),
                url=appsync_endpoint or environ["APPSYNC_ENDPOINT"],
            ),
        )

        if "duration" not in variable_values:
            variable_values["duration"] = duration or 3600

        def refresher() -> dict[str, str]:
            with lock:
                getLogger().debug(f"Refreshing {type(self).__name__} credentials")
                try:
                    with gql_client as session:
                        credentials = session.execute(
                            document=document,
                            variable_values=variable_values,
                        )[credentials_key]["GetAwsCredentials"]
                except Exception:
                    getLogger().exception(
                        f"Error refreshing {type(self).__name__} credentials"
                    )
                    raise
                return dict(
                    access_key=credentials["accessKeyId"],
                    expiry_time=credentials["expiration"],
                    secret_key=credentials["secretAccessKey"],
                    token=credentials["sessionToken"],
                )

        self.__credentials = DeferredRefreshableCredentials(
            method="EchoStreamAwsCredentials", refresh_using=refresher
        )

    def get_credentials(self) -> Credentials:
        return self.__credentials


class ApiSession(EchoStreamSession):
    _GET_AWS_CREDENTIALS = gql(
        """
        query getAwsCredentials($tenant: String!, $duration: Int!) {
            GetTenant(tenant: $tenant) {
                GetAwsCredentials(duration: $duration) {
                    accessKeyId
                    secretAccessKey
                    sessionToken
                    expiration
                }
            }
        }
        """
    )

    def __init__(
        self,
        *,
        appsync_endpoint: str = None,
        client_id: str = None,
        cognito: Cognito = None,
        duration: int = None,
        password: str = None,
        tenant: str = None,
        user_pool_id: str = None,
        username: str = None,
    ):
        super().__init__(
            appsync_endpoint=appsync_endpoint,
            client_id=client_id,
            cognito=cognito,
            credentials_key="GetTenant",
            document=self._GET_AWS_CREDENTIALS,
            duration=duration,
            password=password,
            user_pool_id=user_pool_id,
            username=username,
            variable_values=dict(tenant=tenant or environ["TENANT"]),
        )


class AppSession(EchoStreamSession):
    _GET_AWS_CREDENTIALS = gql(
        """
        query getAwsCredentials($app: String!, $tenant: String!, $duration: Int!) {
            GetApp(name: $app, tenant: $tenant) {
                ... on CrossAccountApp {
                    GetAwsCredentials(duration: $duration) {
                        accessKeyId
                        secretAccessKey
                        sessionToken
                        expiration
                    }
                }
                ... on ExternalApp {
                    GetAwsCredentials(duration: $duration) {
                        accessKeyId
                        secretAccessKey
                        sessionToken
                        expiration
                    }
                }
                ... on ManagedApp {
                    GetAwsCredentials(duration: $duration) {
                        accessKeyId
                        secretAccessKey
                        sessionToken
                        expiration
                    }
                }
            }
        }
        """
    )

    def __init__(
        self,
        *,
        app: str = None,
        appsync_endpoint: str = None,
        client_id: str = None,
        cognito: Cognito = None,
        duration: int = None,
        password: str = None,
        tenant: str = None,
        user_pool_id: str = None,
        username: str = None,
    ):

        super().__init__(
            appsync_endpoint=appsync_endpoint,
            client_id=client_id,
            cognito=cognito,
            credentials_key="GetApp",
            document=self._GET_AWS_CREDENTIALS,
            duration=duration,
            password=password,
            user_pool_id=user_pool_id,
            username=username,
            variable_values=dict(
                app=app or environ["APP"], tenant=tenant or environ["TENANT"]
            ),
        )
