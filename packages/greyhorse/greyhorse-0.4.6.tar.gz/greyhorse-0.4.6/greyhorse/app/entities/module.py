from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Literal, Mapping, Self, TYPE_CHECKING, cast, override, Pattern

from pydantic import BaseModel

from greyhorse.result import Error, Result
from greyhorse.utils.invoke import invoke_sync
from ..abc.controller import Controller, InterfaceController, ResourceController
from ..abc.providers import ForwardProvider, ContextProvider
from ..abc.service import Service, InterfaceService, ResourceService
from ..errors import ProviderPolicyViolation
from ..private.registries_impl import IfaceCtrlRegistryImpl, IfaceCtrlMutRegistryImpl, ResCtrlRegistryImpl, \
    ResCtrlMutRegistryImpl, IfaceSrvRegistryImpl, InterfaceSrvMutRegistryImpl, ResSrvRegistryImpl, ResSrvMutRegistryImpl
from ..schemas.controller import IfaceCtrlConf, ResCtrlConf
from ..schemas.service import IfaceSrvConf, ResSrvConf
from ..utils.registry import DictRegistry, KeyMapping, Registry
from ...i18n import tr
from ...logging import logger

if TYPE_CHECKING:
    from ..schemas.module import ModuleConf, ProviderGrant, ModuleDesc


class ProviderInstanceGrant(BaseModel, frozen=True, arbitrary_types_allowed=True):
    key: type[ForwardProvider | ContextProvider]
    instance: ForwardProvider | ContextProvider
    name: str | None = None


@dataclass(slots=True, frozen=True)
class ModuleErrorsItem:
    where: Literal['module'] | Literal['controller'] | Literal['service'] | Literal['provider']
    name: str
    errors: list[Error] | None = None


