# -*- encoding: utf-8 -*-
'''
@File    :   __init__.py
@Time    :   2023-08-01 09:00:00
@Author  :   phailin791 
@Version :   1.0
@Contact :   phailin791@hotmail.com
'''

from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_serializer

class BaseSchemas(BaseModel):
    id: Optional[int] = Field(None, description="id")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    comment: Optional[str] = Field(None, max_length=128, description="备注")

    @field_serializer("created_at")
    def serialize_created_at(self, created_at: datetime, _info):
        v = None
        if created_at and isinstance(created_at, datetime):
            v = created_at.strftime("%Y-%m-%d %H:%M:%S")
        return v

    @field_serializer("updated_at")
    def serialize_updated_at(self, updated_at: datetime, _info):
        v = None
        if updated_at and isinstance(updated_at, datetime):
            v = updated_at.strftime("%Y-%m-%d %H:%M:%S")
        return v

    class Config:
        from_attributes = True