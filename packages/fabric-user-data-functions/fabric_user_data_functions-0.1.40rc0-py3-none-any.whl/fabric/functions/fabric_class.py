import struct
import typing
import jwt
from enum import IntEnum
from urllib.parse import urlparse

# flake8: noqa: I005
import pyodbc
from azure.core.credentials import AccessToken, TokenCredential
from azure.storage.filedatalake import DataLakeDirectoryClient

class ItemType(IntEnum):
    SQL = 0
    Lakehouse_Sql = 2
    DataWarehouse = 3
    Lakehouse_Files = 4

class FabricItem:
    def __init__(self, alias_name: str, fabric_item_type: ItemType, endpoints: typing.Dict[str, typing.Dict[str, str]]):
        self.__alias_name = alias_name
        self.__fabric_item_type = fabric_item_type
        self.__endpoints = endpoints

    @property
    def alias_name(self) -> typing.Optional[str]:
        return self.__alias_name
    
    @property
    def fabric_item_type(self) -> typing.Optional[ItemType]:
        return self.__fabric_item_type
    
    @property
    def endpoints(self) -> typing.Optional[typing.Dict[str, typing.Dict[str, str]]]:
        return self.__endpoints

class FabricSqlConnection(FabricItem):

    APPSETTINGS_PATH = "sqlendpoint"

    def get_split_connection_string(self) -> typing.Dict[str, str]:

        connString = self.endpoints[self.APPSETTINGS_PATH]["ConnectionString"]

        # Lakehouse connection string contains Data Source instead of Server
        connString = connString.replace("Data Source", "Server")

        if "=" not in connString:
            return { "Server": connString }
        
        if "Server" not in connString:
            raise Exception("Server value is not set in connection")

        split_by_semicolon = connString.split(";")
        return {x.split("=")[0].strip(): x.split("=")[1].strip() for x in split_by_semicolon}

    def connect(self) -> pyodbc.Connection:
        if self.APPSETTINGS_PATH not in self.endpoints:
            raise Exception(f"{self.APPSETTINGS_PATH} is not set")
        
        dict_conn_string = self.get_split_connection_string()
        connString = dict_conn_string["Server"]

        # https://github.com/AzureAD/azure-activedirectory-library-for-python/wiki/Connect-to-Azure-SQL-Database
        
        token = self.endpoints[self.APPSETTINGS_PATH]["AccessToken"].encode('UTF-8')
        exptoken = b""
        for i in token:
            exptoken+=bytes({i})
            exptoken+=bytes(1)
        tokenstruct = struct.pack("=i", len(exptoken)) + exptoken
        return pyodbc.connect(f'DRIVER={"ODBC Driver 18 for SQL Server"};Server={connString};Encrypt=yes;', attrs_before = {1256:tokenstruct}, timeout=60)
    
class FabricLakeHouseFilesClient(FabricItem):
    class CustomTokenCredential(TokenCredential):
        def __init__(self, token: str):
            alg = jwt.get_unverified_header(token)['alg']
            decodedAccessToken = jwt.decode(token, algorithms=[alg], options={"verify_signature": False, # Needed or else it complains about Exception: ValueError: Unable to load PEM file.
                                                                               "verify_exp": False} # Needed to not throw if the access token is already expired
                                                                               )
            # Token Expiry
            tokenExpiry = decodedAccessToken["exp"]

            self._token = AccessToken(token, tokenExpiry)

        def get_token(self, *scopes, **kwargs) -> AccessToken:
            return self._token
    
    APPSETTINGS_PATH = "fileendpoint"
    
    def connect(self) -> DataLakeDirectoryClient:
        if self.APPSETTINGS_PATH not in self.endpoints:
            raise Exception(f"{self.APPSETTINGS_PATH} is not set")
        
        raw_path = self.endpoints[self.APPSETTINGS_PATH]['ConnectionString']
        parsed_path = urlparse(raw_path)
        
        accessToken = self.endpoints[self.APPSETTINGS_PATH]['AccessToken']

        # The account URL is the scheme and netloc parts of the parsed path
        account_url = f"{parsed_path.scheme}://{parsed_path.netloc}"

        # The file system name and directory name are in the path part of the parsed path
        # We remove the leading slash and then split the rest into the file system name and directory name
        file_system_name, _, directory_name = parsed_path.path.lstrip('/').partition('/')

        directory_client = DataLakeDirectoryClient(account_url, file_system_name, directory_name, self.CustomTokenCredential(accessToken))
        return directory_client
    
class FabricLakehouseClient(FabricItem):

    def connectToSql(self) -> pyodbc.Connection:
        return FabricSqlConnection(self.alias_name, self.fabric_item_type, self.endpoints).connect()  

    def connectToFiles(self) -> DataLakeDirectoryClient:
        return FabricLakeHouseFilesClient(self.alias_name, self.fabric_item_type, self.endpoints).connect()
