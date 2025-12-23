import os
from enum import Enum


class ServiceEnv(str, Enum):
    PRODUCTION = "production"
    LOCAL = "local"


ENV = ServiceEnv(os.getenv("ENV", ServiceEnv.LOCAL))
