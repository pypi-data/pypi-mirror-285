import os
import json
import tempfile
from contextlib import contextmanager


@contextmanager
def hide_access_keys(*args, **kwds):
    if "AWS_ACCESS_KEY_ID" in os.environ:
        AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
        del os.environ["AWS_ACCESS_KEY_ID"]
    else:
        AWS_ACCESS_KEY_ID = None
    if "AWS_SECRET_ACCESS_KEY" in os.environ:
        AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
        del os.environ["AWS_SECRET_ACCESS_KEY"]
    else:
        AWS_SECRET_ACCESS_KEY = None
    if "AWS_SESSION_TOKEN" in os.environ:
        AWS_SESSION_TOKEN = os.environ["AWS_SESSION_TOKEN"]
        del os.environ["AWS_SESSION_TOKEN"]
    else:
        AWS_SESSION_TOKEN = None
    try:
        yield
    finally:
        if AWS_ACCESS_KEY_ID is not None:
            os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY_ID
        if AWS_SECRET_ACCESS_KEY is not None:
            os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_ACCESS_KEY
        if AWS_SESSION_TOKEN is not None:
            os.environ["AWS_SESSION_TOKEN"] = AWS_SESSION_TOKEN


class ObpAuthProvider(object):
    name = "obp"

    @staticmethod
    def get_client(
        module, with_error=False, role_arn=None, session_vars=None, client_params=None
    ):
        if client_params is None:
            client_params = {}

        import boto3
        import botocore
        from botocore.exceptions import ClientError
        from metaflow_extensions.outerbounds.plugins.auth_server import get_token

        from hashlib import sha256
        from metaflow.util import get_username

        user = get_username()

        token_info = get_token("/generate/aws")

        # Write token to a file. The file name is derived from the user name
        # so it works with multiple users on the same machine.
        #
        # We hash the user name so we don't have to deal with special characters
        # in the file name and the file name is not exposed to the user
        # anyways, so it doesn't matter that its a little ugly.
        token_file = "/tmp/obp_token." + sha256(user.encode("utf-8")).hexdigest()[:16]

        # Write to a temp file then rename to avoid a situation when someone
        # tries to read the file after it was open for writing (and truncated)
        # but before the token was written to it.
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write(token_info["token"])
            tmp_token_file = f.name
        os.rename(tmp_token_file, token_file)

        os.environ["AWS_WEB_IDENTITY_TOKEN_FILE"] = token_file
        os.environ["AWS_ROLE_ARN"] = token_info["role_arn"]

        # Enable regional STS endpoints. This is the new recommended way
        # by AWS [1] and is the more performant way.
        # [1] https://docs.aws.amazon.com/sdkref/latest/guide/feature-sts-regionalized-endpoints.html
        os.environ["AWS_STS_REGIONAL_ENDPOINTS"] = "regional"
        if token_info.get("region"):
            os.environ["AWS_DEFAULT_REGION"] = token_info["region"]

        with hide_access_keys():
            if role_arn:
                session = boto3.session.Session()
                fetcher = botocore.credentials.AssumeRoleCredentialFetcher(
                    client_creator=session._session.create_client,
                    source_credentials=session._session.get_credentials(),
                    role_arn=role_arn,
                    extra_args={},
                )
                creds = botocore.credentials.DeferredRefreshableCredentials(
                    method="assume-role", refresh_using=fetcher.fetch_credentials
                )
                botocore_session = botocore.session.Session(session_vars=session_vars)
                botocore_session._credentials = creds
                session = boto3.session.Session(botocore_session=botocore_session)
                if with_error:
                    return session.client(module, **client_params), ClientError
                else:
                    return session.client(module, **client_params)
            if with_error:
                return boto3.client(module, **client_params), ClientError
            else:
                return boto3.client(module, **client_params)


AWS_CLIENT_PROVIDERS_DESC = [("obp", ".ObpAuthProvider")]


