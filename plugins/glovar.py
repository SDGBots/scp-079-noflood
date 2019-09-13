# SCP-079-NOFLOOD - Message-flooding prevention
# Copyright (C) 2019 SCP-079 <https://scp-079.org>
#
# This file is part of SCP-079-NOFLOOD.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import pickle
from configparser import RawConfigParser
from os import mkdir
from os.path import exists
from shutil import rmtree
from threading import Lock
from typing import Dict, List, Set, Union

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING,
    filename='log',
    filemode='w'
)
logger = logging.getLogger(__name__)

# Init

all_commands: List[str] = ["config", "config_noflood", "version"]

declared_message_ids: Dict[int, Set[int]] = {}
# declared_message_ids = {
#     -10012345678: {123}
# }

default_config: Dict[str, Union[bool, int]] = {
    "default": True,
    "lock": 0,
    "limit": 5,
    "time": 10
}

default_user_status: Dict[str, Dict[Union[int, str], Union[float, int]]] = {
    "detected": {},
    "score": {
        "captcha": 0.0,
        "clean": 0.0,
        "lang": 0.0,
        "long": 0.0,
        "noflood": 0.0,
        "noporn": 0.0,
        "nospam": 0.0,
        "recheck": 0.0,
        "warn": 0.0
    }
}

flood_ids: Dict[int, List[int]] = {}
# flood_ids = {
#     12345678: [1512345678]
# }

left_group_ids: Set[int] = set()

locks: Dict[str, Lock] = {
    "admin": Lock(),
    "message": Lock(),
    "regex": Lock(),
    "test": Lock()
}

receivers: Dict[str, List[str]] = {
    "bad": ["ANALYZE", "APPLY", "APPEAL", "AVATAR", "CAPTCHA", "CLEAN", "LANG", "LONG",
            "MANAGE", "NOFLOOD", "NOPORN", "NOSPAM", "RECHECK", "TIP", "USER", "WATCH"],
    "declare": ["ANALYZE", "AVATAR", "CLEAN", "LANG", "LONG",
                "NOFLOOD", "NOPORN", "NOSPAM", "RECHECK", "USER", "WATCH"],
    "score": ["ANALYZE", "CAPTCHA", "CLEAN", "LANG", "LONG",
              "MANAGE", "NOFLOOD", "NOPORN", "NOSPAM", "RECHECK"],
    "watch": ["ANALYZE", "CAPTCHA", "CLEAN", "LANG", "LONG",
              "MANAGE", "NOFLOOD", "NOPORN", "NOSPAM", "RECHECK", "WATCH"]
}

recorded_ids: Dict[int, Set[int]] = {}
# recorded_ids = {
#     -10012345678: {12345678}
# }

regex: Dict[str, bool] = {
    "wb": True
}

sender: str = "NOFLOOD"

should_hide: bool = False

version: str = "0.0.1"

# Read data from config.ini

# [basic]
bot_token: str = ""
prefix: List[str] = []
prefix_str: str = "/!"

# [bots]
avatar_id: int = 0
captcha_id: int = 0
clean_id: int = 0
lang_id: int = 0
long_id: int = 0
noflood_id: int = 0
noporn_id: int = 0
nospam_id: int = 0
recheck_id: int = 0
tip_id: int = 0
user_id: int = 0
warn_id: int = 0

# [channels]
critical_channel_id: int = 0
debug_channel_id: int = 0
exchange_channel_id: int = 0
hide_channel_id: int = 0
logging_channel_id: int = 0
test_group_id: int = 0

# [custom]
default_group_link: str = ""
project_link: str = ""
project_name: str = ""
punish_time: int = 0
reset_day: str = ""
time_ban: int = 0

# [encrypt]
key: Union[str, bytes] = ""
password: str = ""

try:
    config = RawConfigParser()
    config.read("config.ini")
    # [basic]
    bot_token = config["basic"].get("bot_token", bot_token)
    prefix = list(config["basic"].get("prefix", prefix_str))
    # [bots]
    avatar_id = int(config["bots"].get("avatar_id", avatar_id))
    captcha_id = int(config["bots"].get("captcha_id", captcha_id))
    clean_id = int(config["bots"].get("clean_id", clean_id))
    lang_id = int(config["bots"].get("lang_id", lang_id))
    long_id = int(config["bots"].get("long_id", long_id))
    noflood_id = int(config["bots"].get("noflood_id", noflood_id))
    noporn_id = int(config["bots"].get("noporn_id", noporn_id))
    nospam_id = int(config["bots"].get("nospam_id", nospam_id))
    recheck_id = int(config["bots"].get("recheck_id", recheck_id))
    tip_id = int(config["bots"].get("tip_id", tip_id))
    user_id = int(config["bots"].get("user_id", user_id))
    warn_id = int(config["bots"].get("warn_id", warn_id))
    # [channels]
    critical_channel_id = int(config["channels"].get("critical_channel_id", critical_channel_id))
    debug_channel_id = int(config["channels"].get("debug_channel_id", debug_channel_id))
    exchange_channel_id = int(config["channels"].get("exchange_channel_id", exchange_channel_id))
    hide_channel_id = int(config["channels"].get("hide_channel_id", hide_channel_id))
    logging_channel_id = int(config["channels"].get("logging_channel_id", logging_channel_id))
    test_group_id = int(config["channels"].get("test_group_id", test_group_id))
    # [custom]
    default_group_link = config["custom"].get("default_group_link", default_group_link)
    project_link = config["custom"].get("project_link", project_link)
    project_name = config["custom"].get("project_name", project_name)
    punish_time = int(config["custom"].get("punish_time", punish_time))
    reset_day = config["custom"].get("reset_day", reset_day)
    time_ban = int(config["custom"].get("time_ban", time_ban))
    # [encrypt]
    key = config["encrypt"].get("key", key)
    key = key.encode("utf-8")
    password = config["encrypt"].get("password", password)
