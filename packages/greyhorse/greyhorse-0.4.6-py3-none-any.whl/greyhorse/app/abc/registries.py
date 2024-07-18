from abc import ABC, abstractmethod

from .providers import (
    AnyProvider, ForwardProvider, FactoryProvider, MutContextProvider, AnyComponentProvider, ContextProvider,
)


class _ProviderGetter[P: AnyProvider](ABC):
    @abstractmethod
    def get_provider(self, key: type[P], name: str | None = None) -> P | None:
        ...

    @abstractmethod
    def has_provider(self, key: type[P], name: str | None = None) -> bool:
        ...


class _ProviderSetter[P: AnyProvider](ABC):
    @abstractmethod
    def add_provider(self, key: type[P], instance: P, name: str | None = None) -> bool:
        ...

    @abstractmethod
    def remove_provider(self, key: type[P], name: str | None = None) -> bool:
        ...


class IfaceCtrlRegistry(
    _ProviderGetter[AnyComponentProvider],  # From current module
    ABC,
):
    pass


class IfaceCtrlMutRegistry(
    _ProviderSetter[FactoryProvider | MutContextProvider],  # To super-module
    ABC,
):
    pass


class ResCtrlRegistry(
    _ProviderGetter[AnyComponentProvider],   # From current module
    ABC,
):
    pass


class ResCtrlMutRegistry(
    _ProviderSetter[ForwardProvider | ContextProvider],  # To submodules
    ABC,
):
    pass


class IfaceSrvRegistry(
    _ProviderGetter[FactoryProvider | MutContextProvider],  # From submodules
    ABC,
):
    pass


class IfaceSrvMutRegistry(
    _ProviderSetter[AnyComponentProvider],  # To current module
    ABC,
):
    pass


class ResSrvRegistry(
    _ProviderGetter[ForwardProvider | ContextProvider],  # From super-module
    ABC,
):
    pass


class ResSrvMutRegistry(
    _ProviderSetter[AnyComponentProvider],  # To current module
    ABC,
):
    pass
