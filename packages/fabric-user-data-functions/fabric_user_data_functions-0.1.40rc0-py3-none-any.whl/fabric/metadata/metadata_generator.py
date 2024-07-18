import importlib
import json
import logging
import os
from pathlib import Path
import sys
# flake8: noqa: I900
import azure.functions as azure_func

# return code:
# 0 - no error
# 1 - error


SCRIPT_FILE_NAME = 'function_app.py'
METADATA_FILE_NAME = 'functions.metadata'
NEEDED_BINDING_TYPES = {'httpTrigger', 'UdfProperty', 'FabricItem'}
ERROR_CODE = 1
SUCCESS = 0

def _get_app_functions(file_name: str = SCRIPT_FILE_NAME):
    module_path = os.getcwd()
    func_file = os.path.join(module_path, file_name)

    if not os.path.exists(func_file):
        logging.error(f'Cannot find source code {file_name}')
        return None
    
    sys.path.append(str(module_path))
    module_name = Path(func_file).stem
    imported_module = importlib.import_module(module_name)

    app = None
    for i in imported_module.__dir__():
        if isinstance(getattr(imported_module, i, None), azure_func.FunctionRegister):
            if not app:
                app = getattr(imported_module, i, None)
            else:
                logging.error("More than 1 app found in the source code")
                return None

    if not app:
        logging.error("No app found in the source code")
        return None
    
    functions = app.get_functions()
    if not functions:
        logging.error("No function found in the source code")
        return None
    
    return functions

def _collect_function_metadata(functions):
    metadata=[]
    for func in functions:
        # log the function  bindings
        logging.info(f'Getting metadata from Function {func._name}')

        single_func_meta = {}
        single_func_meta['name'] = func._name
        single_func_meta['scriptFile'] = func.function_script_file
        single_func_meta['bindings'] = []
        for binding in func._bindings:
            if binding.type not in NEEDED_BINDING_TYPES:
                continue
            logging.info(f' Binding name: {binding.name}')
            logging.info(f' Binding type: {binding.type}')
            logging.info(f' Binding direction: {binding._direction.name}')

            b = {}
            b['name'] = binding.name
            b['direction'] = ''.join([binding._direction.name[0], binding._direction.name[1:].lower()])
            b['type'] = binding.type

            additional_props = {}
            if binding.type == 'httpTrigger':
                additional_props = _get_http_binding_properties(binding)

            if binding.type == 'UdfProperty':
                additional_props = _get_udf_binding_properties(binding)
            
            if binding.type == 'FabricItem':
                additional_props = _get_fabricItem_binding_properties(binding)

            for key, value in additional_props.items():
                b[key] = value

            single_func_meta['bindings'].append(b)
        
        udf_properties = _get_udf_properties_from_function(single_func_meta)
        single_func_meta['fabricProperties'] = udf_properties

        # remove UdfProperties from bindings
        single_func_meta['bindings'] = [b for b in single_func_meta['bindings'] if b['type'] != 'UdfProperty']

        metadata.append(single_func_meta)
    
    return metadata



def _get_http_binding_properties(binding):
    props = {}
    methods = getattr(binding, 'methods', None)
    if not methods:
        methods = [azure_func.HttpMethod.POST]
    
    props['methods'] = []
    for m in methods:
        if m == azure_func.HttpMethod.PUT:
            logging.error("Fabric Function currently does not support PUT HTTP actions.")
            return None
        props['methods'].append(m.value.lower())

    props['route'] = getattr(binding, 'route', None)
    auth = getattr(binding, 'auth_level', None)
    if auth:
        props['authLevel'] = ''.join([auth.value[0].upper(), auth.value[1:].lower()])

    return props

def _get_fabricItem_binding_properties(binding):
    props = {}
    
    props['alias'] = getattr(binding, 'alias', None)

    return props

def _get_udf_binding_properties(binding):
    props = {}
    
    props['parameterName'] = getattr(binding, 'parameterName', None)
    props['typeName'] = getattr(binding, 'typeName', 'any')

    return props

def _get_udf_properties_from_function(func_meta):
    props = {}
    props['fabricFunctionReturnType'] = 'UdfResponse'
    props['fabricFunctionParameters'] = []

    for binding in func_meta['bindings']:
        if binding['type'] == 'UdfProperty':
            p = {}
            p['name'] = binding['parameterName']
            p['dataType'] = binding['typeName']
            props['fabricFunctionParameters'].append(p)

    return props

def _get_metadata_file_path(file_name=METADATA_FILE_NAME):
    base_directory = os.getcwd()
    return os.path.join(base_directory, "fabric_lib", file_name)

def _write_metadata_file(metadata, file_name=METADATA_FILE_NAME):
    metadata_json = json.dumps(metadata)
    output = _get_metadata_file_path(file_name)
    with open(output, 'w') as meta_file:
        meta_file.write(metadata_json)

def _delete_metadata_file_if_exist(file_name=METADATA_FILE_NAME):
    metadata_file = _get_metadata_file_path(file_name)
    if os.path.exists(metadata_file):
        os.remove(metadata_file)

def generate_function_metadata():
    try:
        # remove metadata first since VSCode extension uses existence of the file as the success of the script run
        _delete_metadata_file_if_exist()

        functions = _get_app_functions()

        if(functions is None):
            return ERROR_CODE
        
        metadata = _collect_function_metadata(functions)
        if(metadata is None):
            return ERROR_CODE
        
        _write_metadata_file(metadata)
        # prettify the json metadata and log it
        logging.info(json.dumps(metadata, indent=2, sort_keys=True))
        logging.info(f'Function metadata generated successfully for {len(functions)} functions.')
        return SUCCESS
    except Exception as e:
        logging.error(f'Got errors when generating metadata. Details:{e}')
        return ERROR_CODE
