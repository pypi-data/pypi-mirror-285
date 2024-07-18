from typing import Pattern, Any

from pydantic import BaseModel, Field

from ..abc.service import Service, InterfaceService, ResourceService
from ..abc.providers import ForwardProvider, FactoryProvider, MutContextProvider, AnyComponentProvider, ContextProvider


class IfaceSrvGetPolicy(BaseModel, frozen=True, arbitrary_types_allowed=True):
    key: type[FactoryProvider | MutContextProvider]
    name_pattern: Pattern | None = None


class IfaceSrvSetPolicy(BaseModel, frozen=True, arbitrary_types_allowed=True):
    key: type[AnyComponentProvider]
    name_pattern: Pattern | None = None


class ResSrvGetPolicy(BaseModel, frozen=True, arbitrary_types_allowed=True):
    key: type[ForwardProvider | ContextProvider]
    name_pattern: Pattern | None = None


class ResSrvSetPolicy(BaseModel, frozen=True, arbitrary_types_allowed=True):
    key: type[AnyComponentProvider]
    name_pattern: Pattern | None = None


class IfaceSrvConf(BaseModel, frozen=True):
    key: type[InterfaceService]
    name: str | None = None
    args: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = Field(default=True)
    providers_get: list[IfaceSrvGetPolicy] = Field(default_factory=list)
    providers_set: list[IfaceSrvSetPolicy] = Field(default_factory=list)


class ResSrvConf(BaseModel, frozen=True):
    key: type[ResourceService]
    name: str | None = None
    args: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = Field(default=True)
    providers_get: list[ResSrvGetPolicy] = Field(default_factory=list)
    providers_set: list[ResSrvSetPolicy] = Field(default_factory=list)
