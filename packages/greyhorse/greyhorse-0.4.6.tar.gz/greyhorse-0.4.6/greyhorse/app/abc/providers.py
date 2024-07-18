from abc import ABC, abstractmethod
from typing import Awaitable, override, Union

from greyhorse.app.context import Context, SyncContext, AsyncContext, MutContext, SyncMutContext, AsyncMutContext
from greyhorse.result import Result


class FactoryProvider[T](ABC):
    @abstractmethod
    def create(self) -> Awaitable[T] | T:
        ...

    @abstractmethod
    def destroy(self, instance: T) -> Awaitable[None] | None:
        ...


class SyncFactoryProvider[T](FactoryProvider[T], ABC):
    @override
    @abstractmethod
    def create(self) -> T:
        ...

    @override
    @abstractmethod
    def destroy(self, instance: T) -> None:
        ...


class AsyncFactoryProvider[T](FactoryProvider[T], ABC):
    @override
    @abstractmethod
    async def create(self) -> T:
        ...

    @override
    @abstractmethod
    async def destroy(self, instance: T) -> None:
        ...


class ForwardProvider[T](ABC):
    @abstractmethod
    def take(self) -> Awaitable[T] | T | None:
        ...

    @abstractmethod
    def drop(self, instance: T) -> Awaitable[None] | None:
        ...

    @abstractmethod
    def __bool__(self) -> bool:
        ...


class SyncForwardProvider[T](ForwardProvider[T], ABC):
    @override
    @abstractmethod
    def take(self) -> T | None:
        ...

    @override
    @abstractmethod
    def drop(self, instance: T) -> None:
        ...


class AsyncForwardProvider[T](ForwardProvider[T], ABC):
    @override
    @abstractmethod
    async def take(self) -> T | None:
        ...

    @override
    @abstractmethod
    async def drop(self, instance: T) -> None:
        ...


class ContextProvider(ABC):
    @abstractmethod
    def borrow(self) -> Awaitable[Context] | Context:
        ...

    @abstractmethod
    def release(self, instance: Context) -> Awaitable[None] | None:
        ...


class SyncContextProvider[T](ContextProvider, ABC):
    @override
    @abstractmethod
    def borrow(self) -> SyncContext[T]:
        ...

    @override
    @abstractmethod
    def release(self, instance: SyncContext[T]) -> None:
        ...


class AsyncContextProvider[T](ContextProvider, ABC):
    @override
    @abstractmethod
    async def borrow(self) -> AsyncContext[T]:
        ...

    @override
    @abstractmethod
    async def release(self, instance: AsyncContext[T]) -> None:
        ...


class MutContextProvider(ABC):
    @abstractmethod
    def acquire(self) -> Awaitable[MutContext] | MutContext:
        ...

    @abstractmethod
    def release(self, instance: MutContext) -> Awaitable[None] | None:
        ...


class SyncMutContextProvider[T](MutContextProvider, ABC):
    @override
    @abstractmethod
    def acquire(self) -> SyncMutContext[T]:
        ...

    @override
    @abstractmethod
    def release(self, instance: SyncMutContext[T]) -> None:
        ...


class AsyncMutContextProvider[T](MutContextProvider, ABC):
    @override
    @abstractmethod
    async def acquire(self) -> AsyncMutContext[T]:
        ...

    @override
    @abstractmethod
    async def release(self, instance: AsyncMutContext[T]) -> None:
        ...


AnyProvider = Union[FactoryProvider, ForwardProvider, ContextProvider, MutContextProvider]
AnyComponentProvider = Union[ContextProvider, MutContextProvider]
