from typing import List, Callable
from fastapi import Depends
from tortoise.contrib.pydantic import PydanticModel
from fastapi_pagination import Params
from fastapi_pagination.ext.tortoise import paginate

from ._base import CrudGenerator
from ._type import BaseApiOut


class ModelCrud(CrudGenerator):
    @classmethod
    async def pre_create(cls, item: PydanticModel) -> dict:
        return item.model_dump(exclude_unset=True)

    @classmethod
    async def pre_create_all(cls, items: List[PydanticModel]):
        for item in items:
            yield await cls.pre_create(item)

    @classmethod
    async def pre_update(cls, item: PydanticModel, item_id: str) -> dict:
        return item.model_dump(exclude_unset=True)

    @classmethod
    async def pre_list(cls, item: PydanticModel) -> dict:
        """
        数据预处理：搜索字段
        :param item:
        :return:
        """
        data = {}
        for k, v in item.model_dump(exclude_unset=True).items():
            # 如果v有值或者为bool类型
            if v or isinstance(v, bool):
                # 如果v为字符串并且有值，则使用模糊搜索
                if isinstance(v, str):
                    data[f'{k}__icontains'] = v
                # 否则使用精确搜索
                else:
                    data[k] = v
        return data

    def route_list(self) -> Callable:
        schema_filters = self.schema_filters

        async def route(filters: schema_filters, params: Params = Depends(), order_by: str = '-create_time'):
            filter_item = await self.pre_list(filters)
            queryset = self.model.filter(**filter_item)
            if order_by:
                queryset = queryset.order_by(*order_by.split(','))
            data = await paginate(queryset, params, True)
            return BaseApiOut(data=data)

        return route

    def route_read(self) -> Callable:
        async def route(item_id):
            data = await self.model.find_one(id=item_id)
            data = await self.schema_read.from_tortoise_orm(data)
            return BaseApiOut(data=data)

        return route

    def route_create(self) -> Callable:
        schema_create = self.schema_create

        async def route(item: schema_create):
            item = await self.pre_create(item)
            await self.model.create_one(item)
            return BaseApiOut()

        return route

    def route_create_all(self) -> Callable:
        schema_create = self.schema_create

        async def route(items: List[schema_create]):
            await self.model.bulk_create([self.model(**item) async for item in self.pre_create_all(items)],
                                         ignore_conflicts=False)
            return BaseApiOut(message='批量创建成功')

        return route

    def route_update(self) -> Callable:
        schema_update = self.schema_update

        async def route(item_id: str, item: schema_update):
            item = await self.pre_update(item, item_id=item_id)
            data = await self.model.update_one(item_id, item)
            return BaseApiOut(data=data)

        return route

    def route_delete(self) -> Callable:
        async def route(item_ids: str):
            ids = item_ids.split(',')
            data = await self.model.delete_many(ids)
            return BaseApiOut(data=data)

        return route

    def route_delete_all(self) -> Callable:
        async def route():
            await self.model.all().delete()
            return BaseApiOut(message='删除所有数据成功')

        return route


__all__ = [
    'ModelCrud'
]
