from abc import ABC, abstractmethod
import datetime
import jwt
from typing import Callable


class TokenProvider(ABC):
    """
    Abstract base class for logic that acquires auth tokens.
    """
    @abstractmethod
    def __call__(self) -> str:
        """
        Get implementation specific token.

        Returns
        -------
        str
            Auth token.
        """
        raise NotImplementedError


class ConstantTokenProvider(TokenProvider):
    """
    Wrapper around a token that was externally acquired by the user.

    Parameters
    ----------
    token : str
        Token that will be supplied upon requst.
    """
    def __init__(self, token):
        self.token = token

    def __call__(self):
        """
        Get token.

        Returns
        -------
        str
            Fixed token provided by user during instantiation.
        """
        return self.token


class SynapseTokenProvider(TokenProvider):
    """
    Acquire an auth token from within a Trident workspace.
    """
    def __call__(self):
        """
        Get token from within a Trident workspace.

        Returns
        -------
        str
            Token acquired from Trident libraries.
        """
        try:
            from synapse.ml.fabric.token_utils import TokenUtils
            return TokenUtils().get_aad_token()
        except ImportError:
            try:
                from trident_token_library_wrapper import PyTridentTokenLibrary
                return PyTridentTokenLibrary.get_access_token("pbi")
            except ImportError:
                raise RuntimeError("No token_provider specified and unable to obtain token from the environment")


def _get_token_expiry_raw_timestamp(token: str) -> int:
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("exp", 0)
    except jwt.DecodeError:
        # Token is not a valid token (ex: using myToken in tests)
        return 0


def _get_token_seconds_remaining(token: str) -> int:
    exp_time = _get_token_expiry_raw_timestamp(token)
    now_epoch = (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()
    return int(exp_time - now_epoch)


def _get_token_expiry_utc(token: str) -> str:
    exp_time = _get_token_expiry_raw_timestamp(token)
    return str(datetime.datetime.utcfromtimestamp(exp_time))


def create_on_access_token_expired_callback(token_provider: TokenProvider) -> Callable:
    from System import DateTimeOffset
    from Microsoft.AnalysisServices import AccessToken

    # convert seconds to .NET date time
    def get_token_expiration_datetime(token):

        seconds = _get_token_seconds_remaining(token)

        return DateTimeOffset.UtcNow.AddSeconds(seconds)

    def get_access_token(old_token):
        token = token_provider()

        expiration = get_token_expiration_datetime(token)

        return AccessToken(token, expiration)

    return get_access_token
