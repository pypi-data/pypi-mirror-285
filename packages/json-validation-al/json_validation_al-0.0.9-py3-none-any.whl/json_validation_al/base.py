from abc import ABC

class EventValidationBase(ABC):

    def get_validation_schema(self, file_path: str) -> dict:
        """
        Reads a JSON schema from a file and returns it as a dictionary.

        Parameters:
        - file_path (str): The path to the JSON schema file.

        Returns:
        - dict: The JSON schema as a dictionary.

        Raises:
        - FileNotFoundError: If the file does not exist.
        - json.JSONDecodeError: If the file is not valid JSON.
        """

    def do_validation(self, event: dict, schema: dict) -> tuple:
        """
        Validates an event against a JSON schema.

        Parameters:
        - event (dict): The event to validate.
        - schema (dict): The JSON schema to validate against.

        Returns:
        - tuple: True if the event is valid, False otherwise. Also returns an array of error messages when validation fails.
        """