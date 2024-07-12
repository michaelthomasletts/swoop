__all__ = ["AutoRefreshableSession"]

from boto3 import Session
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session


class AutoRefreshableSession:
    """Returns a boto3 Session object which refreshes automatically, no extra steps required.

    This object is useful for long-running processes where temporary credentials may expire between iterations.

    To use this class, you must have `~/.aws/config` or `~/.aws/credentials` on your machine!

    Attributes
    ----------
    region : str
        AWS region name.
    role_arn : str
        AWS role ARN.
    session_name : str
        Name for session.
    ttl : int, optional
        Number of seconds until temporary credentials expire, default 900
    
    Other Attributes
    ----------------
    **kwargs : dict
        Optional keyword arguments for initializing the boto3 `Session` object.

    Methods
    -------
    get_session
        Returns a boto3 Session object with credentials which refresh automatically.
    
    Notes
    -----
    boto3 employs a variety of methods (in order) to identify credentials:

    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    This class assumes that `~/.aws` exists with `/config` or `/credentials`!
    
    Examples
    --------
    Here's how to initialize the `boto3.Client.S3` object:

    >>> from swoop import AutoRefreshableSession
    >>> ars = AutoRefreshableSession(region="us-east-1", role_arn="...", session_name="test")
    >>> session = ars.get_session()
    >>> s3_client = session.client(service_name="s3")
    """

    def __init__(
        self, region: str, role_arn: str, session_name: str, ttl: int = 900, **kwargs
    ):
        self.region = region
        self.role_arn = role_arn
        self.session_name = session_name
        self.ttl = ttl
        self.kwargs = kwargs

    def _get_credentials(self) -> dict:
        """Returns temporary credentials via AWS STS.

        Returns
        -------
        dict
            AWS temporary credentials.
        """

        session = Session(region_name=self.region, **self.kwargs)
        client = session.client(service_name="sts", region_name=self.region)
        response = client.assume_role(
            RoleArn=self.role_arn,
            RoleSessionName=self.session_name,
            DurationSeconds=self.ttl,
        )
        return {
            "access_key": response.get("AccessKeyId"),
            "secret_key": response.get("SecretAccessKey"),
            "token": response.get("SessionToken"),
            "expiry_time": response.get("Expiration").isoformat(),
        }

    def get_session(self) -> "Session":
        """Returns a boto3 `Session` object with credentials which refresh automatically.

        Returns
        -------
        Session
            boto3 `Session` object.
        """

        credentials = RefreshableCredentials.create_from_metadata(
            metadata=self._get_credentials(),
            refresh_using=self._get_credentials,
            method="sts-assume-role",
        )
        session = get_session()
        # https://github.com/boto/botocore/blob/f8a1dd0820b548a5e8dc05420b28b6f1c6e21154/botocore/session.py#L143
        session._credentials = credentials
        return Session(botocore_session=session)