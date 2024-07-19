from abc import ABC, abstractmethod
from typing import Union, Any, List, Callable, Type

from fastapi import APIRouter
from fastapi.types import DecoratedCallable
from fastapi_pagination import Page
from tortoise.contrib.pydantic import PydanticModel

from .model import BaseModel
from ._type import BaseApiOut, DEPENDENCIES


class CrudGenerator(APIRouter, ABC):
    def __init__(self, model: Union[BaseModel, Any],
                 schema_create: Union[bool, Type[PydanticModel]] = True,
                 schema_list: Union[bool, Type[PydanticModel]] = True,
                 schema_read: Union[bool, Type[PydanticModel]] = True,
                 schema_update: Union[bool, Type[PydanticModel]] = True,
                 schema_delete: Union[bool, Type[PydanticModel]] = True,
                 schema_filters: Union[bool, Type[PydanticModel]] = True,
                 dependencies: DEPENDENCIES = None,
                 depends_read: Union[bool, DEPENDENCIES] = True,
                 depends_create: Union[bool, DEPENDENCIES] = True,
                 depends_update: Union[bool, DEPENDENCIES] = True,
                 depends_delete: Union[bool, DEPENDENCIES] = True,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

        self.dependencies = dependencies or []
        self.schema_read = schema_read or model.schema_read()
        self.schema_list = schema_list or self.schema_read
        self.schema_update = schema_update or model.schema_update()
        self.schema_create = schema_create or model.schema_create()
        self.schema_delete = schema_delete or model.schema_delete()
        self.schema_filters = schema_filters or model.schema_filters()
        model_name = model.__name__.lower()
        if schema_read:
            self._add_api_route(
                '/read/{item_id}',
                self.route_read(),
                methods=['GET'],
                response_model=BaseApiOut[self.schema_read],
                name=f'{model_name}Read',
                summary=f'{model_name} Read',
                dependencies=depends_read
            )
        if schema_list:
            self._add_api_route(
                '/list',
                self.route_list(),
                methods=['POST'],
                response_model=BaseApiOut[Page[self.schema_list]],
                name=f'{model_name}Read',
                summary=f'{model_name} List',
                dependencies=depends_read
            )
        if self.schema_create:
            self._add_api_route(
                '/create',
                self.route_create(),
                methods=['POST'],
                response_model=BaseApiOut,
                name=f'{model_name}Create',
                summary=f'{model_name} Create',
                dependencies=depends_create
            )

            self._add_api_route(
                '/create/all',
                self.route_create_all(),
                methods=['POST'],
                response_model=BaseApiOut,
                name=f'{model_name}Create',
                summary=f'{model_name} CreateAll',
                dependencies=depends_create
            )
        if self.schema_update:
            self._add_api_route(
                '/{item_id}',
                self.route_update(),
                methods=['PUT'],
                response_model=BaseApiOut,
                name=f'{model_name}Update',
                summary=f'{model_name} Update',
                dependencies=depends_update
            )
        if self.schema_delete:
            self._add_api_route(
                '/{item_ids}',
                self.route_delete(),
                methods=['DELETE'],
                response_model=BaseApiOut,
                description='删除1条或多条数据example：1,2',
                name=f'{model_name}Delete',
                summary=f'{model_name} Delete',
                dependencies=depends_delete
            )
            self._add_api_route(
                '/delete/all',
                self.route_delete_all(),
                methods=['DELETE'],
                response_model=BaseApiOut,
                description='删除所有数据',
                name=f'{model_name}Delete',
                summary=f'{model_name}DeleteAll',
                dependencies=depends_delete
            )

    def _add_api_route(
            self,
            path: str,
            endpoint: Callable[..., Any],
            dependencies: Union[bool, DEPENDENCIES],
            **kwargs: Any,
    ) -> None:
        # 先处理None情况，因为None既不是True也不是False
        if dependencies is None:
            dependencies = []
        # 明确检查dependencies是否为bool类型，并根据其值决定使用self.dependencies还是空列表
        elif isinstance(dependencies, bool):
            dependencies = self.dependencies if dependencies else []
        super().add_api_route(path, endpoint, dependencies=dependencies, **kwargs)

    def api_route(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """Overrides and exiting route if it exists"""
        methods = kwargs["methods"] if "methods" in kwargs else ["GET"]
        self.remove_api_route(path, methods)
        return super().api_route(path, *args, **kwargs)

    def get(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["Get"])
        return super().get(path, *args, **kwargs)

    def post(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["POST"])
        return super().post(path, *args, **kwargs)

    def put(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["PUT"])
        return super().put(path, *args, **kwargs)

    def delete(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["DELETE"])
        return super().delete(path, *args, **kwargs)

    def remove_api_route(self, path: str, methods: List[str]) -> None:
        methods_ = set(methods)

        for route in self.routes:
            if (
                    route.path == f"{self.prefix}{path}"  # type: ignore
                    and route.methods == methods_  # type: ignore
            ):
                self.routes.remove(route)

    @abstractmethod
    def route_list(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def route_read(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def route_update(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def route_create(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def route_create_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def route_delete(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def route_delete_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError


__all__ = [
    'CrudGenerator'
]
