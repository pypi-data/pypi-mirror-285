from abc import ABC, abstractmethod
from typing import Awaitable, override, Union

from greyhorse.app.context import Context, SyncContext, AsyncContext, MutContext, SyncMutContext, AsyncMutContext


class ContextOperator(ABC):
    @abstractmethod
    def accept(self, instance: Context) -> Awaitable[None] | None:
        ...

    @abstractmethod
    def reclaim(self) -> Awaitable[Context] | Context:
        ...


class MutContextOperator(ABC):
    @abstractmethod
    def accept(self, instance: MutContext) -> Awaitable[None] | None:
        ...

    @abstractmethod
    def reclaim(self) -> Awaitable[MutContext] | MutContext:
        ...

