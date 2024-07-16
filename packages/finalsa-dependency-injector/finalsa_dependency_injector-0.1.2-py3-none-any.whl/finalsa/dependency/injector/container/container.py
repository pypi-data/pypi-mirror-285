from finalsa.dependency.injector.exceptions import (
    DependencyNotFoundException, InvalidInterface
)
from typing import (
    Callable, Dict, get_type_hints, Union,
    Optional
)
from .life_cycle import LifeCycle
from abc import ABC
from uuid import UUID


class Container():

    def __init__(
        self,
        get_correlation_id_method: Optional[Callable[[], str]] = None
    ) -> None:
        self.life_cycle_map: Dict[Callable, LifeCycle] = {}
        self.dependency_map = {}
        self.loaded_dependencies = {}
        self.type_hints = {}
        self.scoped_loaded_dependencies = {}
        self.get_correlation_id_method = get_correlation_id_method
        if self.get_correlation_id_method is None:
            self.get_correlation_id_method = self.get_scoped_id_default

    def add_dependency(
            self,
            interface: Union[Callable, ABC],
            implementation: Callable,
            life_cycle: LifeCycle = LifeCycle.SCOPED
    ) -> None:
        if isinstance(interface, ABC):
            res = interface.__subclasshook__(implementation)
            if res is None or not res or res is NotImplemented:
                raise InvalidInterface(interface, implementation)
        self.dependency_map[interface] = implementation
        self.life_cycle_map[interface] = life_cycle

    def add_builded_dependency(self, interface: Callable, implementation) -> None:
        self.add_dependency(interface, implementation, LifeCycle.SINGLETON)
        self.loaded_dependencies[interface] = implementation

    def get(self, interface: Callable) -> Callable:
        if interface not in self.dependency_map:
            self.add_dependency(interface, interface)
        life_cycle = self.life_cycle_map[interface]
        if life_cycle == LifeCycle.TRANSIENT:
            return self.build_dependency(interface)
        elif life_cycle == LifeCycle.SINGLETON:
            return self.get_singleton_dependency(interface)
        elif life_cycle == LifeCycle.SCOPED:
            return self.get_scoped_dependency(interface)

    async def get_async(self, interface: Callable) -> Callable:
        if interface not in self.dependency_map:
            self.add_dependency(interface, interface)
        life_cycle = self.life_cycle_map[interface]
        if life_cycle == LifeCycle.TRANSIENT:
            return await self.async_build_dependency(interface)
        elif life_cycle == LifeCycle.SINGLETON:
            return self.get_singleton_dependency(interface)
        elif life_cycle == LifeCycle.SCOPED:
            return await self.async_get_scoped_dependency(interface)

    def get_singleton_dependency(self, interface: Callable) -> Callable:
        if interface not in self.loaded_dependencies:
            self.loaded_dependencies[interface] = self.build_dependency(interface)
        return self.loaded_dependencies[interface]

    def set_scope(self, correlation_id_value: Union[str, UUID]):
        if isinstance(correlation_id_value, UUID):
            correlation_id_value = str(correlation_id_value)
        self.scoped_loaded_dependencies[correlation_id_value] = {}

    def delete_scope(self, correlation_id_value):
        del self.scoped_loaded_dependencies[correlation_id_value]

    @staticmethod
    def get_scoped_id_default() -> str:
        return "default"

    async def async_get_scoped_dependency(self, interface: Callable) -> Callable:
        correlation_id_value = self.get_correlation_id_method()
        if correlation_id_value not in self.scoped_loaded_dependencies:
            return await self.async_build_dependency(interface)
        if interface not in self.scoped_loaded_dependencies[correlation_id_value]:
            self.scoped_loaded_dependencies[correlation_id_value][interface] = await self.async_build_dependency(
                interface)
        return self.scoped_loaded_dependencies[correlation_id_value][interface]

    def get_scoped_dependency(self, interface: Callable) -> Callable:
        correlation_id_value = self.get_correlation_id_method()
        if correlation_id_value not in self.scoped_loaded_dependencies:
            return self.build_dependency(
                interface)
        if interface not in self.scoped_loaded_dependencies[correlation_id_value]:
            self.scoped_loaded_dependencies[correlation_id_value][interface] = self.build_dependency(
                interface)
        return self.scoped_loaded_dependencies[correlation_id_value][interface]

    async def async_build_dependency(self, interface: Callable) -> Callable:
        impl = self.dependency_map[interface]
        self_dependency_map = get_type_hints(impl.__init__)
        attrs: Dict[str, Callable] = {}
        for attr_name in self_dependency_map:
            if attr_name == "return":
                continue
            dependency = self_dependency_map[attr_name]
            attrs[attr_name] = await self.get_async(dependency)
        try:
            implementation = impl(**attrs)
            if hasattr(implementation, "__anext__"):
                return await anext(implementation)
            return implementation
        except Exception as ex:
            raise DependencyNotFoundException(interface, attrs) from ex

    def build_dependency(self, interface: Callable) -> Callable:
        impl = self.dependency_map[interface]
        self_dependency_map = get_type_hints(impl.__init__)
        attrs: Dict[str, Callable] = {}
        for attr_name in self_dependency_map:
            if attr_name == "return":
                continue
            dependency = self_dependency_map[attr_name]
            attrs[attr_name] = self.get(dependency)
        try:
            return impl(**attrs)
        except Exception as ex:
            raise DependencyNotFoundException(interface, attrs) from ex

    def get_type_hints(self, interface: Callable) -> Dict[str, Callable]:
        if interface not in self.type_hints:
            self.type_hints[interface] = get_type_hints(interface.__init__)
        return self.type_hints[interface]