except Exception as e:
    logger.warning(f"Read data from config.ini error: {e}", exc_info=True)

# Check
if (bot_token in {"", "[DATA EXPUNGED]"}
        or prefix == []
        or avatar_id == 0
        or captcha_id == 0
        or clean_id == 0
        or lang_id == 0
        or long_id == 0
        or noflood_id == 0
        or noporn_id == 0
        or nospam_id == 0
        or recheck_id == 0
        or tip_id == 0
        or user_id == 0
        or warn_id == 0
        or critical_channel_id == 0
        or debug_channel_id == 0
        or exchange_channel_id == 0
        or hide_channel_id == 0
        or logging_channel_id == 0
        or test_group_id == 0
        or default_group_link in {"", "[DATA EXPUNGED]"}
        or project_link in {"", "[DATA EXPUNGED]"}
        or project_name in {"", "[DATA EXPUNGED]"}
        or punish_time == 0
        or reset_day in {"", "[DATA EXPUNGED]"}
        or time_ban == 0
        or key in {b"", b"[DATA EXPUNGED]"}
        or password in {"", "[DATA EXPUNGED]"}):
    logger.critical("No proper settings")
    raise SystemExit("No proper settings")

bot_ids: Set[int] = {avatar_id, captcha_id, clean_id, lang_id, long_id,
                     noflood_id, noporn_id, nospam_id, recheck_id, tip_id, user_id, warn_id}

# Load data from pickle

# Init dir
try:
    rmtree("tmp")
except Exception as e:
    logger.info(f"Remove tmp error: {e}")

for path in ["data", "tmp"]:
    if not exists(path):
        mkdir(path)

# Init ids variables

admin_ids: Dict[int, Set[int]] = {}
# admin_ids = {
#     -10012345678: {12345678}
# }

bad_ids: Dict[str, Set[int]] = {
    "users": set()
}
# bad_ids = {
#     "users": {12345678}
# }

except_ids: Dict[str, Set[str]] = {
    "long": set()
}
# except_ids = {
#     "long": {"content"}
# }

user_ids: Dict[int, Dict[str, Dict[Union[int, str], Union[float, int]]]] = {}
# user_ids = {
#     12345678: {
#         "detected": {
#               -10012345678: 1512345678
#         },
#         "score": {
#             "captcha": 0.0,
#             "clean": 0.0,
#             "lang": 0.0,
#             "long": 0.0,
#             "noflood": 0.0,
#             "noporn": 0.0,
#             "nospam": 0.0,
#             "recheck": 0.0,
#             "warn": 0.0
#         }
#     }
# }

watch_ids: Dict[str, Dict[int, int]] = {
    "ban": {},
    "delete": {}
}
# watch_ids = {
#     "ban": {
#         12345678: 0
#     },
#     "delete": {
#         12345678: 0
#     }
# }

# Init data variables

configs: Dict[int, Dict[str, Union[bool, int]]] = {}
# configs = {
#     -10012345678: {
#         "default": True,
#         "lock": 0,
#         "limit": 0,
#         "time": 0
#     }
# }

# Init word variables

for word_type in regex:
    locals()[f"{word_type}_words"]: Dict[str, Dict[str, Union[float, int]]] = {}

# type_words = {
#     "regex": 0
# }

# Load data
file_list: List[str] = ["admin_ids", "bad_ids", "except_ids", "user_ids", "watch_ids", "configs"]
file_list += [f"{f}_words" for f in regex]
for file in file_list:
    try:
        try:
            if exists(f"data/{file}") or exists(f"data/.{file}"):
                with open(f"data/{file}", "rb") as f:
                    locals()[f"{file}"] = pickle.load(f)
            else:
                with open(f"data/{file}", "wb") as f:
                    pickle.dump(eval(f"{file}"), f)
        except Exception as e:
            logger.error(f"Load data {file} error: {e}", exc_info=True)
            with open(f"data/.{file}", "rb") as f:
                locals()[f"{file}"] = pickle.load(f)
    except Exception as e:
        logger.critical(f"Load data {file} backup error: {e}", exc_info=True)
        raise SystemExit("[DATA CORRUPTION]")

# Start program
copyright_text = (f"SCP-079-{sender} v{version}, Copyright (C) 2019 SCP-079 <https://scp-079.org>\n"
                  "Licensed under the terms of the GNU General Public License v3 or later (GPLv3+)\n")
print(copyright_text)
