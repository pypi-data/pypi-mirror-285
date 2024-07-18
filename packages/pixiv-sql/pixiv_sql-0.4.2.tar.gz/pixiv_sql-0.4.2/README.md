# pixiv-sql

[![PyPI version](https://badge.fury.io/py/pixiv-sql.svg)](https://badge.fury.io/py/pixiv-sql)
![build](https://github.com/ryohidaka/pixiv-sql/workflows/Build/badge.svg)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Python library to backup pixiv user data to SQLite DB.

## Installation

You can install this library using PyPI:

```shell
pip install pixiv-sql
```

## Usage

### Create dataBase file

```bash
touch db/my_pixiv.db
```

### Get `refresh_token`

> To get `refresh_token`, see
> [@ZipFile Pixiv OAuth Flow](https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362)
> or
> [OAuth with Selenium/ChromeDriver](https://gist.github.com/upbit/6edda27cb1644e94183291109b8a5fde)

### Initialize the PixivSQL class with your Pixiv user ID, refresh token, and database:

```python
user_id = "your_user_id"
refresh_token = "your_refresh_token"
database = "db/my_pixiv.db"

app = PixivSQL(user_id, refresh_token, database)
```

### You can then fetch your bookmarked illusts and insert them into the database:

```python
app.bookmarked_illusts()
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
