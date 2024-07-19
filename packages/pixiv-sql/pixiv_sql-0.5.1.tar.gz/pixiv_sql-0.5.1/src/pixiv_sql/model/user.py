from sqlalchemy import Boolean, Column, DateTime, String
from pixiv_sql.model.base import BaseModel


class User(BaseModel):
    """
    User Model
    """

    __tablename__ = "users"

    name = Column(String(255), nullable=False)
    account = Column(String(255), nullable=False)
    is_followed = Column(Boolean)
    profile_image_urls = Column(String(255))
    last_create_date = Column(DateTime, default=None)
