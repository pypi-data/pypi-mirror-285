# flake8: noqa: I005
from typing import Any, Callable, Dict, List, Optional, Union, \
    Iterable
from azure.functions.decorators.core import  DataType
from azure.functions.decorators.core import DataType, InputBinding
import azure
from pydoc import locate
from collections import namedtuple
import json
from enum import IntEnum 
from azure.functions import HttpResponse

class UdfResponse(HttpResponse):
    pass

class UdfPropertyInput(InputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return 'UdfProperty'
    
    def __init__(self,
                name: str,
                parameterName: str,
                typeName: Optional[str] = None,
                data_type: Optional[DataType] = DataType.STRING,
                **kwargs):
        super().__init__(name, data_type)


# The input converter that automatically gets registered in the function app.
class UdfPropertyConverter(azure.functions.meta.InConverter, binding='UdfProperty'):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return True

    @classmethod
    def decode(cls, data, *,
               trigger_metadata) -> Any:
        if data is not None and data.type == 'string' and data.value is not None:
            body = json.loads(data.value)
        else:
            raise NotImplementedError(
                'unable to load data successfully for udf property')
        return tryconvert(body['PropertyType'], body['PropertyJsonValue'])


def tryconvert(property_type: str, property_json_value: str):
    prop_type = locate(property_type)
    try:
        return prop_type(property_json_value)
    except TypeError:
        pass

    return json.loads(property_json_value)
