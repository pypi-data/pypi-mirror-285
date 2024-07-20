import re
import sys
import textwrap

import requests

from ts_cli.config.api_config import ApiConfig
from ts_cli.config.publish_artifact_config import PublishArtifactConfig
from ts_cli.util.emit import emit_critical, emit_error

REQUEST_TIMEOUT_SECONDS = 60


class TsApiError(Exception):
    """
    For TsApi Failures
    """


class TsApi:
    """
    A simple adapter for the Tetrascience public api
    At the moment, only artifact endpoints are supported
    """

    def __init__(self, config: ApiConfig):
        self.config = config

    @property
    def _api_url(self):
        return self.config.api_url

    @property
    def _request_defaults(self):
        return {
            "verify": self.config.ignore_ssl is not True,
            "headers": self._get_headers(),
        }

    def _get_headers(self):
        headers = {"x-org-slug": self.config.org}
        ts_auth = self.config.auth_token
        if re.compile(r"^([a-z0-9]+-)+[a-z0-9]+$").match(ts_auth, re.IGNORECASE):
            headers["x-api-key"] = ts_auth
        else:
            headers["ts-auth-token"] = ts_auth
        return headers

    @staticmethod
    def _api_error(response):
        try:
            body = response.json()
            message = body.get("message", "Unknown")
            emit_error(f"Response from platform: \n{textwrap.indent(message, '  ')}")
            emit_critical("Exiting")
        except Exception:
            print(response.text, file=sys.stderr, flush=True)
        return TsApiError(f"HTTP status: {response.status_code}, url: {response.url}")

    def upload_artifact(self, config: PublishArtifactConfig, artifact_bytes):
        """
        :param config: Artifact configuration
        :param artifact_bytes: ZIP file bytes
        :return: API response body
        """
        type_to_url = {
            "ids": "ids",
            "protocol": "master-scripts",
            "task-script": "task-scripts",
            "tetraflow": "tetraflows",
        }
        url = f"{self._api_url}/artifact/{type_to_url[config.type]}/{config.namespace}/{config.slug}/{config.version}"
        params = {
            **({"force": "true"} if config.force else {}),
        }
        response = requests.post(
            url,
            **self._request_defaults,
            params=params,
            data=artifact_bytes,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code < 400:
            return response.json()
        raise TsApi._api_error(response)

    def get_task_script_build_info(self, task_id: str):
        """
        :param task_id: ID of the task build information to retrieve
        :return: API response body
        """
        url = f"{self._api_url}/artifact/builds/{task_id}"
        response = requests.get(
            url, **self._request_defaults, timeout=REQUEST_TIMEOUT_SECONDS
        )
        if response.status_code < 400:
            return response.json()
        raise TsApi._api_error(response)

    def get_task_script_build_logs(self, task_id: str, params):
        """
        :param task_id:
        :param params:
        :return:
        """
        url = f"{self._api_url}/artifact/build-logs/{task_id}"
        response = requests.get(
            url,
            **self._request_defaults,
            params={k: v for k, v in params.items() if v is not None},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code < 400:
            return response.json()
        raise TsApi._api_error(response)
