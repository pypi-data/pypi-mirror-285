from typing import Callable, Any, Dict
from fastapi import APIRouter
from fastapi.routing import APIRoute
from pydantic import BaseModel
import inspect

from fastapi.dependencies.models import Dependant
from fastapi.dependencies.utils import (
    get_flat_dependant,
    create_body_model,
    create_response_field,
    check_file_field
)
from pydantic import Field as ModelField
from typing import Optional, Type
from fastapi import params
from starlette.routing import request_response

def custom_get_body_field(*, dependant: Dependant, name: str) -> Optional[ModelField]:
    flat_dependant = get_flat_dependant(dependant)
    if not flat_dependant.body_params:
        return None
    first_param = flat_dependant.body_params[0]
    field_info = first_param.field_info
    embed = getattr(field_info, "embed", None)
    body_param_names_set = {param.name for param in flat_dependant.body_params}
    # if len(body_param_names_set) == 1 and not embed:
    #     check_file_field(first_param)
    #     return first_param
    # If one field requires to embed, all have to be embedded
    # in case a sub-dependency is evaluated with a single unique body field
    # That is combined (embedded) with other body fields
    for param in flat_dependant.body_params:
        setattr(param.field_info, "embed", True)  # noqa: B010
    model_name = name
    BodyModel = create_body_model(
        fields=flat_dependant.body_params, model_name=model_name
    )
    required = any(True for f in flat_dependant.body_params if f.required)
    BodyFieldInfo_kwargs: Dict[str, Any] = {
        "annotation": BodyModel,
        "alias": "body",
    }
    if not required:
        BodyFieldInfo_kwargs["default"] = None
    if any(isinstance(f.field_info, params.File) for f in flat_dependant.body_params):
        BodyFieldInfo: Type[params.Body] = params.File
    elif any(isinstance(f.field_info, params.Form) for f in flat_dependant.body_params):
        BodyFieldInfo = params.Form
    else:
        BodyFieldInfo = params.Body

        body_param_media_types = [
            f.field_info.media_type
            for f in flat_dependant.body_params
            if isinstance(f.field_info, params.Body)
        ]
        if len(set(body_param_media_types)) == 1:
            BodyFieldInfo_kwargs["media_type"] = body_param_media_types[0]
    final_field = create_response_field(
        name="body",
        type_=BodyModel,
        required=required,
        alias="body",
        field_info=BodyFieldInfo(**BodyFieldInfo_kwargs),
    )
    check_file_field(final_field)
    return final_field

class CustomAPIRoute(APIRoute):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.body_field = custom_get_body_field(dependant=self.dependant, name=self.unique_id)
            self.app = request_response(self.get_route_handler())

# 라우터를 모듈별로 저장할 딕셔너리
module_routers: Dict[str, APIRouter] = {}

def get_router_for_module(module_name: str) -> APIRouter:
    if module_name not in module_routers:
        module_routers[module_name] = APIRouter()
    return module_routers[module_name]

def data_conv(func: Callable) -> Callable:
    def wrapper(*args, **kwargs) -> Any:
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs).arguments

        for name, param in sig.parameters.items():
            param_class = param.annotation
            if name in bound_args:
                if isinstance(bound_args[name], dict) and issubclass(param_class, BaseModel):
                    bound_args[name] = param_class(**bound_args[name])
                else:
                    bound_args[name] = bound_args[name]

        return func(*bound_args.values())

    return wrapper

class MBaseModel(BaseModel):
    class Config:
        title = None
        widget = None

        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            cls.json_schema_extra = {}
            cls.json_schema_extra["dataclassname"] = cls.__module__ + '.' + cls.__qualname__.rsplit('.', 2)[0]
            if cls.widget is not None:
                cls.json_schema_extra["ui:widget"] = cls.widget

def auto_schema(func: Callable) -> Callable:
    func_name = func.__name__
    module = inspect.getmodule(func)
    if module is None:
        raise ValueError("Module not found for the given function")
    module_name = module.__name__
    path = f"/{module_name.replace('.', '/')}/{func_name}"

    router = get_router_for_module(module_name + func_name)
    id = func_name.replace('_', ' ')

    router.add_api_route(path, func, methods=["POST"], operation_id=id, route_class_override=CustomAPIRoute)
    return data_conv(func)
