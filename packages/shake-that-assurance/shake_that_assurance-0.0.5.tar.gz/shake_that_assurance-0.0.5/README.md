# API Wrapper

Python wrapper for making calls to Oracle Communications Unified Assurance, previously known as Assure1 and Monolith. It connects to the Presentation Server.

## Development

Clone the repo and install dependencies into a local virtual environment.

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install --editable .
```

### Tests

Export variables for your environment, otherwise the test will prompt you for input.

```sh
export UA_API_USER=example
export UA_API_PASS=hunter2
export UA_FQDN='https://presentation-server01.example.com'
pytest
```

### Error Handling

* If you see an `requests.exceptions.SSLError` error or something similar, it usually just means Apache is overwhelmed and failed to respond. This typically happens when making successive queries and happens more or less randomly. We already retry after waiting with an exponential backoff. If it stalls for too long, try starting over again.

* Another transient bug in the API can cause the script to throw `IndexError` (needs investigation). Just re-run the script for now.

* If you see database errors like below, it likely means you've exhaused the maximum connections to Oracle MySQL. You should probably increase the max connections or it will just keep happening.

    ```php
    WARNING: API responded with failure: {"success":false,"message":"PHP Exception<ul><li>\/opt\/assure1\/www\/api\/lib\/Model.php on line 997<\/li><ul><li>Error connecting to [Assure1] database. Please contact your administrator<\/li><\/ul><\/ul>","data":[]}
    ```
