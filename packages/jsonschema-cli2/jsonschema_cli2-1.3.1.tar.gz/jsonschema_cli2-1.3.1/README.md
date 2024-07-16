This is based on the frok from [jsonschema-cli](https://github.com/eyal-mor/jsonschema-cli.git).

# JsonSchema CLI

A thin wrapper over [Python Jsonschema](https://github.com/Julian/jsonschema) to allow validating shcemas easily using simple CLI commands.

## Installing

`pip install jsonschema-cli2`

## Security

The `$ref` resolving will automatically resolve to any path using basic `$ref` notation:

```json
{"$ref": "my-custom.json#...."}
```

That means that when using this tool, an attacker may do the following:

```json
{"$ref": "../../../../all-my-secrets.json"}
```

To make sure this doesn't happen:

1. When using this tool in a backend server, make sure the file access is scoped.
2. Don't run JSONSCHEMAS without sanitizing paths.
3. Treat all un-knwon user input as evil.

This has no actual current  affect other than loading the contets of secrets into memory of the process.
But may lead to misfortune if not addressed.

## Usgae

Using `jsonschema-cli --help`

```bash
usage: jsonschema-cli [-h] {validate} ...

A wrapper around https://github.com/Julian/jsonschema to validate JSON using the CLI

positional arguments:
  {validate}  Validate thet json data with a schema
    validate  Validate

optional arguments:
  -h, --help  show this help message and exit
```

### Validate

Using `jsonschema-cli validate --help`

```bash
usage: jsonschema-cli validate [-h] schema_file_or_string data_file_or_string

positional arguments:
  schema_file_or_string
                        The schema you want to use to validate the data
  data_file_or_string   The data you want validated by the schema

optional arguments:
  -h, --help            show this help message and exit
```

### Examples

```bash
# Returns no errors on stdout, no output needed on success (just exit code 0 is enough)
jsonschema-cli validate '{"properties": {"number": {"type": "integer"}}, "required": ["number"]}' '{"number": 123}'
# Has an error, "number" is now "123" instead of 123, an integer is expected.
jsonschema-cli validate '{"properties": {"number": {"type": "integer"}}, "required": ["number"]}' '{"number": "123"}'
> '123' is not of type 'integer'
>
> Failed validating 'type' in schema['properties']['number']:
>     {'type': 'integer'}
>
> On instance['number']:
>     '123'
```

## Load YAML

The CLI command can read YAML and validate both schema and data written in YAML

```bash
# Returns no errors on stdout, no output needed on success (just exit code 0 is enough)
SCHEMA="
properties:
  number:
    type: integer
"
DATA="
number: 123
"
jsonschema-cli validate "$SCHEMA" "$DATA"
# Has an error, "number" is now "123" instead of 123, an integer is expected.
SCHEMA="
properties:
  number:
    type: integer
"
DATA="
number: \"123\"
"
jsonschema-cli validate "$SCHEMA" "$DATA"
> '123' is not of type 'integer'
>
> Failed validating 'type' in schema['properties']['number']:
>     {'type': 'integer'}
>
> On instance['number']:
>     '123'
```
