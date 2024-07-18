import asyncio
import threading
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Mapping, TYPE_CHECKING, cast, override

from .registries import InterfaceSrvRegistry, InterfaceSrvMutRegistry, ResSrvRegistry, ResSrvMutRegistry
from greyhorse.result import Result


class Service(ABC):
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

    @abstractmethod
    def wait(self) -> threading.Event | asyncio.Event:
        ...


class InterfaceService(Service, ABC):
    def __init__(
        self, registry: InterfaceSrvRegistry | None = None,
        mut_registry: InterfaceSrvMutRegistry | None = None,
    ):
        self._registry = registry
        self._mut_registry = mut_registry

    def set_registries(
        self, prv_registry: InterfaceSrvRegistry,
        mut_prv_registry: InterfaceSrvMutRegistry,
    ):
        self._registry = prv_registry
        self._mut_registry = mut_prv_registry

    def reset_registries(self):
        self._registry = None
        self._mut_registry = None


class ResourceService(Service, ABC):
    def __init__(
        self, registry: ResSrvRegistry | None = None,
        mut_registry: ResSrvMutRegistry | None = None,
    ):
        self._registry = registry
        self._mut_registry = mut_registry

    def set_registries(
        self, prv_registry: ResSrvRegistry,
        mut_prv_registry: ResSrvMutRegistry,
    ):
        self._registry = prv_registry
        self._mut_registry = mut_prv_registry

    def reset_registries(self):
        self._registry = None
        self._mut_registry = None


class SyncService(Service):
    def __init__(self, *args, **kwargs):
        super(SyncService, self).__init__(*args, **kwargs)
        self._event = threading.Event()

    @override
    def create(self) -> Result:
        return Result.from_ok()

    @override
    def destroy(self) -> Result:
        return Result.from_ok()

    @override
    def start(self) -> None:
        self._event.clear()

    @override
    def stop(self) -> None:
        self._event.set()

    @override
    @property
    def active(self) -> bool:
        return not self._event.is_set()

    @override
    def wait(self) -> threading.Event:
        return self._event


class AsyncService(Service):
    def __init__(self, *args, **kwargs):
        super(AsyncService, self).__init__(*args, **kwargs)
        self._event = asyncio.Event()

    @override
    async def create(self) -> Result:
        return Result.from_ok()

    @override
    async def destroy(self) -> Result:
        return Result.from_ok()

    @override
    async def start(self) -> None:
        self._event.clear()

    @override
    async def stop(self) -> None:
        self._event.set()

    @override
    @property
    def active(self) -> bool:
        return not self._event.is_set()

    @override
    def wait(self) -> asyncio.Event:
        return self._event
