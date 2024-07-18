from typing import Any, Callable, Optional, Pattern, Mapping

from pydantic import BaseModel, Field, PrivateAttr

from greyhorse.result import Result
from greyhorse.utils.invoke import caller_path
from .controller import IfaceCtrlConf, ResCtrlConf
from .service import IfaceSrvConf, ResSrvConf
from ..abc.controller import Controller
from ..abc.providers import ForwardProvider, ContextProvider, FactoryProvider, MutContextProvider
from ..abc.service import Service
from ..entities.module import Module

type ControllerFactoryFn = Callable[[...], Result[Controller]]
type ControllerFactories = Mapping[type[Controller], ControllerFactoryFn]
type ServiceFactoryFn = Callable[[...], Result[Service]]
type ServiceFactories = Mapping[type[Service], ServiceFactoryFn]


class ProviderClaim(BaseModel, frozen=True, arbitrary_types_allowed=True):
    key: type[ForwardProvider | ContextProvider]
    # name_pattern: Pattern | None = None


class ProviderGrant(BaseModel, frozen=True, arbitrary_types_allowed=True):
    key: type[ForwardProvider | ContextProvider]
    name_pattern: Pattern | None = None


class ProviderImport(BaseModel, frozen=True, arbitrary_types_allowed=True):
    key: type[FactoryProvider | MutContextProvider]
    # name_pattern: Pattern | None = None


class ProviderExport(BaseModel, frozen=True, arbitrary_types_allowed=True):
    key: type[FactoryProvider | MutContextProvider]
    name_pattern: Pattern | None = None


class ModuleDesc(BaseModel):
    path: str = Field(frozen=True)
    args: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = Field(default=True, frozen=True)

    provider_grants: list[ProviderGrant] = Field(default_factory=list)
    provider_imports: list[ProviderImport] = Field(default_factory=list)

    _conf: Optional['ModuleConf'] = PrivateAttr(default=None)
    _initpath: list[str] = PrivateAttr(default_factory=lambda: caller_path(5))


class ModuleConf(BaseModel, arbitrary_types_allowed=True):
    name: str = Field(frozen=True)
    enabled: bool = Field(default=True)
    factory: Callable[[...], Module] = Field(default=Module, frozen=True)

    submodules: list[ModuleDesc] = Field(default_factory=list)

    controllers: list[IfaceCtrlConf | ResCtrlConf] = Field(default_factory=list)
    services: list[IfaceSrvConf | ResSrvConf] = Field(default_factory=list)

    controller_factories: ControllerFactories = Field(default_factory=dict)
    service_factories: ServiceFactories = Field(default_factory=dict)

    provider_claims: list[ProviderClaim] = Field(default_factory=list)
    provider_exports: list[ProviderExport] = Field(default_factory=list)
