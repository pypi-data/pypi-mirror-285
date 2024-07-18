from http import HTTPStatus
from typing import Optional, Tuple

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


class ClerkAuthenticatorProductionInstance(ClerkInstanceBase):

    @classmethod
    @raise_errors_as_clerk_errors
    def login_and_activate_session(
        cls,
        clerk_frontend_api_url: str,
        login_strategy: SignInStrategy,
        proxies: Optional[dict] = None,
    ) -> "ClerkAuthenticatorProductionInstance":
        """
        Performs the authentication flow against Clerk with the chosen strategy by creating
        a session then choosing the first organization the user is a member of (activation).

        Args:
            clerk_frontend_api_url:
            login_strategy:
            proxies: dict with the proxies in format {protocol: url}

        Returns: ClerkAuthenticatorProductionInstance
        """
        if not isinstance(login_strategy, PasswordStrategy):
            raise ClerkAuthUnsupportedError("Unsupported SignInStrategy")

        session = requests.Session()
        if proxies:
            session.proxies.update(proxies)
        clerk_session, clerk_jwt = ClerkAuthenticatorProductionInstance._sign_in(
            clerk_frontend_api_url, strategy=login_strategy, proxies=proxies
        )
        session.cookies.set("__client", clerk_jwt)
        ClerkAuthenticatorProductionInstance._activate_session(
            session, clerk_session, clerk_frontend_api_url
        )
        return ClerkAuthenticatorProductionInstance(
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
        clerk_session, clerk_jwt = ClerkAuthenticatorProductionInstance._sign_in(
            clerk_frontend_api_url, strategy=login_strategy, proxies=proxies
        )
        session = requests.Session()
        if proxies:
            session.proxies.update(proxies)
        session.cookies.set("__client", clerk_jwt)
        ClerkAuthenticatorProductionInstance._activate_session(
            session, clerk_session, clerk_frontend_api_url
        )
        return RefreshedTokenManagerParams(session=session, clerk_session=clerk_session)

    @staticmethod
    def _sign_in(
        clerk_frontend_api_url: str, strategy: SignInStrategy, proxies: Optional[dict]
    ) -> Tuple[str, str]:
        url = f"{clerk_frontend_api_url}client/sign_ins"
        response = requests.post(
            url=url,
            data=strategy.get_payload(),
            headers=strategy.get_headers(),
            proxies=proxies,
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
                raise ClerkInvalidCredentialsError
            raise ClerkAuthError from e

        return (
            response.json()["response"]["created_session_id"],
            response.headers["authorization"],
        )
