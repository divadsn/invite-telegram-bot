import os
import sys
import logging

# enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# if version < 3.7, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 7:
    logger.error("You MUST have a python version of at least 3.7! Multiple features depend on this. Bot quitting.")
    quit(1)

BOT_TOKEN = os.getenv("BOT_TOKEN", None)

try:
    OWNER_ID = int(os.environ.get("OWNER_ID", "101110325"))
except ValueError:
    raise Exception("Your OWNER_ID env variable is not a valid integer.")

try:
    MAX_INVITES_PER_USER = int(os.environ.get("MAX_INVITES_PER_USER", "3"))
except ValueError:
    raise Exception("Your MAX_INVITES_PER_USER env variable is not a valid integer.")

try:
    EXPIRY_HOURS = int(os.environ.get("EXPIRY_HOURS", "24"))
except ValueError:
    raise Exception("Your EXPIRY_HOURS env variable is not a valid integer.")

DB_URI = os.getenv("DATABASE_URL", "sqlite:///invitebot.sqlite3")
