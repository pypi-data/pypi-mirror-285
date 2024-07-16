import jsonschema
import yaml
import json


def load_file(path: str) -> dict:
    """load_file
    Loads a YAML or JSON file safely
    Uses `load_string` to parse the YAML or JSON file to a Python Object.

    Arguments:
        path {str} -- The path to the file

    Returns:
        dict -- Parsed Python object of the file
    """
    with open(str(path)) as f:
        return load_string(f.read())


def load_string(data: str) -> dict:
    """load_string
    Loads a given string and parses it a JSON or YAML

    Arguments:
        data {str} -- The string to parse (JSON/YAML string)

    Returns:
        dict -- The python object created from the data
    """
    try:
        return _load_json(data)
    except json.JSONDecodeError:
        return _load_yaml(data)


def _load_json(data: str) -> dict:
    return json.loads(data)


def _load_yaml(data: str) -> dict:
    return yaml.safe_load(data)