class Module:
    def __init__(self, name: str, conf: 'ModuleConf', desc: 'ModuleDesc'):
        self._name = name
        self._conf = conf
        self._desc = desc
        self._modules: dict[str, Self] = {}
        self._controllers = DictRegistry[type[Controller], InterfaceController | ResourceController]()
        self._services = DictRegistry[type[Service], InterfaceService | ResourceService]()
        self._registry = DictRegistry[Any, Any]()

    @property
    def name(self) -> str:
        return self._name

    @property
    def config(self) -> 'ModuleConf':
        return self._conf

    def add_iface_controller(
        self, conf: IfaceCtrlConf,
        instance: InterfaceController,
        name: str | None = None,
    ):
        if self._controllers.set(conf.key, instance, name=name):
            prv_registry = IfaceCtrlRegistryImpl(conf.providers_get, self._registry)
            mut_prv_registry = IfaceCtrlMutRegistryImpl(conf.providers_set, self._registry)
            instance.set_registries(prv_registry, mut_prv_registry)

    def add_res_controller(
        self, conf: ResCtrlConf,
        instance: ResourceController,
        name: str | None = None,
    ):
        if self._controllers.set(conf.key, instance, name=name):
            prv_registry = ResCtrlRegistryImpl(conf.providers_get, self._registry)
            mut_prv_registry = ResCtrlMutRegistryImpl(conf.providers_set, self._registry)
            instance.set_registries(prv_registry, mut_prv_registry)

    def remove_controller(self, key: type[InterfaceController | ResourceController], name: str | None = None):
        if instance := self._controllers.get(key, name=name):
            self._controllers.reset(key, name=name)
            instance.reset_registries()
            del instance

    def get_controller(self, key: type[Controller], name: str | None = None) -> Controller | None:
        if instance := self._controllers.get(key, name=name):
            return cast(key, instance)
        return None

    def add_iface_service(
        self, conf: IfaceSrvConf,
        instance: InterfaceService,
        name: str | None = None,
    ):
        if self._services.set(conf.key, instance, name=name):
            prv_registry = IfaceSrvRegistryImpl(conf.providers_get, self._registry)
            mut_prv_registry = InterfaceSrvMutRegistryImpl(conf.providers_set, self._registry)
            instance.set_registries(prv_registry, mut_prv_registry)

    def add_res_service(
        self, conf: ResSrvConf,
        instance: ResourceService,
        name: str | None = None,
    ):
        if self._services.set(conf.key, instance, name=name):
            prv_registry = ResSrvRegistryImpl(conf.providers_get, self._registry)
            mut_prv_registry = ResSrvMutRegistryImpl(conf.providers_set, self._registry)
            instance.set_registries(prv_registry, mut_prv_registry)

    def remove_service(self, key: type[InterfaceService | ResourceService], name: str | None = None):
        if instance := self._services.get(key, name=name):
            self._services.reset(key, name=name)
            instance.reset_registries()
            del instance

    def get_service(self, key: type[Service], name: str | None = None) -> Service | None:
        if instance := self._services.get(key, name=name):
            return cast(key, instance)
        return None

    @property
    def module_names(self) -> list[str]:
        return list(self._modules.keys())

    @property
    def controllers_list(self) -> list[Controller]:
        result = []

        for key in self._controllers.list_keys():
            for name in self._controllers.get_names(key):
                result.append(self._controllers.get(key, name))

        return result

    @property
    def service_list(self) -> list[Service]:
        result = []

        for key in self._services.list_keys():
            for name in self._services.get_names(key):
                result.append(self._services.get(key, name))

        return result

    def add_module(self, name: str, instance: Self):
        self._modules[name] = instance

    def remove_module(self, name: str):
        self._modules.pop(name, None)

    def get_module(self, name) -> Self | None:
        return self._modules.get(name)

    def satisfy_provider_claims(self, items: list[ProviderInstanceGrant]) -> list[ModuleErrorsItem]:
        errors: list[ModuleErrorsItem] = []
        items_set: dict[type, dict[str | None, Any]] = defaultdict(dict)
        for item in items:
            items_set[item.key][item.name] = item.instance

        for claim in self.config.provider_claims:
            result = False

            for name, instance in items_set.get(claim.key, {}).items():
                if result := self._registry.set(claim.key, instance, name=name):
                    break

            if not result:
                claim_name = f'{claim.key}'
                error = ProviderPolicyViolation(type='module', name=self.name, claim_name=claim_name)
                errors.append(ModuleErrorsItem(
                    where='provider', name=claim_name, errors=[error],
                ))

        for submodule in self._modules.values():
            sub_errors = self._grant_providers(submodule)
            for error_item in sub_errors:
                errors.append(ModuleErrorsItem(
                    where='module', name=submodule.name, errors=error_item.errors,
                ))

        return errors

    def _grant_providers(self, child: Self, undo: bool = False) -> list[ModuleErrorsItem]:
        errors: list[ModuleErrorsItem] = []

        sub_desc, sub_conf = child._desc, child._conf
        claims_set = {claim.key for claim in sub_conf.provider_claims}

        for grant in sub_desc.provider_grants:
            result = False

            if grant.key in claims_set:
                if grant.name_pattern is not None:
                    for name in self._registry.get_names(grant.key):
                        if grant.name_pattern.match(name):
                            if not undo:
                                instance = self._registry.get(grant.key, name)
                                result = child._registry.set(grant.key, instance, name=name)
                            else:
                                result = child._registry.reset(grant.key, name=name)

                            if result:
                                break

                elif instance := self._registry.get(grant.key):
                    if not undo:
                        result = child._registry.set(grant.key, instance)
                    else:
                        result = child._registry.reset(grant.key)

            if not result:
                grant_name = f'{grant.key}' + (f' ("{grant.name_pattern}")' if grant.name_pattern else '')
                error = ProviderPolicyViolation(type='module', name=child.name, claim_name=grant_name)
                errors.append(ModuleErrorsItem(
                    where='provider', name=grant_name, errors=[error],
                ))

        for sub_child in sub_conf.submodules:
            for error_item in child._grant_providers(sub_child, undo):
                errors.append(ModuleErrorsItem(
                    where='module', name=sub_child.name, errors=error_item.errors,
                ))

        return errors

    def _import_providers(self, child: Self, undo: bool = False) -> list[ModuleErrorsItem]:
        errors: list[ModuleErrorsItem] = []

        sub_desc, sub_conf = child._desc, child._conf
        imports_set = {claim.key for claim in sub_desc.provider_imports}

        for sub_child in sub_conf.submodules:
            for error_item in child._import_providers(sub_child, undo):
                errors.append(ModuleErrorsItem(
                    where='module', name=sub_child.name, errors=error_item.errors,
                ))

        for export in sub_conf.provider_exports:
            result = False

            if export.key in imports_set:
                if export.name_pattern is not None:
                    for name in child._registry.get_names(export.key):
                        if export.name_pattern.match(name):
                            if not undo:
                                instance = child._registry.get(export.key, name)
                                result = self._registry.set(export.key, instance, name=name)
                            else:
                                result = self._registry.reset(export.key, name=name)

                            if result:
                                break

                elif instance := child._registry.get(export.key):
                    if not undo:
                        result = self._registry.set(export.key, instance)
                    else:
                        result = self._registry.reset(export.key)

            if not result:
                export_name = f'{export.key}' + (f' ("{export.name_pattern}")' if export.name_pattern else '')
                error = ProviderPolicyViolation(type='module', name=child.name, claim_name=export_name)
                errors.append(ModuleErrorsItem(
                    where='provider', name=export_name, errors=[error],
                ))

        return errors

    def create(self) -> list[ModuleErrorsItem]:
        errors: list[ModuleErrorsItem] = []
        logger.info(tr('app.entities.module.create-start').format(name=self.name))

        for key in self._services.list_keys():
            for name in self._services.get_names(key):
                instance = self._services.get(key, name)
                res = invoke_sync(instance.create)
                if not res.success:
                    errors.append(ModuleErrorsItem(
                        where='service', name=name, errors=res.errors,
                    ))
                else:
                    logger.info(tr('app.entities.module.service-created').format(name=name))

        for module in self._modules.values():
            sub_errors = invoke_sync(module.create)
            for error_item in sub_errors:
                errors.append(ModuleErrorsItem(
                    where='module', name=module.name, errors=error_item.errors,
                ))

        for key in self._controllers.list_keys():
            for name in self._controllers.get_names(key):
                instance = self._controllers.get(key, name)
                res = invoke_sync(instance.create)
                if not res.success:
                    errors.append(ModuleErrorsItem(
                        where='controller', name=name, errors=res.errors,
                    ))
                else:
                    logger.info(tr('app.entities.module.ctrl-created').format(name=name))

        logger.info(tr('app.entities.module.create-finish').format(name=self.name))
        return errors

    def destroy(self) -> list[ModuleErrorsItem]:
        errors: list[ModuleErrorsItem] = []
        logger.info(tr('app.entities.module.destroy-start').format(name=self.name))

        for key in self._controllers.list_keys():
            for name in self._controllers.get_names(key):
                instance = self._controllers.get(key, name)
                res = invoke_sync(instance.destroy)
                if not res.success:
                    errors.append(ModuleErrorsItem(
                        where='controller', name=name, errors=res.errors,
                    ))
                else:
                    logger.info(tr('app.entities.module.ctrl-destroyed').format(name=name))

        for module in self._modules.values():
            sub_errors = invoke_sync(module.destroy)
            for error_item in sub_errors:
                errors.append(ModuleErrorsItem(
                    where='module', name=module.name, errors=error_item.errors,
                ))

        for key in self._services.list_keys():
            for name in self._services.get_names(key):
                instance = self._services.get(key, name)
                res = invoke_sync(instance.destroy)
                if not res.success:
                    errors.append(ModuleErrorsItem(
                        where='service', name=name, errors=res.errors,
                    ))
                else:
                    logger.info(tr('app.entities.module.service-destroyed').format(name=name))

        logger.info(tr('app.entities.module.destroy-finish').format(name=self.name))
        return errors

    def start(self):
        logger.info(tr('app.entities.module.start-start').format(name=self.name))

        for key in self._controllers.list_keys():
            for name in self._controllers.get_names(key):
                instance = self._controllers.get(key, name)
                invoke_sync(instance.start)
                logger.info(tr('app.entities.module.ctrl-started').format(name=name))

        for module in self._modules.values():
            module.start()

        for key in self._services.list_keys():
            for name in self._services.get_names(key):
                instance = self._services.get(key, name)
                invoke_sync(instance.start)
                logger.info(tr('app.entities.module.service-started').format(name=name))

        logger.info(tr('app.entities.module.start-finish').format(name=self.name))

    def stop(self):
        logger.info(tr('app.entities.module.stop-start').format(name=self.name))

        for key in self._services.list_keys():
            for name in self._services.get_names(key):
                instance = self._services.get(key, name)
                invoke_sync(instance.stop)
                logger.info(tr('app.entities.module.service-stopped').format(name=name))

        for module in reversed(self._modules.values()):
            module.stop()

        for key in self._controllers.list_keys():
            for name in self._controllers.get_names(key):
                instance = self._controllers.get(key, name)
                invoke_sync(instance.stop)
                logger.info(tr('app.entities.module.ctrl-stopped').format(name=name))

        logger.info(tr('app.entities.module.stop-finish').format(name=self.name))
