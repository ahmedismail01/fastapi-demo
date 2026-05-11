from os import getenv

dotenv_config = {
    "access_token_expire_minutes": int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)),
    "secret_key": getenv("SECRET_KEY", "fallback_secret"),
    "algorithm": getenv("ALGORITHM", "HS256"),
}