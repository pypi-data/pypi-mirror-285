from typing import Pattern, Any

from pydantic import BaseModel, Field

from ..abc.controller import Controller, InterfaceController, ResourceController
from ..abc.providers import ForwardProvider, AnyComponentProvider, FactoryProvider, MutContextProvider, ContextProvider


class IfaceCtrlGetPolicy(BaseModel, frozen=True, arbitrary_types_allowed=True):
    key: type[AnyComponentProvider]
    name_pattern: Pattern | None = None


class IfaceCtrlSetPolicy(BaseModel, frozen=True, arbitrary_types_allowed=True):
    key: type[FactoryProvider | MutContextProvider]
    name_pattern: Pattern | None = None


class ResCtrlGetPolicy(BaseModel, frozen=True, arbitrary_types_allowed=True):
    key: type[AnyComponentProvider]
    name_pattern: Pattern | None = None


class ResCtrlSetPolicy(BaseModel, frozen=True, arbitrary_types_allowed=True):
    key: type[ForwardProvider | ContextProvider]
    name_pattern: Pattern | None = None


class IfaceCtrlConf(BaseModel, frozen=True):
    key: type[InterfaceController]
    name: str | None = None
    args: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = Field(default=True)
    providers_get: list[IfaceCtrlGetPolicy] = Field(default_factory=list)
    providers_set: list[IfaceCtrlSetPolicy] = Field(default_factory=list)


class ResCtrlConf(BaseModel, frozen=True):
    key: type[ResourceController]
    name: str | None = None
    args: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = Field(default=True)
    providers_get: list[ResCtrlGetPolicy] = Field(default_factory=list)
    providers_set: list[ResCtrlSetPolicy] = Field(default_factory=list)
