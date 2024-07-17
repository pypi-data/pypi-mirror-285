import functools
from http import HTTPStatus
from typing import Any
from typing import Self

from flask import Flask
from flask import jsonify
from flask.views import MethodView
from flask_jwt_extended import JWTManager as BaseJWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import current_user as jwt_current_user
from flask_jwt_extended import get_jwt
from flask_jwt_extended import jwt_required
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended.default_callbacks import default_expired_token_callback
from flask_jwt_extended.default_callbacks import default_invalid_token_callback
from flask_jwt_extended.default_callbacks import default_needs_fresh_token_callback
from flask_jwt_extended.default_callbacks import default_revoked_token_callback
from flask_jwt_extended.default_callbacks import default_token_verification_failed_callback
from flask_jwt_extended.default_callbacks import default_unauthorized_callback
from flask_jwt_extended.default_callbacks import default_user_lookup_error_callback

from .exception import abort


def admin_required():
    def wrapper(fn):
        @functools.wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["admin"]:
                return fn(*args, **kwargs)
            else:
                abort(code="PERMISSION_DENIED", msg="You have no permissions!", status_code=403)

        return decorator

    return wrapper


class JwtUser:
    def user_identity_loader(self) -> Any:
        raise NotImplementedError

    @classmethod
    def user_lookup_loader(cls, jwt_header: dict, jwt_data: dict) -> Self | None:
        raise NotImplementedError

    @staticmethod
    def login(**_):
        raise NotImplementedError

    @staticmethod
    def refresh_token(**_):
        raise NotImplementedError

    def generate_access_token(self):
        return create_access_token(self)

    def generate_refresh_token(self):
        return create_refresh_token(self)

    @classmethod
    def current_user(cls) -> Self:
        return jwt_current_user


class JWTManager(BaseJWTManager):
    def init_app(self, app: Flask, add_context_processor: bool = False) -> None:
        super().init_app(app, add_context_processor)
        self.autoload_user(app)
        self.rewrite_errorhandlers()

    def autoload_user(self, app: Flask):
        if self._user_identity_callback and self._user_lookup_callback:
            return

        models = [m.class_ for m in app.extensions["sqlalchemy"].Model._sa_registry.mappers]
        for model in models:
            if not issubclass(model, JwtUser):
                continue
            app.logger.info(f"Found jwt user model: {model}")
            self.user_identity_loader(lambda user: user.user_identity_loader())
            self.user_lookup_loader(model.user_lookup_loader)
            app.post("/login")(model.login)
            app.post("/refreshtoken")(jwt_required(refresh=True, locations="json")(model.refresh_token))

            break

    def rewrite_errorhandler(self, handler):
        @functools.wraps(handler)
        def wrapper(*args, **kwargs):
            response, _ = handler(*args, **kwargs)
            new_data = response.json | {"code": "JWT_ERROR"}
            return (jsonify(new_data), HTTPStatus.UNAUTHORIZED)

        return wrapper

    def rewrite_errorhandlers(self):
        self._expired_token_callback = self.rewrite_errorhandler(default_expired_token_callback)
        self._invalid_token_callback = self.rewrite_errorhandler(default_invalid_token_callback)
        self._needs_fresh_token_callback = self.rewrite_errorhandler(default_needs_fresh_token_callback)
        self._revoked_token_callback = self.rewrite_errorhandler(default_revoked_token_callback)
        self._unauthorized_callback = self.rewrite_errorhandler(default_unauthorized_callback)
        self._user_lookup_error_callback = self.rewrite_errorhandler(default_user_lookup_error_callback)
        self._token_verification_failed_callback = self.rewrite_errorhandler(default_token_verification_failed_callback)


class AuthMethodView[T](MethodView):
    decorators = [jwt_required()]

    @property
    def current_user(self) -> T:
        return jwt_current_user


class AdminMethodView[T](AuthMethodView[T]):
    decorators = [admin_required()]
