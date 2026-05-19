<<<<<<< HEAD
from os import getenv

dotenv_config = {
    "access_token_expire_minutes": int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)),
    "secret_key": getenv("SECRET_KEY", "fallback_secret"),
    "algorithm": getenv("ALGORITHM", "HS256"),
}
=======
from os import getenv

from dotenv import load_dotenv

load_dotenv()

dotenv_config = {
    "database_url": getenv("DATABASE_URL"),
    "access_token_expire_minutes": int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)),
    "secret_key": getenv("SECRET_KEY", "fallback_secret"),
    "algorithm": getenv("ALGORITHM", "HS256"),
}
>>>>>>> 8b9766d (remove sensitive files)
