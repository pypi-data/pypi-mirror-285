import os
from dotenv import load_dotenv
from tqdm import tqdm
from pixiv_sql.lib.logger import init_logger
from pixiv_sql.lib.pixiv import (
    collect_bookmarked_illust_records,
    collect_image_records,
    collect_registered_tag_records,
    collect_tag_records,
    collect_user_following_records,
    collect_user_records,
    get_restrict,
)
from pixiv_sql.lib.pixivpy import (
    get_bookmarked_illusts,
    get_illusts_registered_tags,
    get_user_following,
    init_api,
)
from pixiv_sql.lib.sql import (
    create_tables,
    get_engine,
    get_random_records,
    get_session,
    upsert,
)
from pixiv_sql.model.bookmarked_illust import BookmarkedIllust
from pixiv_sql.model.illust_tag import IllustTag
from pixiv_sql.model.image import Image
from pixiv_sql.model.tag import Tag
from pixiv_sql.model.type import Type
from pixiv_sql.model.user import User


# Load .env file and reflect environment variables.
load_dotenv()


def main() -> int:
    print("Hello from pixiv-sql!")

    user_id = os.environ.get("USER_ID")
    refresh_token = os.environ.get("REFRESH_TOKEN")
    database = os.environ.get("DB")

    app = PixivSQL(user_id, refresh_token, database)

    app.bookmarked_illusts()

    random_ids = app.get_random_illust_ids()
    app.registered_tags(illust_ids=random_ids)

    app.user_following()

    return 0


class PixivSQL:
    def __init__(self, user_id: str, refresh_token: str, database: str):
        """
        The constructor for the PixivSQL class.

        Parameters:
            user_id (str): The user ID for the Pixiv account.
            refresh_token (str): The refresh token for the Pixiv API.
        """

        self.logger = init_logger()

        # Set the user ID, refresh token and database.
        self.user_id = user_id
        self.refresh_token = refresh_token
        self.database = database

        self.logger.info(f"UserID: {self.user_id}")

        # Initialize the API.
        self.api = init_api(self)

        # Create Engine
        self.engine = get_engine(database)

        # Create Session
        self.session = get_session(self.engine)

        # Create Tables
        create_tables(self.engine)

    def bookmarked_illusts(self, is_private: bool = False):
        """
        The bookmarked_illusts method for the PixivSQL class.

        This method fetches the bookmarked illusts of the user and inserts them into the database.
        It also creates the necessary tables if they do not exist.

        Parameters:
            is_private (bool): A flag to indicate if the bookmarked illusts are private. Default is False.
        """

        # Get the restrict level based on the is_private flag.
        self.restrict = get_restrict(self, is_private)
        self.is_private = is_private

        # Fetch the bookmarked illusts from the Pixiv API.
        illusts = get_bookmarked_illusts(self)

        # Insert the types of illusts into the database.
        types = ["illust", "manga", "ugoira"]
        for index, type_name in enumerate(types):
            upsert(self.session, Type, id=index + 1, name=type_name)

        # Insert the fetched users into the database.
        users = collect_user_records(illusts)
        for user in tqdm(users, desc="Users"):
            upsert(self.session, User, **user)

        # Insert the fetched bookmarked illusts into the database.
        bookmarked_illusts = collect_bookmarked_illust_records(illusts, is_private)
        for illust in tqdm(bookmarked_illusts, desc="Bookmarked Illusts"):
            upsert(self.session, BookmarkedIllust, **illust)

        # Insert the fetched tags into the database.
        tags, illust_tags = collect_tag_records(illusts)
        for tag in tqdm(tags, desc="Tags"):
            upsert(self.session, Tag, **tag)

        # Insert the fetched illusts_tags pare into the database.
        for illust_tag in tqdm(illust_tags, desc="Illust Tags"):
            upsert(self.session, IllustTag, id=None, **illust_tag)

        # Insert the fetched images into the database.
        images = collect_image_records(illusts, self.session)
        for image in tqdm(images, desc="Images"):
            upsert(self.session, Image, id=None, **image)

    def registered_tags(self, illust_ids: list[int]):
        """
        The registered_tags method for the PixivSQL class.

        This method fetches the registered tags of the given illust ids and inserts them into the database.

        Parameters:
            illust_ids (list[int]): List of target illustration id.
        """
        illusts_registered_tags = get_illusts_registered_tags(self, illust_ids)

        tags, illust_tags = collect_registered_tag_records(
            illusts_registered_tags, self.session
        )

        # Insert the fetched tags into the database.
        for tag in tqdm(tags, desc="Tags"):
            upsert(self.session, Tag, **tag)

        # Insert the fetched illusts_tags pare into the database.
        for illust_tag in tqdm(illust_tags, desc="Illust Tags"):
            upsert(self.session, IllustTag, True, **illust_tag)

    def get_random_illust_ids(self, limit=10):
        """
        The get_random_illust_ids method for the PixivSQL class.

        This method gets random illust records.

        Parameters:
            limit (int): Number of records to retrieve.
        """
        random_illusts = get_random_records(self.session, BookmarkedIllust, limit)

        # Get list of ids
        random_ids = [record.id for record in random_illusts]

        return random_ids

    def user_following(self, is_private: bool = False):
        """
        The user_following method for the PixivSQL class.

        This method fetches the following users of the user and inserts them into the database.
        It also creates the necessary tables if they do not exist.

        Parameters:
            is_private (bool): A flag to indicate if the following users are private. Default is False.
        """
        # Get the restrict level based on the is_private flag.
        self.restrict = get_restrict(self, is_private)
        self.is_private = is_private

        following_users = get_user_following(self)
        following_users = collect_user_following_records(following_users)

        # Insert the fetched user_following into the database.
        for user in tqdm(following_users, desc="User Following"):
            upsert(self.session, User, **user)
