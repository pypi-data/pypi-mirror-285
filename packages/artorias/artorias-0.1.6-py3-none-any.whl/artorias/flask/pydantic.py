import functools
from inspect import isclass
from typing import Any
from typing import Callable
from typing import Sequence
from typing import Type
from typing import get_args
from typing import get_origin
from typing import get_type_hints

from flask import Flask
from flask import current_app
from flask import request
from flask.typing import RouteCallable
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import ValidationError
from pydantic import validate_call

from artorias.flask import abort

VIEW_HINTS: dict[int, dict[str, Callable[[], Any]]] = {}


def From(data_from: str, var_type: Any | None = None):
    if var_type is None:
        return functools.partial(From, data_from=data_from)
    else:
        data = getattr(request, data_from)
        if data_from is None:
            return None
        return var_type(**data) if issubclass(var_type, Schema) else data


class Schema(BaseModel):
    pass


class PaginationSchema[T](Schema):
    page: int
    per_page: int
    total: int
    items: Sequence[T]


def extract(func: Callable):
    data: dict[str, Callable[[], Any]] = {}
    for var, var_hint in get_type_hints(func, include_extras=True).items():
        if isclass(var_hint) and issubclass(var_hint, Schema):
            data[var] = functools.partial(lambda h: h(**request.json) if request.is_json else None, h=var_hint)
        else:
            data[var] = functools.partial(lambda v: request.args.get(v), v=var)

    return data


def validate(func: Callable) -> RouteCallable:
    VIEW_HINTS[id(func)] = extract(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            params = {
                var: var_value()
                for var, var_value in VIEW_HINTS[id(func)].items()
                if var not in kwargs and var_value() is not None
            }
            current_app.logger.debug(f"Params: {params}")
        except ValidationError as e:
            abort(code="REQUEST_VALIDATION_ERROR", msg=e.json(), status_code=400)
        return validate_call(config=ConfigDict(arbitrary_types_allowed=True))(func)(*args, **kwargs, **params)

    return wrapper


def serialize(return_type: Type[Schema] | Any, from_attributes: bool = True):
    def check() -> tuple[bool, Type[Schema] | None]:
        try:
            issubclass(return_type, Schema)
        except TypeError:
            origin, args = get_origin(return_type), get_args(return_type)
            if origin and issubclass(origin, Sequence) and args:
                return False, args[0]
            else:
                raise
        else:
            return True, None

    is_schema, list_schema = check()

    def decorator(func: Callable) -> RouteCallable:
        def _wrapper(*args, **kwargs):
            response = func(*args, **kwargs)

            if is_schema:
                return return_type.model_validate(response, from_attributes=from_attributes).model_dump()
            else:
                return [
                    list_schema.model_validate(item, from_attributes=from_attributes).model_dump()  # type: ignore
                    for item in response
                ]

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return _wrapper(*args, **kwargs)

        return wrapper

    return decorator


def pydantic_patch(app: Flask):
    for endpoint, view in app.view_functions.items():
        if endpoint == "static":
            continue
        if not hasattr(view, "view_class"):
            app.view_functions[endpoint] = validate(app.view_functions[endpoint])
        else:
            view_class = getattr(view, "view_class")
            for method in ("get", "post", "patch", "delete", "put"):
                if not hasattr(view_class, method):
                    continue
                setattr(view_class, method, validate(getattr(view_class, method)))
