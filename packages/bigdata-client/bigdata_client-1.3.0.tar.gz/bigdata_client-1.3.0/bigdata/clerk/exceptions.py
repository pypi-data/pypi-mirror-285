from functools import wraps


class ClerkAuthError(Exception):
    """Base exception"""


class ClerkAuthUnsupportedError(ClerkAuthError):
    """For handling unsupported features"""


class ClerkUnexpectedSignInParametersError(ClerkAuthError):
    """For handling sign in kwargs"""


class ClerkInvalidCredentialsError(ClerkAuthError):
    """When the sign in process fails"""


def raise_errors_as_clerk_errors(func):
    """
    Try/except to raise BaseClerkError. Decorator to be used
    for the methods that are exposed to the user.

    Args:
        func:

    Returns:

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, ClerkAuthError):
                raise e
            raise ClerkAuthError(e) from e

    return wrapper
