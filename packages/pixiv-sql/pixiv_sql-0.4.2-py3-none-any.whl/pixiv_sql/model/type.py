from sqlalchemy import Column, String
from pixiv_sql.model.base import BaseModel


class Type(BaseModel):
    """
    Type Model
    """

    __tablename__ = "types"

    name = Column(String(255), nullable=False)
