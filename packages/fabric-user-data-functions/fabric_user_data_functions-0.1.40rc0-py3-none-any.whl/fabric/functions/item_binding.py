import json
from typing import Any, Callable, Optional

# flake8: noqa: I900
import azure
from azure.functions.decorators.core import DataType, InputBinding
from azure.functions.decorators.utils import parse_singular_param_to_enum

from .fabric_class import (FabricItem, FabricLakeHouseFilesClient,
                           FabricSqlConnection, ItemType, FabricLakehouseClient)

# The binding object that will be used by our input decorator below
class FabricItemInput(InputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return 'FabricItem'
    
    def __init__(self,
                name: str,
                alias: str,
                itemType: ItemType,
                defaultItemName: Optional[str] = None,
                defaultWorkspaceName: Optional[str] = None,
                data_type: Optional[DataType] = DataType.STRING,
                **kwargs):
        super().__init__(name, data_type)

# The input converter that automatically gets registered in the function app. 
class FabricItemConverter(azure.functions.meta.InConverter,
                              binding='FabricItem'):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:

        # Need to check what the enum type of the item is and make sure we can convert it
        return issubclass(pytype, (FabricItem, FabricSqlConnection))
    
    @classmethod
    def parseType(self, body: json):

        endpoints = body['Endpoints']
        endpoints = {k.lower():v for k,v in endpoints.items()} # we can know this doesn't have collisions 
        # because the host extension uses a case insensitive dictionary
        sqlEndpoint = "sqlendpoint"
        fileEndpoint = "fileendpoint"

        itemType = ItemType(body['FabricItemType'])

        if sqlEndpoint in endpoints and fileEndpoint in endpoints:
            return FabricLakehouseClient(
                alias_name=body['AliasName'],
                fabric_item_type=itemType,
                endpoints=endpoints)
        elif sqlEndpoint in endpoints:
            return FabricSqlConnection(
                alias_name=body['AliasName'],
                fabric_item_type=itemType,
                endpoints=endpoints)
        elif fileEndpoint in endpoints:
            return FabricLakeHouseFilesClient(
                alias_name=body['AliasName'],
                fabric_item_type=itemType,
                endpoints=endpoints)

        # If not found above, return the default
        return FabricItem(
                alias_name=body['AliasName'],
                fabric_item_type=itemType,
                endpoints=endpoints)
    
    @classmethod
    def decode(cls, data, *,
               trigger_metadata) -> Any:
        
        if data is not None and data.type == 'string' and data.value is not None: 
            body = json.loads(data.value) 
        else:
            raise NotImplementedError(
                f'unable to load data successfully for fabric item')
         
        body = json.loads(data.value) 

        return cls.parseType(body)