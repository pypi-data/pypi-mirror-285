from typing import Optional

from bigdata.clerk.authenticators.dev_instance import ClerkAuthenticatorDevInstance
from bigdata.clerk.authenticators.production_instance import (
    ClerkAuthenticatorProductionInstance,
)
from bigdata.clerk.constants import ClerkInstanceType
from bigdata.clerk.exceptions import ClerkUnexpectedSignInParametersError
from bigdata.clerk.models import SignInStrategyType
from bigdata.clerk.sign_in_strategies.password import PasswordStrategy
from bigdata.clerk.token_manager import ClerkTokenManager

TEMPLATE_NAME = "bigdata_sdk"


def token_manager_factory(
    instance_type: ClerkInstanceType,
    sign_in_strategy: SignInStrategyType,
    clerk_frontend_url: str,
    proxies: Optional[dict],
    **sign_in_kwargs,
) -> ClerkTokenManager:
    """
    Factory to be used by Clerk consumers

    Args:
        instance_type: Instance type DEV/PROD
        sign_in_strategy: PASSWORD
        clerk_frontend_url: URL of the Clerk frontend
        proxies: dict with the proxies in format {protocol: url}
        **sign_in_kwargs: extra params required by the factory

    Returns:
        ClerkTokenManager is used for obtaining JWTs

    Raises:
        ClerkUnexpectedSignInParameters
    """

    strategy = _get_strategy(sign_in_strategy, sign_in_kwargs)
    if instance_type == ClerkInstanceType.DEV:
        clerk_instance = ClerkAuthenticatorDevInstance.login_and_activate_session(
            clerk_frontend_url,
            strategy,
            proxies=proxies,
        )
    elif instance_type == ClerkInstanceType.PROD:
        clerk_instance = (
            ClerkAuthenticatorProductionInstance.login_and_activate_session(
                clerk_frontend_url,
                strategy,
                proxies=proxies,
            )
        )
    else:
        raise ValueError(f"Unknown clerk instance: {instance_type}")

    return ClerkTokenManager(
        clerk_authenticator_instance=clerk_instance,
        clerk_jwt_template_name=TEMPLATE_NAME,
    )


def _get_strategy(sign_in_strategy: SignInStrategyType, kwargs: dict):
    if sign_in_strategy == SignInStrategyType.PASSWORD:
        return _get_password_strategy(kwargs)

    raise ValueError(f"Unknown sign in strategy: {sign_in_strategy}")


def _get_password_strategy(kwargs: dict):
    if set(kwargs) != {"password", "email"}:
        raise ClerkUnexpectedSignInParametersError

    return PasswordStrategy(email=kwargs["email"], password=kwargs["password"])
