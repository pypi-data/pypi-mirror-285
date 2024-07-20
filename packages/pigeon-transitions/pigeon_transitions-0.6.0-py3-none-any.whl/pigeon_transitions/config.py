from pydantic import BaseModel, model_validator, field_validator, ConfigDict
from typing import List, Optional, Mapping
from importlib import import_module
from copy import copy
from .base import BaseMachine


class MachineConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str
    states: Optional[List[str | Mapping[str, str | Mapping[str, str]]]] = None
    transitions: Optional[List[str] | List[Mapping[str, str]]] = None
    initial: Optional[str] = None

    @field_validator("type")
    @classmethod
    def get_class(cls, type: str):
        package_name = ".".join(type.split(".")[:-1])
        class_name = type.split(".")[-1]
        package = import_module(package_name)
        class_obj = getattr(package, class_name)
        assert issubclass(class_obj, BaseMachine)
        return class_obj

    @property
    def _as_dict(self):
        d = copy(self.__dict__)
        d.update(self.__pydantic_extra__)
        return {k: v for k, v in d.items() if v is not None}


class PigeonTransitionsConfig(BaseModel):
    machines: Mapping[str, MachineConfig]