class ObpAzureAuthProvider(object):
    name = "obp"

    @staticmethod
    def create_cacheable_azure_credential(*args, **kwargs):
        """azure.identity.DefaultAzureCredential is not readily cacheable in a dictionary
        because it does not have a content based hash and equality implementations.

        We implement a subclass CacheableDefaultAzureCredential to add them.

        We need this because credentials will be part of the cache key in _ClientCache.
        """
        from azure.identity import WorkloadIdentityCredential

        from metaflow_extensions.outerbounds.plugins.auth_server import get_token

        class CacheableDefaultAzureCredential(WorkloadIdentityCredential):
            def __init__(self, *args, **kwargs):
                super(CacheableDefaultAzureCredential, self).__init__(*args, **kwargs)
                # Just hashing all the kwargs works because they are all individually
                # hashable as of 7/15/2022.
                #
                # What if Azure adds unhashable things to kwargs?
                # - We will have CI to catch this (it will always install the latest Azure SDKs)
                # - In Metaflow usage today we never specify any kwargs anyway. (see last line
                #   of the outer function.
                self._hash_code = hash((args, tuple(sorted(kwargs.items()))))

            def __hash__(self):
                return self._hash_code

            def __eq__(self, other):
                return hash(self) == hash(other)

        from hashlib import sha256
        from metaflow.util import get_username

        user = get_username()

        token_info = get_token("/generate/azure")
        token_file = "/tmp/obp_token." + sha256(user.encode("utf-8")).hexdigest()[:16]

        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write(token_info["token"])
            tmp_token_file = f.name
        os.rename(tmp_token_file, token_file)
        return CacheableDefaultAzureCredential(
            tenant_id=token_info["azureTenantId"],
            client_id=token_info["azureClientId"],
            token_file_path=token_file,
        )


AZURE_CLIENT_PROVIDERS_DESC = [("obp", ".ObpAzureAuthProvider")]

import threading
import time

_gcp_client_cache = dict()


def _get_cache_key():
    return os.getpid(), threading.get_ident()


class ObpGcpAuthProvider(object):
    name = "obp"

    @staticmethod
    def get_gs_storage_client(*args, **kwargs):

        import sys
        from metaflow_extensions.outerbounds.plugins.auth_server import get_token

        cache_key = _get_cache_key()
        if _gcp_client_cache.get(cache_key):
            # Don't cache the client for more than 5 minutes as it may have
            # expired.
            if _gcp_client_cache[cache_key]._created_at < time.time() - 300:
                del _gcp_client_cache[cache_key]
            else:
                return _gcp_client_cache[cache_key]

        from hashlib import sha256
        from metaflow.util import get_username

        user = get_username()

        token_info = get_token("/generate/gcp")
        token_file = "/tmp/obp_token." + sha256(user.encode("utf-8")).hexdigest()[:16]
        credentials_file = (
            "/tmp/obp_credentials." + sha256(user.encode("utf-8")).hexdigest()[:16]
        )

        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write(token_info["token"])
            tmp_token_file = f.name
        os.rename(tmp_token_file, token_file)

        credentials_json = {
            "type": "external_account",
            "audience": f"//iam.googleapis.com/projects/{token_info['gcpProjectNumber']}/locations/global/workloadIdentityPools/{token_info['gcpWorkloadIdentityPool']}/providers/{token_info['gcpWorkloadIdentityPoolProvider']}",
            "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
            "token_url": "https://sts.googleapis.com/v1/token",
            "service_account_impersonation_url": f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{token_info['gcpServiceAccountEmail']}:generateAccessToken",
            "credential_source": {
                "file": token_file,
                "format": {"type": "text"},
            },
        }

        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write(json.dumps(credentials_json))
            tmp_credentials_file = f.name
        os.rename(tmp_credentials_file, credentials_file)

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file
        from google.cloud import storage

        storage_client = storage.Client(project=token_info["gcpProjectId"])
        storage_client._created_at = time.time()
        _gcp_client_cache[cache_key] = storage_client
        return storage_client

    @staticmethod
    def get_credentials(scopes, *args, **kwargs):
        import google.auth

        return google.auth.default(scopes=scopes)


GCP_CLIENT_PROVIDERS_DESC = [("obp", ".ObpGcpAuthProvider")]
CLIS_DESC = [("nvcf", ".nvcf.nvcf_cli.cli")]
STEP_DECORATORS_DESC = [("nvidia", ".nvcf.nvcf_decorator.NvcfDecorator")]
FLOW_DECORATORS_DESC = [("nim", ".nim.NimDecorator")]
