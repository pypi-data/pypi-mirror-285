from datetime import datetime
import hashlib
import json
from typing import Literal

from pixiv_sql.model import Image, Tag


def generate_unique_index(name) -> int:
    """
    Generate a unique index for a given name using SHA-256 hashing.

    Parameters:
    name (str): The name for which to generate a unique index.

    Returns:
    int: The unique index generated from the name.
    """
    return int(hashlib.sha256(name.encode("utf-8")).hexdigest(), 16) % 10**8


def get_restrict(self, is_private: bool) -> Literal["private", "public"]:
    """
    This method determines the restriction level based on the is_private parameter.

    Parameters:
    is_private (bool): A boolean value that indicates whether the restriction is private.

    Returns:
    str: Returns 'private' if is_private is True, otherwise returns 'public'.
    """

    # Initialize the logger
    logger = self.logger

    # Determine the restriction level
    restrict = "private" if is_private else "public"

    # Log the restriction level
    logger.info(f"Restrict: {restrict}")

    # Return the restriction level
    return restrict


def is_ignore_file(filename: str) -> bool:
    ignore_list = ["limit_unknown_360.png", "limit_sanity_level_360.png"]
    return filename in ignore_list


def get_filename(url: str) -> str:
    """
    Function to get the filename from a URL.

    Args:
        url (str): URL.

    Returns:
        str: Filename.
    """
    return url.split("/")[-1]


def collect_user_records(illusts):
    users = []
    for illust in illusts:
        try:
            user = illust["user"]

            # Skip user where name is empty
            if not user.get("name"):
                continue

            # Get is_followed or default to None if not present
            is_followed = user.get("is_followed")

            filename = get_filename(user["profile_image_urls"]["medium"])
            profile_image_urls = (
                user["profile_image_urls"]["medium"]
                if filename != "no_profile.png"
                else None
            )

            users.append(
                {
                    "id": user["id"],
                    "name": user["name"],
                    "account": user["account"],
                    "is_followed": is_followed,
                    "profile_image_urls": profile_image_urls,
                }
            )
        except KeyError as e:
            print(f"Issue with user record: {e}")
            print(json.dumps(user, indent=4, ensure_ascii=False))
            continue  # Continue to the next illust if there's an issue with the current one
    return users


def collect_bookmarked_illust_records(illusts, is_private):
    records = []
    for illust in illusts:
        try:
            # Skip illusts where visible is 0
            if illust.get("visible", 1) == 0:
                continue

            user_id = illust["user"]["id"]
            records.append(
                {
                    "id": illust["id"],
                    "title": illust["title"],
                    "caption": illust["caption"],
                    "user_id": user_id,
                    "create_date": datetime.strptime(
                        illust["create_date"], "%Y-%m-%dT%H:%M:%S%z"
                    ),
                    "page_count": illust["page_count"],
                    "visible": illust["visible"],
                    "illust_ai_type": illust["illust_ai_type"],
                    "illust_book_style": illust["illust_book_style"],
                    "is_private": is_private,
                }
            )
        except KeyError as e:
            print(f"Issue with illusts record: {e}")
            print(json.dumps(illusts, indent=4, ensure_ascii=False))
            continue  # Continue to the next illust if there's an issue with the current one
    return records


def collect_tag_records(illusts):
    tags = {}
    illust_tags = []
    for illust in illusts:
        try:
            for tag in illust["tags"]:
                tag_id = generate_unique_index(tag["name"])
                tags[tag_id] = {
                    "id": tag_id,
                    "name": tag["name"],
                    "translated_name": tag.get("translated_name"),
                }
                illust_tags.append(
                    {
                        "illust_id": illust["id"],
                        "tag_id": tag_id,
                        "is_registered": tag.get("is_registered"),
                    }
                )
        except KeyError as e:
            print(f"Issue with tag record: {e}")
            print(json.dumps(illust["tags"], indent=4, ensure_ascii=False))
            continue  # Continue to the next illust if there's an issue with the current one
    return tags.values(), illust_tags


