## Validator Class for Json Schema

Validation class provides json schema validation using multiple methods. Based on the benchmarks, `validate` and `validate_fjs` provide the best performance. 
 - `validate` is based on the python package `jsonschema`, and 
 - `validate_fjs` is based on `fastjsonschema`.

 The class is also capable of handling complex schemas with internal or local file references. 




#### References:
 - benchmarks based on [this article](https://www.peterbe.com/plog/jsonschema-validate-10x-faster-in-python)
 - Inferring schemas from examples using [online services](https://jsonschema.net)
 - Defining complex/referenced schema based on [this article](https://medium.com/grammofy/handling-complex-json-schemas-in-python-9eacc04a60cf)