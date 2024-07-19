import time
from pixivpy3 import AppPixivAPI
from tqdm import tqdm


def init_api(self) -> AppPixivAPI:
    """
    Initialize the API.

    Returns:
        AppPixivAPI: The API client.
    """

    api = AppPixivAPI()
    api.auth(refresh_token=self.refresh_token)
    time.sleep(2)

    return api


def get_bookmarked_illusts(self):
    """
    This function retrieves a list of bookmarked illusts for a user.
    It fetches bookmarks in a loop until there are no more bookmarks to fetch.
    If an error occurs during the fetching process, it logs the error but continues fetching.
    """

    self.logger.info("[Start] Getting bookmarked illust list")

    # Define a list to store illusts.
    illusts = []

    # Get a list of bookmarked illusts.
    res = fetch_bookmarked_illusts(self)

    while res:
        try:
            # Extract the illustrations from the response.
            illusts += res.illusts
            next_url = res.next_url

        except Exception as e:
            self.logger.error("Failed to get the bookmark:", str(e))
            res = None  # Set res to None to handle in the next step

        # If there is a next URL, parse it and fetch the next set of bookmarked illusts.
        if res and next_url:
            try:
                next_qs = self.api.parse_qs(res.next_url)
                self.logger.info(f"Next: {next_qs}")
                res = fetch_bookmarked_illusts(self, **next_qs)
            except Exception as e:
                self.logger.error("Failed to fetch next bookmarked illusts:", str(e))
                res = None  # Proceed to the next loop iteration
        else:
            break

    self.logger.info("[End] Getting bookmarked illust list")

    return illusts


def fetch_bookmarked_illusts(self, **kwargs):
    """
    This function fetches bookmarked illusts for a given user ID.
    It makes a call to the Pixiv API and returns the response.
    If an error occurs during the API call, it logs the error and returns None.
    """

    try:
        # Remove 'user_id' from kwargs if it exists
        kwargs.pop("user_id", None)

        # Remove 'restrict' from kwargs if it exists
        kwargs.pop("restrict", None)

        res = self.api.user_bookmarks_illust(
            user_id=self.user_id, restrict=self.restrict, **kwargs
        )
        time.sleep(5)
        return res
    except Exception as e:
        self.logger.error("Failed to fetch bookmarked illusts:", str(e))
        return None


def get_illusts_registered_tags(self, illust_ids: list[int]):
    """
    This function retrieves a list of registered tags a given illust IDs.
    If an error occurs during the fetching process, it logs the error but continues fetching.
    """
    self.logger.info("[Start] Getting bookmarked illust detail list")

    # Define a list to store illusts.
    illusts_registered_tags = []

    for id in tqdm(illust_ids, desc="Registered Tags"):
        try:
            registered_tags = fetch_registered_tags(self, id)
            illusts_registered_tags.append(
                {
                    "id": id,
                    "tags": registered_tags,
                }
            )
        except Exception as e:
            self.logger.error("Failed to get the bookmark detail:", str(e))
            return None

    self.logger.info("[End] Getting bookmarked illust detail list")

    return illusts_registered_tags


def fetch_registered_tags(self, id: int):
    """
    This function fetches registered tags for a given illust ID.
    It makes a call to the Pixiv API and returns the response.
    If an error occurs during the API call, it logs the error and returns None.
    """

    try:
        res = self.api.illust_bookmark_detail(id)
        time.sleep(3)

        # Get bookmark tag list
        bookmark_tags = res["bookmark_detail"]["tags"]

        # Get registered tags in an array
        registered_tags = [item for item in bookmark_tags if item["is_registered"]]

        return registered_tags
    except Exception as e:
        self.logger.error("Failed to fetch bookmarked illust detail:", str(e))
        return None


def get_user_following(self):
    """
    This function retrieves a list of following users for a user.
    It fetches user_following in a loop until there are no more user to fetch.
    If an error occurs during the fetching process, it logs the error but continues fetching.
    """

    self.logger.info("[Start] Getting user_following list")

    # Define a list to store following users.
    users = []

    # Get a list of user_following.
    res = fetch_user_following(self)

    while res:
        try:
            # Extract the illustrations from the response.
            users += res.user_previews
            next_url = res.next_url

        except Exception as e:
            self.logger.error("Failed to get user_following:", str(e))
            res = None  # Set res to None to handle in the next step

        # If there is a next URL, parse it and fetch the next set of user_following.
        if res and next_url:
            try:
                next_qs = self.api.parse_qs(res.next_url)
                self.logger.info(f"Next: {next_qs}")
                res = fetch_user_following(self, **next_qs)
            except Exception as e:
                self.logger.error("Failed to fetch next user_following:", str(e))
                res = None  # Proceed to the next loop iteration
        else:
            break

    self.logger.info("[End] Getting user_following list")

    return users


def fetch_user_following(self, **kwargs):
    """
    This function fetches user_following for a given user ID.
    It makes a call to the Pixiv API and returns the response.
    If an error occurs during the API call, it logs the error and returns None.
    """

    try:
        # Remove 'user_id' from kwargs if it exists
        kwargs.pop("user_id", None)

        # Remove 'restrict' from kwargs if it exists
        kwargs.pop("restrict", None)

        res = self.api.user_following(
            user_id=self.user_id, restrict=self.restrict, **kwargs
        )
        time.sleep(5)
        return res
    except Exception as e:
        self.logger.error("Failed to fetch user_following:", str(e))
        return None
