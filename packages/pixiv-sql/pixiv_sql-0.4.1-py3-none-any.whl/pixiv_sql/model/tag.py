from sqlalchemy import Column, String
from pixiv_sql.model.base import BaseModel


class Tag(BaseModel):
    """
    Tag Model
    """

    __tablename__ = "tags"

    name = Column(String(255), nullable=False)
    translated_name = Column(String(255))