def collect_image_records(illusts, session):
    images = []
    for illust in illusts:
        try:
            # Skip illusts where visible is 0
            if illust.get("visible", 1) == 0:
                continue

            if illust["meta_pages"]:
                for index, page in enumerate(illust["meta_pages"]):
                    original_image_url = page["image_urls"]["original"]
                    if not is_ignore_file(get_filename(original_image_url)):
                        filename = get_filename(original_image_url)

                        image = (
                            session.query(Image)
                            .filter(Image.filename == filename)
                            .all()
                        )

                        if not image:
                            images.append(
                                {
                                    "illust_id": illust["id"],
                                    "page": index,
                                    "is_multiple_page": True,
                                    "filename": get_filename(original_image_url),
                                    "url": original_image_url,
                                    "is_square": False,
                                }
                            )

                        square_medium_image_url = page["image_urls"]["square_medium"]

                        filename = get_filename(square_medium_image_url)

                        image = (
                            session.query(Image)
                            .filter(Image.filename == filename)
                            .all()
                        )

                        if not image:
                            images.append(
                                {
                                    "illust_id": illust["id"],
                                    "page": index,
                                    "is_multiple_page": True,
                                    "filename": get_filename(square_medium_image_url),
                                    "url": square_medium_image_url,
                                    "is_square": True,
                                }
                            )

            else:
                original_image_url = illust["meta_single_page"]["original_image_url"]
                filename = get_filename(original_image_url)

                image = session.query(Image).filter(Image.filename == filename).all()

                if not is_ignore_file(filename) and not image:
                    images.append(
                        {
                            "illust_id": illust["id"],
                            "page": 0,
                            "is_multiple_page": False,
                            "filename": get_filename(original_image_url),
                            "url": original_image_url,
                            "is_square": False,
                        }
                    )

                square_medium_image_url = illust["image_urls"]["square_medium"]
                filename = get_filename(square_medium_image_url)

                image = session.query(Image).filter(Image.filename == filename).all()

                if not image:
                    images.append(
                        {
                            "illust_id": illust["id"],
                            "page": 0,
                            "is_multiple_page": False,
                            "filename": get_filename(square_medium_image_url),
                            "url": square_medium_image_url,
                            "is_square": True,
                        }
                    )

        except KeyError as e:
            print(f"Issue with image record: {e}")
            print(json.dumps(illust, indent=4, ensure_ascii=False))
            continue  # Continue to the next illust if there's an issue with the current one
    return images


def collect_registered_tag_records(illusts, session):
    tags = {}
    illust_tags = []
    for illust in illusts:
        try:
            for tag in illust["tags"]:
                tag_id = generate_unique_index(tag["name"])

                if not session.query(Tag).filter(Tag.id == tag_id).all():
                    tags[tag_id] = {
                        "id": tag_id,
                        "name": tag["name"],
                        "translated_name": tag.get("translated_name"),
                    }

                illust_tags.append(
                    {"illust_id": illust["id"], "tag_id": tag_id, "is_registered": True}
                )
        except KeyError as e:
            print(f"Issue with tag record: {e}")
            print(json.dumps(illust["tags"], indent=4, ensure_ascii=False))
            continue  # Continue to the next illust if there's an issue with the current one
    return tags.values(), illust_tags


def collect_user_following_records(following_users):
    users = []

    for following_user in following_users[:1]:
        try:
            user = following_user.user

            # Skip user where name is empty
            if not user.get("name"):
                continue

            # Get is_followed or default to None if not present
            is_followed = user.get("is_followed")

            filename = get_filename(user["profile_image_urls"]["medium"])
            profile_image_urls = (
                user["profile_image_urls"]["medium"]
                if filename != "no_profile.png"
                else None
            )

            # Set last_create_date to None if "illusts" does not exist
            last_create_date = (
                user.get("illusts", [{}])[0].get("create_date")
                if user.get("illusts")
                else None
            )

            users.append(
                {
                    "id": user["id"],
                    "name": user["name"],
                    "account": user["account"],
                    "is_followed": is_followed,
                    "profile_image_urls": profile_image_urls,
                    "last_create_date": last_create_date,
                }
            )
        except KeyError as e:
            print(f"Issue with user record: {e}")
            print(json.dumps(user, indent=4, ensure_ascii=False))
            continue  # Continue to the next user if there's an issue with the current one
    return users
