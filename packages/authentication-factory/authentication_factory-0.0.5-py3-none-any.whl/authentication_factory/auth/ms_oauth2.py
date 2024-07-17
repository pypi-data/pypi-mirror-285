from ..auth_decorators import AuthDecorators
from functools import wraps


import msal
import jwt
import base64
import requests
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


class MS_OAuth2(AuthDecorators):

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def ensure_bytes(self, message):
        """
        This function will encode the string in UTF-8 format.
        :param message (str):   String to encode in string format.
        :return message:        If data is type of string will encode
                                in utf-8 fomrat else return as is.
        """

        if isinstance(message, str):
            message = message.encode('utf-8')
        return message

    @classmethod
    def decode_value(self, val):
        """
        This function will encode the string in UTF-8 format.
        :param message (str):   String to encode in string format.
        :return message:        If data is type of string will encode
                                in utf-8 fomrat else return as is.
        """
        decoded = base64.urlsafe_b64decode(self.ensure_bytes(val) + b'==')
        return int.from_bytes(decoded, 'big')

    @classmethod
    def rsa_pem_from_jwk(self, jwk):
        return RSAPublicNumbers(
            n=self.decode_value(jwk['n']),
            e=self.decode_value(jwk['e'])
        ).public_key(default_backend()).public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)

    @classmethod
    def get_public_key(self, jwk):
        return self.rsa_pem_from_jwk(jwk)

    def verify(self, token: str, client_id: str, tenant_id: str):
        """
        Verifies a JWT string's signature and validates reserved claims.
        Get the key id from the header, locate it in the Microsoft OAuth2 keys and verify
        the key
        :param token (str):         A signed JWS to be verified.
        :param access_token (str):  An access token string. If the "at_hash" claim
                                    is included in the
        :return id_token (dict):    The dict representation of the claims set,
                                    assuming the signature is valid and all
                                    requested data validation passes.
        """
        header = jwt.get_unverified_header(token)
        jwt_key = requests.get(
            "https://login.microsoftonline.com/common/discovery/v2.0/keys").json()["keys"]
        key = [k for k in jwt_key if k["kid"] == header['kid']][0]

        if "issuer" not in key:
            issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
        else:
            issuer = key["issuer"].replace(
                '{tenantid}', tenant_id)
        decoded = jwt.decode(jwt=token,
                             key=self.get_public_key(key),
                             verify=False,
                             options={"verify_signature": False},
                             algorithms=['RS256'],
                             audience=[client_id],
                             issuer=issuer)
        return decoded

    def build_ms_oauth2_app(self, authority, client_id, client_secret):
        msml_app = msal.ConfidentialClientApplication(
            client_id=client_id,
            authority=authority,
            client_credential=client_secret)
        return msml_app

    def build_ms_oauth2_url(self,
                            authority,
                            scopes,
                            state,
                            client_id,
                            client_secret,
                            redirect_uri):
        msml_app = self.build_ms_oauth2_app(authority=authority,
                                            client_id=client_id,
                                            client_secret=client_secret)
        req_url = msml_app.get_authorization_request_url(
            scopes=scopes,
            state=state,
            redirect_uri=redirect_uri)
        return req_url

    def login_handler(self, config: dict):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                assert("state" in config)
                assert("client_id" in config)
                assert("client_secret" in config)
                assert("tenant_id" in config)
                assert("redirect_uri" in config)

                tenant_id = config["tenant_id"]
                state = config["state"]
                client_id = config["client_id"]
                client_secret = config["client_secret"]
                redirect_uri = config["redirect_uri"]
                scope = [
                    "User.Read"] if not "scope" in config else config["scope"]
                authority = f"https://login.microsoftonline.com/{tenant_id}"

                auth_url = self.build_ms_oauth2_url(authority=authority,
                                                    scopes=scope,
                                                    state=state,
                                                    client_id=client_id,
                                                    client_secret=client_secret,
                                                    redirect_uri=redirect_uri)

                kwargs["auth_url"] = auth_url

                result = f(*args, **kwargs)
                return result
            return wrapper
        return decorator

    def logout_handler(self, config: dict):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                assert("tenant_id" in config)
                assert("signout_uri" in config)

                tenant_id = config["tenant_id"]
                signout_uri = config["signout_uri"]

                authority = f"https://login.microsoftonline.com/{tenant_id}"
                logout_uri = (f"{authority}/oauth2/v2.0/logout?"
                              f"post_logout_redirect_uri={signout_uri}")

                kwargs["logout_uri"] = logout_uri

                result = f(*args, **kwargs)
                return result
            return wrapper
        return decorator

    def callback_handler(self, config: dict, response_code: str, response_state: str):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                assert("tenant_id" in config)
                assert("signout_uri" in config)
                assert("state" in config)
                assert("client_id" in config)
                assert("client_secret" in config)
                assert("redirect_uri" in config)

                tenant_id = config["tenant_id"]
                state = config["state"]
                client_id = config["client_id"]
                client_secret = config["client_secret"]
                redirect_uri = config["redirect_uri"]
                authority = f"https://login.microsoftonline.com/{tenant_id}"
                scope = [
                    "User.Read"] if not "scope" in config else config["scope"]

                if not response_code or not response_state:
                    raise ("Not a valid Response code or Response state.")

                if state not in [response_state]:
                    raise ("Authentication state is not valid")

                msml_app = self.build_ms_oauth2_app(authority=authority,
                                                    client_id=client_id,
                                                    client_secret=client_secret)
                result = msml_app.acquire_token_by_authorization_code(response_code,
                                                                      scopes=scope,
                                                                      redirect_uri=redirect_uri)

                if "error" not in result:
                    id_token = self.verify(token=result.get("access_token"),
                                           client_id=client_id,
                                           tenant_id=tenant_id)

                kwargs["id_token"] = id_token
                kwargs["access_token"] = result["access_token"]
                kwargs["refresh_token"] = result["refresh_token"]

                result = f(*args, **kwargs)
                return result
            return wrapper
        return decorator
