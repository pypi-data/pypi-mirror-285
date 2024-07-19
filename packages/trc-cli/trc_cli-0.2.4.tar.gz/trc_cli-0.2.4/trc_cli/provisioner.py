import logging
import time

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
    wait_random,
)

from trc_cli.authenticator import LeanIXAPIAuthenticator
from trc_cli.constants import FEATURE_FLAGS, WORKSPACE_READINESS_FIELD
from trc_cli.exceptions import LeanIXDemoProvisionerException

logger = logging.getLogger('main')


class LeanIXDemoProvisioner:
    """Provisions a demo workspace for tech discovery"""

    _base_url: str
    _authenticator: LeanIXAPIAuthenticator
    _user_agent: str = "LeanIXTechDiscoveryDemoProvisioner"
    _request_timeout: int = 10
    _workspace_info: dict
    session: requests.Session

    def __init__(
        self, base_url: str, api_token: str, session: requests.Session | None = None
    ):
        self._base_url = base_url
        self.session = session or requests.Session()
        self._authenticator = LeanIXAPIAuthenticator(
            api_token=api_token,
            base_url=base_url,
            user_agent=self._user_agent,
            session=self.session,
        )
        self._workspace_info = self._authenticator.retrieve_information_from_token()

    def prepare_request(self):
        """Prepares the request details"""
        self.session.headers = {
            "User-Agent": self._user_agent,
            "Authorization": f"Bearer {self._authenticator.access_token}",
        }

    @retry(
        retry=retry_if_exception_type(requests.RequestException),
        stop=stop_after_attempt(3),
        wait=wait_fixed(3) + wait_random(0, 2),
    )
    def enable_feature_flags(self):
        """Enables the necessary feature flags for tech discovery support in a workspace"""
        features_endpoint = (
            f"https://{self._base_url}.leanix.net/services/mtm/v1/customFeatures"
        )
        self.prepare_request()
        workspace_id = self._workspace_info["workspace_id"]
        for feature_flag in FEATURE_FLAGS:
            request_payload = {
                "status": "ENABLED",
                "feature": {
                    "id": feature_flag,
                },
                "workspace": {"id": workspace_id},
            }
            logger.info(
                f"Enabling feature flag: {
                    feature_flag} for Workspace: {workspace_id}"
            )
            response = self.session.post(
                url=features_endpoint,
                json=request_payload,
                timeout=self._request_timeout,
            )
            try:
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(
                    f"Failed to enable feature: {
                        feature_flag} for workspace id: {workspace_id}"
                )
                raise LeanIXDemoProvisionerException(
                    f"Failed to enable feature: {feature_flag} for workspace id: {
                        workspace_id} reason: {e}"
                ) from e
            else:
                logger.info(
                    f"Enabled feature: {
                        feature_flag} for workspace: {workspace_id}"
                )

    @retry(
        retry=retry_if_exception_type(requests.RequestException),
        stop=stop_after_attempt(3),
        wait=wait_fixed(3) + wait_random(0, 2),
    )
    def wait_for_workspace_readiness(self) -> bool:
        """Checks if the workspace has been provisioned properly

        Returns:
            bool: True if the workspace was provisioned, False if not
        """
        data_model_endpoint = f"https://{
            self._base_url}.leanix.net/services/pathfinder/v1/models/dataModel"
        self.prepare_request()
        workspace_id = self._workspace_info["workspace_id"]
        while True:
            response = self.session.get(
                url=data_model_endpoint, timeout=self._request_timeout
            )
            try:
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"Failed to fetch workspace information: {e}")
                raise requests.RequestException(
                    f"Failed to fetch information for workspace id: {
                        workspace_id}, reason: {e}"
                ) from e
            else:
                if (
                    WORKSPACE_READINESS_FIELD
                    not in response.json()["data"]["factSheets"]["Application"][
                        "fields"
                    ].keys()
                ):
                    logger.info(
                        f"Workspace: {workspace_id} not ready yet, will re-try"
                    )
                    time.sleep(60)
                else:
                    logger.info(
                        f"Workspace: {workspace_id} has been provisioned")
                    break
