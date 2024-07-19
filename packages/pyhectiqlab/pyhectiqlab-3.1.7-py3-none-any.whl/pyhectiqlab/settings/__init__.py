import os
import logging
from typing import Any, Optional
from dotenv import load_dotenv


def load_env(override: bool = False):
    """Load environment variables from .env files. This function loads the public
    environment variables from a `.env.public` file and then loads specific
    environment variables from a `.env.{ENV}` file where `{ENV}` is the value of the
    `ENV` environment variable.

    Args:
        override (bool): Whether to override existing environment variables.
            Default: False.
    """
    # Load comments from .env file
    env_path = os.path.join(os.path.dirname(__file__), ".env.public")
    if not env_path:
        assert False, f"🚫 api/app/settings: Could not find .env.public file"
    else:
        logging.info(f"✅ Loading secrets at {env_path}")
        load_dotenv(env_path, override=override)

    # Load specific environment variables from .env.{ENV} file
    ENV = os.getenv("ENV", "local")
    env_path = os.path.join(os.path.dirname(__file__), f".env.{ENV}")
    if not env_path:
        logging.info(f"🚫 api/app/settings:::.env.{ENV} file")
    else:
        logging.info(f"✅ Loading secrets at {env_path}")
        load_dotenv(env_path, override=override)


def getenv(key: str, default: Optional[Any] = None) -> Any:
    """Get environment variable or return explicit default. This function overrides
    the behavior of os.getenv() to return a boolean or None if the value is set to
    "True", "False", or "None" respectively.

    Args:
        key (str): The environment variable key.
        default (Any, optional): The default value to return if the key is not found.
            Defaults to None.

    Returns:
        Any: The environment variable value or the default value.
    """
    value = os.getenv(key, default)
    if value == "True":
        return True
    elif value == "False":
        return False
    elif value == "None":
        return None
    return value
