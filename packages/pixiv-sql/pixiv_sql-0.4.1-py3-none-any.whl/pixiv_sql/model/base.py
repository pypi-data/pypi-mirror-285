from datetime import datetime
from sqlalchemy import Column, Integer, DateTime

from pixiv_sql.lib.sql import Base


class BaseModel(Base):
    """
    Base Model
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, nullable=False)
