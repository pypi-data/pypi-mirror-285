"""
Example: Shows use case on package's objects [Resource, Observer].
Run from console: `python -m telempack.examples.example-telempack`
"""

import logging

from fastapi import FastAPI

from telempack.telemetry import Observer, Resource

resource_data = Resource(
    export_endpoint="https://api.datadoghq.com/",
    logger_obj=logging.getLogger("my_logger"),
    app=FastAPI(title="example1"),
    app_env="dev",
    is_local=True,
    version="1.0.0",
    additional_info={"additional_attr1": "value1", "additional_attr2": "value2"},
)
print(resource_data.model_dump_json(indent=2))
observer = Observer(resource_data)
print(observer)

# Example of editing options
# observer.edit_options(
#     observer,
#     export_endpoint="https://api.datadoghq.com/",
#     app_env="prod"
# )
# new_resource = observer.get_resource()
# print(new_resource.model_dump_json(indent=2))
