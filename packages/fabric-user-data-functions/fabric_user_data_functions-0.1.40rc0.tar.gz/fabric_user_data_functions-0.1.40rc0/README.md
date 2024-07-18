# Fabric Functions Python Worker

## Introduction

This project contains the necessary bindings and middleware we can register on a python function in order to receive fabric data from our worker extension. 

## Fabric Item Binding

By importing the `fabric_item_input` binding, the user can add a new attribute to their fabric function. This input has the same properties as the FabricItem attribute and binding from the host extension and will pass down to the worker the information to create a FabricItem:

```
class FabricItem:
    def __init__(self, aliasName: str, connectionString: str, fabricItemType: ItemType, endpoints: typing.Dict[str, Endpoint]):
        self.__aliasName = aliasName
        self.__connectionString = connectionString
        self.__fabricItemType = fabricItemType
        self.__endpoints = endpoints
```

where Endpoint is a class containing a string ConnectionString and a string AccessToken

Depending on the `itemType` specified in the input binding, we can map the item type to either the default FabricItem, a FabricSqlConnection (for SQL or Datamarts), or a FabricLakeHouseFilesClient (for LakeHouse files). 

```
@fabric_item_input(app, argName="myDatamart", alias="MyDatamart", item_type=ItemType.Datamart)
@app.route(route="hello_fabric")
def hello_fabric(req: func.HttpRequest, myDatamart: FabricSqlConnection) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    conn = myDatamart.connect()

    # Use pyodbc connection

    currentTime = datetime.datetime.now()

    return func.HttpResponse(f"Hello Fabric. The current time is {currentTime.time()}.")
```

