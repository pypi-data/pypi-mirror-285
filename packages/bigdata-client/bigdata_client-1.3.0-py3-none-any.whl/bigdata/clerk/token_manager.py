from http import HTTPStatus
from typing import Optional

import requests.exceptions

from bigdata.clerk.authenticators.base_instance import ClerkInstanceBase
from bigdata.clerk.exceptions import raise_errors_as_clerk_errors


class ClerkTokenManager:
    def __init__(
        self,
        clerk_authenticator_instance: ClerkInstanceBase,
        clerk_jwt_template_name: Optional[str] = None,
    ):
        """
        Class responsible from getting a JWT and refreshing it from Clerk.
        When the session expires it refreshes it to get a new JWT.

        Args:
            clerk_authenticator_instance: Contains the authorized session with Clerk.
            clerk_jwt_template_name:
        """
        self._clerk_jwt_template_name = clerk_jwt_template_name
        self._clerk_frontend_api_url = (
            clerk_authenticator_instance.clerk_frontend_api_url
        )
        self._session = clerk_authenticator_instance.session
        self._clerk_session = clerk_authenticator_instance.clerk_session
        self._clerk_authenticator_instance = clerk_authenticator_instance
        self._login_strategy = clerk_authenticator_instance.login_strategy
        self._jwt: str = ""

    @raise_errors_as_clerk_errors
    def refresh_session_token(self) -> str:
        """
        To be called when the token is invalid. It refreshes
        the clerk session if it expired.
        Returns:
            jwt
        """
        try:
            self._jwt = self._get_new_session_token()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == HTTPStatus.UNAUTHORIZED:
                self._refresh_token_manager()
                self._jwt = self._get_new_session_token()
        return self._jwt

    def get_session_token(self) -> str:
        """Returns the last generated JWT"""
        return self._jwt

    def _get_new_session_token(self) -> str:
        url = f"{self._clerk_frontend_api_url}client/sessions/{self._clerk_session}/tokens"
        if self._clerk_jwt_template_name:
            url = f"{url}/{self._clerk_jwt_template_name}"
        response = self._session.post(url=url)
        response.raise_for_status()
        return response.json()["jwt"]

    def _refresh_token_manager(self) -> None:
        params = self._clerk_authenticator_instance.get_new_token_manager_params(
            self._clerk_frontend_api_url,
            self._login_strategy,
            proxies=self._session.proxies,
        )
        self._session = params.session
        self._clerk_session = params.clerk_session
