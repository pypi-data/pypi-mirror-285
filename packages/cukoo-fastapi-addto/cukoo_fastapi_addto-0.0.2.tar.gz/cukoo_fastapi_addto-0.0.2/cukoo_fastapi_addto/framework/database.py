# -*- encoding: utf-8 -*-
'''
@File    :   database.py
@Time    :   2023-08-01 09:00:00
@Author  :   phailin791 
@Version :   1.0
@Contact :   phailin791@hotmail.com
'''

from contextlib import contextmanager, AbstractContextManager
from typing import Callable
from loguru import logger

from sqlalchemy import create_engine, orm
from sqlalchemy.orm import declarative_base, Session, Mapped, mapped_column

Base = declarative_base()

class Database:

    def __init__(self, db_url: str) -> None:
        self._engine = create_engine(db_url, echo=False, pool_pre_ping=True, pool_size=100, max_overflow=0)
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def create_database(self) -> None:
        Base.metadata.create_all(self._engine)

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            logger.error("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()
