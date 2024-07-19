from typing import Generic, TypeVar, Optional, Sequence

from fastapi import Depends
from pydantic import BaseModel

_T = TypeVar('_T')
DEPENDENCIES = Optional[Sequence[Depends]]


class BaseApiOut(BaseModel, Generic[_T]):
    message: str = '请求成功'
    data: Optional[_T] = None
    code: int = 200


__all__ = [
    'BaseApiOut',
    'DEPENDENCIES'
]
