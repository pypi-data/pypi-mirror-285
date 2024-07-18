from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Mapping, TYPE_CHECKING, cast

from .registries import InterfaceCtrlRegistry, InterfaceCtrlMutRegistry, ResCtrlRegistry, ResCtrlMutRegistry
from greyhorse.result import Result


class Controller(ABC):
    @abstractmethod
    def create(self) -> Awaitable[Result] | Result:
        ...

    @abstractmethod
    def destroy(self) -> Awaitable[Result] | Result:
        ...

    @abstractmethod
    def start(self) -> Awaitable[None] | None:
        ...

    @abstractmethod
    def stop(self) -> Awaitable[None] | None:
        ...

    @property
    @abstractmethod
    def active(self) -> bool:
        ...


class InterfaceController(Controller, ABC):
    def __init__(
        self, registry: InterfaceCtrlRegistry | None = None,
        mut_registry: InterfaceCtrlMutRegistry | None = None,
    ):
        self._registry = registry
        self._mut_registry = mut_registry

    def set_registries(
        self, prv_registry: InterfaceCtrlRegistry,
        mut_prv_registry: InterfaceCtrlMutRegistry,
    ):
        self._registry = prv_registry
        self._mut_registry = mut_prv_registry

    def reset_registries(self):
        self._registry = None
        self._mut_registry = None


class ResourceController(Controller, ABC):
    def __init__(
        self, registry: ResCtrlRegistry | None = None,
        mut_registry: ResCtrlMutRegistry | None = None,
    ):
        self._registry = registry
        self._mut_registry = mut_registry

    def set_registries(
        self, prv_registry: ResCtrlRegistry,
        mut_prv_registry: ResCtrlMutRegistry,
    ):
        self._registry = prv_registry
        self._mut_registry = mut_prv_registry

    def reset_registries(self):
        self._registry = None
        self._mut_registry = None
