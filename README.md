# QPI

This codebase is the source for the DIPAAL api found at https://dipaal.dk

# Development

## Setup
Copy the file config-local-template.properties to config-local.properties and change the desired values if applicable.

## Running

### Docker

1. ```docker build -t dipaal-api .```
2. ```docker run -p 8000:8000 dipaal-api uvicorn app.api_main:app --reload --host 0.0.0.0```

### Native

Ensure that python 3.11 is installed, and install the PIP dependencies with `pip install -r requirements.txt`.

To run the api, use uvicorn `uvicorn app.api_main:app --reload`.