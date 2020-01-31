"""
# -------------------------------------------------------------------------------
# Name:         JSON Schema Validation
# Purpose:      Shared JSON Schema Validation for Input JSONS
#
#
# Author:       Moe Maysami
#
# Created:      Nov 2019
# Licence:      See Git
# -------------------------------------------------------------------------------
"""
import os
import time
import json
from jsonschema import validate, ValidationError
from jsonschema.validators import validator_for
from fastjsonschema import compile as fjs_compile, validate as fjs_validate
from fastjsonschema.exceptions import JsonSchemaException as fjs_JsonSchemaException

__all__ = ['Json_Validator']


# ======================================================================
#   Decorators
# ======================================================================
def timeit(method):
    def timed(*args, **kw):
        ts = time.perf_counter()
        result = method(*args, **kw)
        te = time.perf_counter()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%6s<--- %s function executed in %2.2f ms' % ("",
                                                                method.__name__,
                                                                (te - ts) * 1000))
        return result

    return timed


# ======================================================================
#   JSON Validation Class
# ======================================================================
class Json_Validator(object):
    """
    Class of JSON Schema Validation for GM and Sub-Models

    Note1: benchmarks based on https://www.peterbe.com/plog/jsonschema-validate-10x-faster-in-python
    Note2: use https://jsonschema.net for defining schema

    # json Schema
    # validate(instance, schema, cls=None)
    #   Raises
    #     jsonschema.exceptions.ValidationError – is invalid
    #     jsonschema.exceptions.SchemaError     – is invalid
    #
    #  cls (IValidator) – The class that will be used to validate the instance.
    #    If schema has a $schema property with a known meta-schema, the proper validator will be used.
    #    It is recommended that all schemas contain $schema properties for this reason.
    #
    #  class jsonschema.IValidator(schema, types=(), resolver=None, format_checker=None)
    """

    # ----------------------------------------------------------------------
    def __init__(self, schema_file=os.path.join('..//schema', 'schema.json')):

        # Find Absolute Path of schema_file
        if not os.path.isabs(schema_file):
            schema_file = os.path.join(os.path.dirname(__file__), schema_file)

        if not os.path.exists(schema_file):
            raise ValueError("Cannot create class instance with no/missing schema file.")

        # Message for Invalid Jsons
        self.message = "%8s******** WARNING: JSON data is invalid based on schema ********" % ("")

        # Read Schema from JSON Schema File
        self.schema_file = schema_file

        # Load schema from file to class
        with open(self.schema_file) as schema_file:
            self.schema = json.loads(schema_file.read())

        # Create JS Validator
        self.validator = validator_for(self.schema)
        self.validator.check_schema(self.schema)
        self.validator_fast = self.validator(self.schema)

        # Create Fast JS Validator
        self.validator_fjs = fjs_compile(self.schema)

    # ----------------------------------------------------------------------
    @timeit
    def validate(self, json_input):
        """
        Fast Deployment Using JsonSchema

        :param json_input: Json data to be validated 
        :return: Boolean Valid Flag 
        """
        try:
            self.validator_fast.validate(json_input)
        except ValidationError as err:
            print(self.message)
            print(err)
            return False
        return True

    # ----------------------------------------------------------------------
    @timeit
    def validate_fjs(self, json_input):
        """
        Fast Deployment Using FastJsonSchema

        :param json_input: Json data to be validated 
        :return: Boolean Valid Flag 
        """
        try:
            self.validator_fjs(json_input)
        except fjs_JsonSchemaException as err:
            print(self.message)
            print(err)
            return False
        return True

    # ----------------------------------------------------------------------
    @timeit
    def _validate1(self, json_input):
        """
        Slow Aux Deployment Using JsonSchema
        
        :param json_input: Json data to be validated 
        :return: Boolean Valid Flag 
        """

        try:
            validate(json_input, self.schema, cls=self.validator)
        except ValidationError as err:
            print(self.message)
            print(err)
            return False
        return True

    # ----------------------------------------------------------------------
    @timeit
    def _validate2(self, json_input):
        """
        Slow Aux Deployment Using JsonSchema

        :param json_input: Json data to be validated 
        :return: Boolean Valid Flag 
        """
        try:
            validate(json_input, self.schema)
        except ValidationError as err:
            print(self.message)
            print(err)
            return False
        return True

    # ----------------------------------------------------------------------
    @timeit
    def _validate3(self, json_input):
        """
        Slow Aux Deployment Using FastJsonSchema

        :param json_input: Json data to be validated 
        :return: Boolean Valid Flag 
        """
        try:
            fjs_validate(self.schema, json_input)
        except fjs_JsonSchemaException as err:
            print(self.message)
            print(err)
            return False
        return True


# --------------------------------------------------------------------------------------
# ======================================================================================
# ==========                           MAIN                                   ==========
# ======================================================================================
# --------------------------------------------------------------------------------------
# Running independent benchmark of class
if __name__ == '__main__':
    print("%2s===> JSON Validation Class" % (""))

    relative_path = os.path.join('..//schema', 'sample_invalid.json')
    absolute_path = os.path.join(os.path.dirname(__file__), relative_path)


    print("%6s---> Reading JSON Data File: %s" % ("", absolute_path))
    with open(absolute_path) as json_data_file:
        json_data = json.loads(json_data_file.read())

    print("%6s---> Create Validator Class Instance" % (""))
    jv = Json_Validator()

    print("\n  ", "-" * 50)
    print("%6s---> Validation Function Json Schema" % (""))
    jv.validate(json_data)

    print("\n  ", "-" * 50)
    print("%6s---> Validation Function Fast Json Schema" % (""))
    jv.validate_fjs(json_data)

    print("\n  ", "-" * 50)
    print("%6s---> Validation Function Benchmark _3" % (""))
    jv._validate1(json_data)

    print("\n  ", "-" * 50)
    print("%6s---> Validation Function Benchmark _4" % (""))
    jv._validate2(json_data)

    print("\n  ", "-" * 50)
    print("%6s---> Validation Function Benchmark _5" % (""))
    jv._validate3(json_data)

    print("\n  ", "-" * 50)
    print("%2s<=== Validation Completed" % (""))
