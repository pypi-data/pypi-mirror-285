# trash_collector

Python cli to easily help clean old folders and free up disk space.
Use `py -m trash_collector --help` to see the available commands.
or `python3 -m trash_collector --help` if you are using a linux system.

[Pypi here](https://pypi.org/project/trash-collector/)

## Develop

Setup a venv, activate it and install the requirements

```bash
py -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Testing

Run the tests

```bash
py -m pytest tests
```

## Build

`py -m pip install --upgrade build`
`py -m build`

## Build to test

`pip install .`
