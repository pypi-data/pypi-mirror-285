# -*- encoding: utf-8 -*-
'''
@Time    :   2023-08-01 09:00:00
@Author  :   phailin791 
@Version :   1.0
@Contact :   phailin791@hotmail.com
'''

from typing import Optional
from datetime import datetime
from sqlalchemy import String
from sqlalchemy.orm import (declared_attr, declarative_mixin, Mapped, mapped_column)

from cukoo_fastapi_addto.framework.database import Base

@declarative_mixin
class ModelMixin:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {'mysql_engine': 'InnoDB'}
    __mapper_args__= {'always_refresh': True}

    id: Mapped[int] = mapped_column(primary_key=True, sort_order=-1, comment="id", doc="id")
    created_by: Mapped[Optional[int]] = mapped_column(comment="创建人", doc="创建人")
    created_at: Mapped[Optional[datetime]] = mapped_column(comment="创建时间", doc="创建时间")
    updated_by: Mapped[Optional[int]] = mapped_column(comment="更新人", doc="更新人")
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.now, comment="更新时间", doc="更新时间")
    comment: Mapped[Optional[str]] = mapped_column(String(64), comment="备注", doc="备注")
    vsn: Mapped[Optional[int]] = mapped_column(default=0, comment="版本号", doc="版本号")
    deleted: Mapped[Optional[bool]] = mapped_column(default=False, comment="逻辑删除:False=>未删除,True=>已删除", doc="逻辑删除")