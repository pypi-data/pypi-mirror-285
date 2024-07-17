from .auth_decorators import AuthDecorators
from functools import wraps


class AuthFactory(object):
    def __init__(self, auth_type, config) -> None:
        self.auth_type = auth_type
        self.auth_obj = self.get_auth()
        self.config = config

    def get_auth(self):
        if self.auth_type in ["ms-oauth2"]:
            from .auth.ms_oauth2 import MS_OAuth2
            return MS_OAuth2()

    def login_handler(self):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                @self.auth_obj.login_handler(config=self.config)
                def login_handler(*args, **kwargs):
                    assert ("auth_url" in kwargs)
                    return kwargs["auth_url"]
                result = login_handler()

                # kwargs["auth_url"] = result
                _result = f(*args, **kwargs)
                return result
            return wrapper
        return decorator

    def logout_handler(self):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                @self.auth_obj.logout_handler(config=self.config)
                def logout_handler(*args, **kwargs):
                    assert ("logout_uri" in kwargs)
                    return kwargs["logout_uri"]
                result = logout_handler()

                # kwargs["logout_uri"] = result
                _result = f(*args, **kwargs)
                return result
            return wrapper
        return decorator

    def callback_handler(self, response_code: str = None, response_state: str = None):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                # If states and code is provided via kwargs, then that
                # will be treated as priority else will use from function
                # parameters.
                if "kwargs" in kwargs and "response_code" in kwargs["kwargs"]:
                    _response_code = kwargs["kwargs"]["response_code"]
                else:
                    _response_code = response_code
                if "kwargs" in kwargs and "response_state" in kwargs["kwargs"]:
                    _response_state = kwargs["kwargs"]["response_state"]
                else:
                    _response_state = response_state

                @self.auth_obj.callback_handler(config=self.config,
                                                response_code=_response_code,
                                                response_state=_response_state)
                def callback_handler(*args, **kwargs):
                    assert ("id_token" in kwargs)
                    assert ("access_token" in kwargs)
                    assert ("refresh_token" in kwargs)

                    ret = {
                        "id_token": kwargs["id_token"],
                        "access_token": kwargs["access_token"],
                        "refresh_token": kwargs["refresh_token"]
                    }

                    return ret
                result = callback_handler()

                # kwargs["id_token"] = result
                _result = f(*args, **kwargs)
                return result
            return wrapper
        return decorator
