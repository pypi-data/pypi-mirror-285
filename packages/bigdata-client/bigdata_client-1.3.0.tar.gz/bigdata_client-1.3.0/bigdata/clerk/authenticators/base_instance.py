from abc import ABC, abstractmethod
from typing import Optional

import requests

from bigdata.clerk.models import RefreshedTokenManagerParams
from bigdata.clerk.sign_in_strategies.base import SignInStrategy


class ClerkInstanceBase(ABC):
    def __init__(
        self,
        clerk_frontend_api_url: str,
        login_strategy: SignInStrategy,
        session: requests.Session,
        clerk_session: str,
    ):
        self.clerk_frontend_api_url = clerk_frontend_api_url
        self.login_strategy = login_strategy
        self.session = session
        self.clerk_session = clerk_session

    @classmethod
    @abstractmethod
    def login_and_activate_session(
        cls,
        clerk_frontend_api_url: str,
        login_strategy: SignInStrategy,
    ):
        """
        Performs the authentication flow against Clerk with the chosen strategy by creating
        a session then choosing the first organization the user is a member of (activation).
        Returns a new instance

        Args:
            clerk_frontend_api_url:
            login_strategy:

        """

    @staticmethod
    @abstractmethod
    def get_new_token_manager_params(
        clerk_frontend_api_url: str,
        login_strategy: SignInStrategy,
        proxies: Optional[dict],
    ) -> RefreshedTokenManagerParams: ...

    @staticmethod
    def _activate_session(
        session: requests.Session, clerk_session: str, clerk_frontend_api_url: str
    ):
        # Get user's org
        url = f"{clerk_frontend_api_url}me/organization_memberships"
        response = session.get(url=url)
        response.raise_for_status()
        # The user is assumed to belong to 1 org only
        organization_to_activate = response.json()["response"][0]["organization"]["id"]

        # Activate the organization
        url = f"{clerk_frontend_api_url}client/sessions/{clerk_session}/touch"
        response = session.post(
            url=url,
            headers={"content-type": "application/x-www-form-urlencoded"},
            data=f"active_organization_id={organization_to_activate}",
        )
        response.raise_for_status()
