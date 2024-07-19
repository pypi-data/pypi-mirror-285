from abc import ABC, abstractmethod

from fastapi_pydentity.infrastructure.types import TService, TImplementation, DependencyCallable


class IServiceCollection(dict[type, DependencyCallable[TImplementation]], ABC):

    @abstractmethod
    def add_service(self, service_type: type[TService], factory: DependencyCallable[TImplementation]):
        ...

    @abstractmethod
    def get(self, service_type: type[TService]):
        ...

    @abstractmethod
    def get_all(self):
        ...
