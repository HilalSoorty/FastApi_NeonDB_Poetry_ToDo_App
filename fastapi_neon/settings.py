from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
    print("HELLO TESTING CHECKING")
except FileNotFoundError:
    config = Config()
    print("NOT FOUND!!!")

DATABASE_URL = config("DATABASE_URL", cast=Secret)

# TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)