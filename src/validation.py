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
import platform
from os.path import join, dirname, isabs, exists
import logging
import time
import json
import jsonref
from fastjsonschema import compile as fjs_compile, validate as fjs_validate
from fastjsonschema.exceptions import JsonSchemaException as fjs_JsonSchemaException
from jsonschema import validate, ValidationError
from jsonschema.validators import validator_for

__all__ = ['Json_Validator']

logIt = True
if logIt:
    loggingConfig = {'level': logging.DEBUG,
                     'format': '[%(asctime)s][%(levelname)s]:%(message)s',
                     'datefmt': '%m/%d/%Y %I:%M:%S %p'
                     }
    logging.basicConfig(**loggingConfig)
    logger = logging.getLogger(__name__)

# -----------------------------------------
#   Init. Folder/File Constants
# -----------------------------------------
folder_schema = join('..', 'schema', 'nested')
file_schema = 'schema_nested.json'


# file_valid = 'sample_valid.json'
# file_invalid = 'sample_invalid.json'


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
            logger.info('%6s<--- %s function executed in %2.2f ms' % ("",
                                                                      method.__name__,
                                                                      (te - ts) * 1000))

            # print('%6s<--- %s function executed in %2.2f ms' % ("",
            #                                                     method.__name__,
            #                                                     (te - ts) * 1000))
        return result

    return timed


# ======================================================================
#   JSON Validation Class
# ======================================================================
class Json_Validator(object):
    """
    Class of JSON Schema Validation for GM and Sub-Models

    Note1: benchmarks based on https://www.peterbe.com/plog/jsonschema-validate-10x-faster-in-python
    Note2: Inferring schemas from examples using https://jsonschema.net
    Note3: Defining complex/referenced schema based on https://medium.com/grammofy/handling-complex-json-schemas-in-python-9eacc04a60cf

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
    def __init__(self, schema_file=join(folder_schema, file_schema)):

        # Find Absolute Path of schema_file
        if not isabs(schema_file):
            schema_file = join(dirname(__file__), schema_file)

        if not exists(schema_file):
            raise ValueError("Cannot create class instance with no/missing schema file.")

        # Message for Invalid Jsons
        self.message = "%8s******** WARNING: JSON data is invalid based on schema ********" % ("")

        # Read Schema from JSON Schema File
        self.schema_file = schema_file

        # Load schema from file to class
        # Notes: https://github.com/Julian/jsonschema/issues/98#issuecomment-105475109
        # with open(os.path.join(absolute_path_to_base_directory, base_filename)) as file_object:
        #     schema = json.load(file_object)
        # resolver = jsonschema.RefResolver('file:///' + absolute_path_to_base_directory.replace("\\", "/") + '/', schema)
        # jsonschema.Draft4Validator(schema, resolver=resolver).validate(data)
        base_path = dirname(self.schema_file)
        if platform.system().lower() in ["windows"]:
            base_uri = 'file:///{}/'.format(base_path.replace("\\", "/"))
        elif platform.system().lower() in ["linux"]:
            base_uri = 'file://{}/'.format(base_path.replace("\\", "/"))

        with open(self.schema_file) as schema_file:
            # self.schema = json.loads(schema_file.read())
            self.schema = jsonref.loads(schema_file.read(), base_uri=base_uri, jsonschema=True)

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
# Running independent benchmarks of schema validator class
if __name__ == '__main__':

    # Unified Nested Schema
    folder_test = join('..', 'schema', 'flat')
    file_test = 'schema_flat.json'
    test_valid = 'sample_valid.json'
    test_invalid = 'sample_invalid.json'

    # Complex (Referenced) Nested Schema
    folder_test = join('..','schema', 'nested')
    file_test = 'schema_nested.json'
    test_valid = 'sample_valid.json'
    test_invalid = 'sample_invalid.json'

    logger.info("%2s===> JSON Validation Class" % (""))
    relative_path = join(folder_test, test_invalid)
    absolute_path = join(dirname(__file__), relative_path)

    logger.info("%6s---> Reading JSON Data File: %s" % ("", absolute_path))
    with open(absolute_path) as json_data_file:
        json_data = json.loads(json_data_file.read())

    logger.info("%6s---> Create Validator Class Instance" % (""))
    jv = Json_Validator(join(folder_test, file_test))

    logger.info("\n" + "-" * 75)
    logger.info("%6s---> Validation Function Json Schema" % (""))
    jv.validate(json_data)

    logger.info("\n" + "-" * 75)
    logger.info("%6s---> Validation Function Fast Json Schema" % (""))
    jv.validate_fjs(json_data)

    logger.info("\n" + "-" * 75)
    logger.info("%6s---> Validation Function Benchmark _1" % (""))
    jv._validate1(json_data)

    logger.info("\n" + "-" * 75)
    logger.info("%6s---> Validation Function Benchmark _2" % (""))
    jv._validate2(json_data)

    logger.info("\n" + "-" * 75)
    logger.info("%6s---> Validation Function Benchmark _3" % (""))
    jv._validate3(json_data)

    logger.info("\n" + "-" * 75)
    logger.info("%2s<=== Validation Completed" % (""))
