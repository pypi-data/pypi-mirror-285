# flake8: noqa: I005
from typing import Any, Callable, Dict, List, Optional, Union, \
    Iterable
from azure.functions.decorators.http import HttpTrigger, HttpOutput, \
    HttpMethod
from azure.functions.decorators.core import DataType, \
    AuthLevel, InputBinding
from azure.functions.decorators.utils import parse_singular_param_to_enum, \
    parse_iterable_param_to_enums
from azure.functions import FunctionApp, HttpResponse
from azure.functions.decorators.core import DataType
from pydoc import locate
from .middleware import RemoveReqExtension, InvocationIdMidleware
import json
import azure
import inspect

from .udf_binding import UdfPropertyInput, UdfResponse
from .fabric_class import FabricSqlConnection, FabricLakeHouseFilesClient, FabricLakehouseClient
from .item_binding import FabricItemInput, ItemType

class FabricApp(FunctionApp):

    def __init__(self):
        super().__init__(AuthLevel.ANONYMOUS)

    def function(self, name=None):
        @self._configure_function_builder_with_func
        def wrap(fb, user_func):
            # Add HTTP Trigger
            fb.add_trigger(trigger=HttpTrigger(
                        name='req',
                        methods=[HttpMethod.POST],
                        auth_level=AuthLevel.ANONYMOUS,
                        route=name))
            fb.add_binding(binding=HttpOutput(name='$return'))

            # Add Custom UDF Bindings
            sig = inspect.signature(user_func)
            for param in sig.parameters.values():
                if self._is_typeof_fabricitem_input(param.annotation):
                    continue
                if(param.name == 'req'):
                    continue

                # Add custom bindings
                fb.add_binding(binding=UdfPropertyInput(
                    name=param.name, parameterName=param.name, typeName=param.annotation.__name__)
                )

            return fb
        return wrap

    def _is_typeof_fabricitem_input(self, obj):
        # Check to see if parameter is anything we might return from a fabric binding
        return obj == FabricSqlConnection or obj == FabricLakeHouseFilesClient or obj == FabricLakehouseClient

    def _configure_function_builder_with_func(self, wrap) -> Callable[..., Any]:
        def decorator(func):

            sig = inspect.signature(func)
            params = []
            params.append(inspect.Parameter('req', inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=azure.functions.HttpRequest))

            for param in sig.parameters.values():
                if param.name != 'req':
                    params.append(param)

            sig = sig.replace(parameters=tuple(params))
            func.__signature__ = sig

            fb = self._validate_type(func)
            self._function_builders.append(fb)

            return wrap(fb, func)

        return decorator
    # The decorator that will be used to tell the function we want a fabric item
    def fabric_item_input(self,
                        argName,
                        alias: str,
                        item_type: Optional[ItemType] = ItemType.SQL,
                        default_item_name: Optional[str] = None,
                        default_workspace_name: Optional[str] = None,
                        data_type : Optional[DataType] = DataType.STRING,
                        **kwargs) \
            -> Callable[..., Any]:

        @self._configure_function_builder
        def wrap(fb):
                
            fb.add_binding(
                binding=FabricItemInput(
                    name=argName,
                    alias=alias,
                    itemType=item_type,
                    defaultItemName=default_item_name,
                    defaultWorkspaceName=default_workspace_name,
                    data_type=parse_singular_param_to_enum(data_type,
                                                        DataType),
                    **kwargs))
            return fb
        
        return wrap