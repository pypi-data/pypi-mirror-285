import logging
from typing import Dict, Optional, Union

from fastapi import FastAPI
from flask import Flask
from pydantic import BaseModel, ConfigDict, Field

from .utils.logger import default_logger

# TODO: Take inputs for ddtrace manual instrumentation tags
"""
Resource object is required and given as input to Observer object
"""


class Resource(BaseModel):
    # FIXME DEFAULT_TRACES_EXPORT_PATH = "v1/traces"
    # TODO: Optional[AnyUrl] for endpoint in future
    export_endpoint: Optional[str] = (
        "console"  # "http://localhost:4318/" # append: v1/traces , v1/metrics , v1/logs
    )
    logger_obj: logging.Logger = default_logger
    app: Union[FastAPI, Flask]
    app_env: str = "dev"  # "dev"|"stage"|"prod"|"local"
    app_name: Optional[str] = (
        None  # default defined dynamic in Observer if Flask or FastAPI
    )
    is_local: Optional[bool] = False
    version: Optional[str]  # default defined dynamic in Observer if Flask or FastAPI
    is_ddprofiler_on: bool = False  # Datadog profiler default disabled
    additional_info: Optional[Dict[str, str]] = Field(default_factory=dict)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            logging.Logger: lambda v: f"Logger(name={v.name})",
            FastAPI: lambda v: f"FastAPI(app={v.title})",
            Flask: lambda v: f"Flask(app={v.name})",
        },
    )

    # String Representation of Resource Object
    # def __repr__(self):
    #     return (f"Resource(export_endpoint={self.export_endpoint}, "
    #             f"logger_obj={self.logger_obj}, app={self.app}, app_env={self.app_env}, "
    #             f"is_local={self.is_local}, version={self.version}, additional_info={self.additional_info})")
