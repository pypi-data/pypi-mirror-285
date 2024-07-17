# JSON Validation

This Python package provides a simple and intuitive way to validate JSON data against a specified schema. It is designed to be easy to use and highly customizable.

## Installation

You can install JSON Validation using pip:

```shell
pip install json-validation
```

## Usage

To use JSON Validation in your Python code, you first need to import the `Validator` class:

```python
from json_validation import Validator
```

Next, you can create an instance of the `Validator` class and specify the JSON schema you want to validate against:

```python
validator = Validator(schema)
```

You can then use the `validate` method to validate your JSON data:

```python
result = validator.validate(data)
```

The `validate` method returns a boolean value indicating whether the data is valid according to the schema. You can also access detailed validation errors using the `errors` property of the `Validator` instance.

## Examples

Here are some examples to help you get started:

```python
# Create a schema
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"}
    },
    "required": ["name"]
}

# Create a Validator instance
validator = Validator(schema)

# Validate JSON data
data = {
    "name": "John",
    "age": 30
}
result = validator.validate(data)

if result:
    print("Data is valid!")
else:
    print("Data is invalid.")
    print(validator.errors)
```

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request on the GitHub repository.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
