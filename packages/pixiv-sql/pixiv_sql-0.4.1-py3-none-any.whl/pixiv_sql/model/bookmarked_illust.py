from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from pixiv_sql.model.base import BaseModel


class BookmarkedIllust(BaseModel):
    """
    Bookmarked Illust Model
    """

    __tablename__ = "bookmarked_illusts"

    title = Column(String(255), nullable=False)
    type_id = Column(Integer, ForeignKey("types.id"))
    caption = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    create_date = Column(DateTime, nullable=False)
    page_count = Column(Integer, nullable=False)
    visible = Column(Boolean, nullable=False)
    illust_ai_type = Column(Integer, nullable=False)
    illust_book_style = Column(Integer, nullable=False)
    is_private = Column(Boolean, nullable=False)
