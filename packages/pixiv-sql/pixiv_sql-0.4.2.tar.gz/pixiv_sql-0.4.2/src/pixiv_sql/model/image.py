from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from pixiv_sql.model.base import BaseModel


class Image(BaseModel):
    """
    Image Model
    """

    __tablename__ = "images"

    illust_id = Column(Integer, ForeignKey("bookmarked_illusts.id"))
    page = Column(Integer, nullable=False)
    is_multiple_page = Column(Boolean, nullable=False)
    filename = Column(String(255), unique=True)
    url = Column(String(255), unique=True)
    is_square = Column(Boolean, nullable=False)
