from collections import defaultdict
from typing import Pattern, Any, override

from ..abc.controller import InterfaceController, ResourceController
from ..abc.providers import ForwardProvider, AnyComponentProvider, FactoryProvider, MutContextProvider, ContextProvider
from ..abc.registries import ResCtrlRegistry, ResCtrlMutRegistry, \
    ResSrvRegistry, ResSrvMutRegistry, IfaceCtrlRegistry, IfaceCtrlMutRegistry, IfaceSrvRegistry, IfaceSrvMutRegistry
from ..abc.service import InterfaceService, ResourceService
from ..errors import PolicyViolation, PolicyPatternViolation
from ..schemas.controller import IfaceCtrlGetPolicy, ResCtrlGetPolicy, IfaceCtrlSetPolicy, ResCtrlSetPolicy
from ..schemas.service import IfaceSrvGetPolicy, ResSrvGetPolicy, IfaceSrvSetPolicy, ResSrvSetPolicy
from ..utils.registry import Registry, MutableRegistry
from ...logging import logger


class _BasicPolicyAwareRegistry:
    class_: type[InterfaceController | ResourceController | InterfaceService | ResourceService]
    unit_type: str

    def __init__(
        self,
        policies: list[IfaceCtrlGetPolicy | ResCtrlGetPolicy | IfaceSrvGetPolicy | ResSrvGetPolicy],
        registry: Registry[type, Any],
    ):
        self._policies: dict[type, list[Pattern]] = defaultdict(list)
        self._registry = registry

        for policy in policies:
            if policy.name_pattern is None:
                self._policies[policy.key].clear()
                break
            else:
                self._policies[policy.key].append(policy.name_pattern)

    def _check_policies(self, key: type, name: str | None = None) -> bool:
        if key not in self._policies:
            error = PolicyViolation(
                type='GET', entity=self.unit_type,
                class_=str(self.class_.__name__),
                key=str(key.__name__),
            )
            logger.warning(error.message)
            return False

        if len(self._policies[key]) == 0:
            return True

        for existing_name in self._registry.get_names(key):
            if name is None and '' == existing_name:
                return True

            for pattern in self._policies[key]:
                if pattern.match(existing_name) and existing_name == name:
                    return True

        error = PolicyPatternViolation(
            type='GET', entity=self.unit_type,
            class_=str(self.class_.__name__),
            key=str(key.__name__), name=name,
        )
        logger.warning(error.message)
        return False


class _BasicPolicyAwareMutRegistry:
    class_: type[InterfaceController | ResourceController | InterfaceService | ResourceService]
    unit_type: str

    def __init__(
        self,
        policies: list[IfaceCtrlSetPolicy | ResCtrlSetPolicy | IfaceSrvSetPolicy | ResSrvSetPolicy],
        registry: MutableRegistry[type, Any],
    ):
        self._policies: dict[type, list[Pattern]] = defaultdict(list)
        self._registry = registry

        for policy in policies:
            if policy.name_pattern is None:
                self._policies[policy.key].clear()
                break
            else:
                self._policies[policy.key].append(policy.name_pattern)

    def _check_policies(self, key: type, name: str | None = None) -> bool:
        if key not in self._policies:
            error = PolicyViolation(
                type='SET', entity=self.unit_type,
                class_=str(self.class_.__name__),
                key=str(key.__name__),
            )
            logger.warning(error.message)
            return False

        if len(self._policies[key]) == 0:
            return True

        for existing_name in self._registry.get_names(key):
            if name is None and '' == existing_name:
                return True

            for pattern in self._policies[key]:
                if pattern.match(existing_name) and existing_name == name:
                    return True

        error = PolicyPatternViolation(
            type='SET', entity=self.unit_type,
            class_=str(self.class_.__name__),
            key=str(key.__name__), name=name,
        )
        logger.warning(error.message)
        return False


class _PolicyAwareRegistry[PolicyT, ProvT](_BasicPolicyAwareRegistry):
    def __init__(
        self, policies: list[PolicyT],
        registry: Registry[type, Any],
    ):
        super().__init__(policies, registry)

    def get_provider(
        self, key: type[ProvT], name: str | None = None,
    ) -> ProvT | None:
        if not self._check_policies(key, name):
            return None
        return self._registry.get(key, name)

    def has_provider(
        self, key: type[ProvT], name: str | None = None,
    ) -> bool:
        if not self._check_policies(key, name):
            return False
        return self._registry.has(key, name)


class _PolicyAwareMutRegistry[PolicyT, ProvT](_BasicPolicyAwareMutRegistry):
    def __init__(
        self, policies: list[PolicyT],
        registry: MutableRegistry[type, Any],
    ):
        super().__init__(policies, registry)

    def add_provider(
        self, key: type[ProvT], instance: ProvT, name: str | None = None,
    ) -> bool:
        if not self._check_policies(key, name):
            return False
        return self._registry.set(key, instance, name)

    def remove_provider(
        self, key: type[ProvT], name: str | None = None,
    ) -> bool:
        if not self._check_policies(key, name):
            return False
        return self._registry.reset(key, name)


class IfaceCtrlRegistryImpl(
    _PolicyAwareRegistry[IfaceCtrlGetPolicy, AnyComponentProvider],
    IfaceCtrlRegistry,
):
    class_ = InterfaceController
    unit_type = 'controller'


class IfaceCtrlMutRegistryImpl(
    _PolicyAwareMutRegistry[IfaceCtrlSetPolicy, FactoryProvider | MutContextProvider],
    IfaceCtrlMutRegistry,
):
    class_ = InterfaceController
    unit_type = 'controller'


class ResCtrlRegistryImpl(
    _PolicyAwareRegistry[ResCtrlGetPolicy, AnyComponentProvider],
    ResCtrlRegistry,
):
    class_ = ResourceController
    unit_type = 'controller'


class ResCtrlMutRegistryImpl(
    _PolicyAwareMutRegistry[ResCtrlSetPolicy, ForwardProvider | ContextProvider],
    ResCtrlMutRegistry,
):
    class_ = ResourceController
    unit_type = 'controller'


class IfaceSrvRegistryImpl(
    _PolicyAwareRegistry[IfaceSrvGetPolicy, FactoryProvider | MutContextProvider],
    IfaceSrvRegistry,
):
    class_ = InterfaceService
    unit_type = 'service'


class InterfaceSrvMutRegistryImpl(
    _PolicyAwareMutRegistry[IfaceSrvSetPolicy, AnyComponentProvider],
    IfaceSrvMutRegistry,
):
    class_ = InterfaceService
    unit_type = 'service'


class ResSrvRegistryImpl(
    _PolicyAwareRegistry[ResSrvGetPolicy, ForwardProvider | ContextProvider],
    ResSrvRegistry,
):
    class_ = ResourceService
    unit_type = 'service'


class ResSrvMutRegistryImpl(
    _PolicyAwareMutRegistry[ResSrvSetPolicy, AnyComponentProvider],
    ResSrvMutRegistry,
):
    class_ = ResourceService
    unit_type = 'service'
