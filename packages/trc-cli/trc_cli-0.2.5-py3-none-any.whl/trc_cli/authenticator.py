import datetime
import logging

import jwt
import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
    wait_random,
)

from trc_cli.exceptions import LeanIXAPIAuthenticatorException

logger = logging.getLogger('main')


class LeanIXAPIAuthenticator:
    _api_token: str
    _base_url: str
    _last_refresh_time: datetime.datetime | None
    _session: requests.Session
    _user_agent: str
    _access_token: str = None
    _refresh_threshold: int = 3600
    workspace_information: dict
    request_timeout: int = 10

    def __init__(
        self, api_token: str, base_url: str, user_agent: str, session: requests.Session
    ) -> None:
        self._api_token = api_token
        self._base_url = base_url
        self._user_agent = user_agent
        self._last_refresh_time = None
        self._session = session

    @property
    def session(self) -> requests.Session:
        return self._session

    @property
    def request_headers(self) -> dict:
        return {
            "User-Agent": self._user_agent,
            "Authorization": f"Bearer {self.access_token}",
        }

    @property
    def token_has_expired(self) -> bool:
        """Checks if the access token is expired based on the refresh threshold.

        Returns:
            bool: True if the token is expired, False otherwise.
        """

        return self._last_refresh_time is None or (
            datetime.datetime.now() - self._last_refresh_time
        ) > datetime.timedelta(seconds=self._refresh_threshold)

    @property
    def access_token(self) -> str:
        """Obtains access token needed for authentication.
        This function first checks if an access token exists and it's not expired.
        If the access token doesn't exist or it's expired, it refreshes the token
        by calling refresh_token() method.

        Returns:
            str: The obtained access token string for authentication.
        """
        if not self._access_token or self.token_has_expired:
            self.refresh_token()

        return self._access_token

    def retrieve_information_from_token(self):
        """Retrieve workspace and user role information from the access token.

        Args:
            access_token (str): The access token as provided by MTM

        Returns:
            dict: A dictionary with the user role and workspace information.
        """
        try:
            decoded_jwt = jwt.decode(self.access_token, options={
                                     "verify_signature": False})
            workspace_information = {
                "workspace_id": decoded_jwt["principal"]["permission"]["workspaceId"],
                "workspace_name": decoded_jwt["principal"]["permission"][
                    "workspaceName"
                ],
                "role": decoded_jwt["principal"]["role"],
                "instance_url": decoded_jwt['instanceUrl']
            }

            return workspace_information
        except jwt.DecodeError as e:
            logger.error(f"Failed to decode JWT: {e}")
            raise LeanIXAPIAuthenticatorException(
                f"Failed to decode JWT: {e}") from e
        except KeyError as e:
            logger.error(f"Failed to parse decoded JWT: {e}")
            raise LeanIXAPIAuthenticatorException(
                f"Failed to obtain role and workspace information from decoded JWT: {
                    e}"
            ) from e

    @retry(
        retry=retry_if_exception_type(requests.RequestException),
        stop=stop_after_attempt(3),
        wait=wait_fixed(3) + wait_random(0, 2),
    )
    def refresh_token(self) -> str:
        """Function to obtain an access token for secure API communication.

        This function sends a POST request to authenticate to the base url and get the access token.
        API token is required for this operation.

        Returns:
            str: The access token required for secure API operations.

        Raises:
            Exception: If no valid API token is provided to the function.
            HTTPError: If the attempt to authenticate to the base url results in an HTTP error.
        """
        oauth2_url = f"https://{self._base_url}.leanix.net/services/mtm/v1/oauth2/token"
        if not self._api_token:
            raise Exception("A valid API token is required")
        logger.info(f"Obtaining new access token from {oauth2_url}")
        response = self._session.post(
            oauth2_url,
            auth=("apitoken", self._api_token),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": self._user_agent},
            timeout=self.request_timeout,
        )

        if response.status_code == 401:
            raise Exception("A valid API token is required")
        response.raise_for_status()
        self._access_token = response.json().get("access_token")
        self._last_refresh_time = datetime.datetime.now()
        self.retrieve_information_from_token()
