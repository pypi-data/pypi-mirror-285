# Snow Way Out

Simple Python wrapper for making api calls to ServiceNow.

## Development

Clone the repo and install dependencies into a local virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --editable .
```

### Tests

Export variables for your environment, otherwise the test will prompt you for input.

```sh
export SNOW_ENDPOINT="https://example.service-now.com"
export SNOW_API_USERNAME=example
export SNOW_API_PASSWORD=hunter2
pytest
```
