from http import HTTPStatus
from typing import Optional

import requests

from bigdata.clerk.authenticators.base_instance import ClerkInstanceBase
from bigdata.clerk.exceptions import (
    ClerkAuthError,
    ClerkAuthUnsupportedError,
    ClerkInvalidCredentialsError,
    raise_errors_as_clerk_errors,
)
from bigdata.clerk.models import RefreshedTokenManagerParams
from bigdata.clerk.sign_in_strategies.base import SignInStrategy
from bigdata.clerk.sign_in_strategies.password import PasswordStrategy


class ClerkAuthenticatorDevInstance(ClerkInstanceBase):
    @classmethod
    @raise_errors_as_clerk_errors
    def login_and_activate_session(
        cls,
        clerk_frontend_api_url: str,
        login_strategy: SignInStrategy,
        proxies: Optional[dict] = None,
    ) -> "ClerkAuthenticatorDevInstance":
        """
        Performs the authentication flow against Clerk with the chosen strategy by creating
        a session then choosing the first organization the user is a member of (activation).
        Args:
            clerk_frontend_api_url:
            login_strategy:
            proxies: dict with the proxies in format {protocol: url}

        Returns: ClerkAuthenticatorDevInstance
        """
        if not isinstance(login_strategy, PasswordStrategy):
            raise ClerkAuthUnsupportedError("Unsupported SignInStrategy")
        dev_browser_token = ClerkAuthenticatorDevInstance._get_dev_browser_token(
            clerk_frontend_api_url, proxies
        )
        session = requests.Session()
        if proxies:
            session.proxies.update(proxies)
        session.params = {"__dev_session": dev_browser_token}
        clerk_session = ClerkAuthenticatorDevInstance._sign_in(
            session, clerk_frontend_api_url, login_strategy
        )
        ClerkAuthenticatorDevInstance._activate_session(
            session, clerk_session, clerk_frontend_api_url
        )

        return ClerkAuthenticatorDevInstance(
            clerk_frontend_api_url=clerk_frontend_api_url,
            login_strategy=login_strategy,
            session=session,
            clerk_session=clerk_session,
        )

    @staticmethod
    def get_new_token_manager_params(
        clerk_frontend_api_url: str,
        login_strategy: SignInStrategy,
        proxies: Optional[dict],
    ):
        dev_browser_token = ClerkAuthenticatorDevInstance._get_dev_browser_token(
            clerk_frontend_api_url, proxies
        )
        session = requests.Session()
        if proxies:
            session.proxies.update(proxies)
        session.params = {"__dev_session": dev_browser_token}
        clerk_session = ClerkAuthenticatorDevInstance._sign_in(
            session, clerk_frontend_api_url, login_strategy
        )
        ClerkAuthenticatorDevInstance._activate_session(
            session, clerk_session, clerk_frontend_api_url
        )
        return RefreshedTokenManagerParams(session=session, clerk_session=clerk_session)

    @staticmethod
    def _get_dev_browser_token(
        clerk_frontend_api_url: str, proxies: Optional[dict]
    ) -> str:
        """
        This is used to authenticate Development Instances with the DevBrowser scheme.
        It must be set before making any request to a dev instance, even for endpoints that are public.
        """
        response = requests.post(
            url=f"{clerk_frontend_api_url}dev_browser", proxies=proxies
        )
        response.raise_for_status()

        return response.json()["token"]

    @staticmethod
    def _sign_in(
        session: requests.Session, clerk_frontend_api_url: str, strategy: SignInStrategy
    ) -> str:
        url = f"{clerk_frontend_api_url}client/sign_ins"
        response = session.post(
            url=url, data=strategy.get_payload(), headers=strategy.get_headers()
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
                raise ClerkInvalidCredentialsError
            raise ClerkAuthError from e

        return response.json()["response"]["created_session_id"]
