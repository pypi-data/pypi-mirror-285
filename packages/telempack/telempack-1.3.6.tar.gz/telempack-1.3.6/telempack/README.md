# Telemetry Package for Python (telempack)
This current version only supports open telemetry exporting. There are two objects (Resource & Observer) that you will import from telempack. First fill out the parameters for the Resource object then instantiate an Observer object passing through one paramater - the Resource object. Note that prod is the only environment that will export data to datadog. That's it. For an example, look in telempack/examples/example-telempack.py

# Installation
You can install this package via pip xor poetry.

## Pip
If your service primarily uses pip, then check out [eog's piphub](https://piphub.eogresources.com/). Inside the simple index you can find "telempack" which is this package. To install with pip, run this command (note the whitespace):
- `pip install --index-url http://piphub.eogresources.com/simple/ telempack`

## Poetry
In order to install this package from eog's internal pypi server please run these commands in order (note in config command you can replace '.eog' with a tag of your choice but you have to replace it in the next command too):
- `poetry config repositories.eog https://piphub.eogresources.com/simple/`
- `poetry add telempack --source eog`

And to update the package: 
- `poetry update telempack`

# Example Usage
> Be sure to instantiate the Observer and create the Resource in the same area you add your middleware and routes (preferably before both & after app instantiation).
See example-telempack.py in telempack/examples/example-telempack.py
Run script: `python -m telempack.examples.example-telempack`

## Configure Resource Object Parameters
- export_endpoint: str = "https://datadog-agent.svc.eogresources.com" [REQUIRED]
- app_env: str = "dev"||"stage"||"prod"||"local"[REQUIRED]
- app: Union[FastAPI, Flask] (flask currently not fully support) [REQUIRED]
- logger_obj: logging.Logger (optional, one is created if not provided)
- is_ddprofiler_on: bool = False (not supported until version 2.0.0)

## Note on Exporting to Datadog
> The export_endpoint link will change and your team will have a specific link. Hardcoding each link for traces, metrics, and logs is okay but not recommended; instead try adding it to your environment variables.