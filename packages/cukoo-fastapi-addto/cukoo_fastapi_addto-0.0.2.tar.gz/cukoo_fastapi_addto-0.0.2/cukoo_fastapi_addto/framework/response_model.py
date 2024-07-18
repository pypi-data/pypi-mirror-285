# -*- encoding: utf-8 -*-
'''
@File    :   response_model.py
@Time    :   2023-08-01 09:00:00
@Author  :   phailin791 
@Version :   1.0
@Contact :   phailin791@hotmail.com
'''

from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    page: int = 1  # type: ignore
    per_page: int = 10  # type: ignore
    total: int = 0  # type: ignore
    page_data: List[T] = []


class RenderBase(BaseModel, Generic[T]):
    code: int = 10200  # first version api code,
    data: T = ""
    message: str = ""


class RenderPage(BaseModel, Generic[T]):
    code: int = 10200  # first version api code,
    data: Page[T] = ""
    message: str = ""