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
from typing import Union

from pyrogram import Client, Message

from .. import glovar
from .etc import crypt_str, get_forward_name, get_full_name, get_now, thread
from .channel import ask_for_help, declare_message, forward_evidence, send_debug, share_bad_user
from .channel import share_watch_user, update_score
from .file import save
from .group import delete_message
from .filters import is_class_d, is_declared_message, is_detected_user, is_high_score_user, is_regex_text, is_watch_user
from .ids import init_user_id
from .telegram import kick_chat_member

# Enable logging
logger = logging.getLogger(__name__)


def add_bad_user(client: Client, uid: int) -> bool:
    # Add a bad user, share it
    try:
        if uid not in glovar.bad_ids["users"]:
            glovar.bad_ids["users"].add(uid)
            save("bad_ids")
            share_bad_user(client, uid)

        return True
    except Exception as e:
        logger.warning(f"Add bad user error: {e}", exc_info=True)

    return False


def add_detected_user(gid: int, uid: int) -> bool:
    # Add or update a detected user's status
    try:
        init_user_id(uid)
        now = get_now()
        previous = glovar.user_ids[uid]["detected"].get(gid)
        glovar.user_ids[uid]["detected"][gid] = now

        return bool(previous)
    except Exception as e:
        logger.warning(f"Add detected user error: {e}", exc_info=True)

    return False


def add_watch_user(client: Client, the_type: str, uid: int) -> bool:
    # Add a watch ban user, share it
    try:
        now = get_now()
        until = now + glovar.time_ban
        glovar.watch_ids[the_type][uid] = until
        until = str(until)
        until = crypt_str("encrypt", until, glovar.key)
        share_watch_user(client, the_type, uid, until)
        save("watch_ids")

        return True
    except Exception as e:
        logger.warning(f"Add watch user error: {e}", exc_info=True)

    return False


def ban_user(client: Client, gid: int, uid: Union[int, str]) -> bool:
    # Ban a user
    try:
        thread(kick_chat_member, (client, gid, uid))

        return True
    except Exception as e:
        logger.warning(f"Ban user error: {e}", exc_info=True)

    return False


def terminate_user(client: Client, message: Message, context: str) -> bool:
    # Delete user's message, or ban the user
    try:
        if is_class_d(None, message) or is_declared_message(None, message):
            return True

        gid = message.chat.id
        uid = message.from_user.id
        mid = message.message_id
        context_list = context.split()
        the_time = context_list[0]
        the_count = context_list[1]

        full_name = get_full_name(message.from_user)
        forward_name = get_forward_name(message)
        if ((is_regex_text("wb", full_name)
             or is_regex_text("wb", forward_name))
                and (full_name not in glovar.except_ids["long"]
                     and forward_name not in glovar.except_ids["long"])):
            result = forward_evidence(client, message, "自动封禁", "名称检查", the_time, the_count)
            if result:
                add_bad_user(client, uid)
                ban_user(client, gid, uid)
                delete_message(client, gid, mid)
                declare_message(client, gid, mid)
                ask_for_help(client, "ban", gid, uid)
                send_debug(client, message.chat, "名称封禁", uid, mid, result)
        elif is_watch_user(message, "ban"):
            result = forward_evidence(client, message, "自动封禁", "敏感追踪", the_time, the_count)
            if result:
                add_bad_user(client, uid)
                ban_user(client, gid, uid)
                delete_message(client, gid, mid)
                declare_message(client, gid, mid)
                ask_for_help(client, "ban", gid, uid)
                send_debug(client, message.chat, "追踪封禁", uid, mid, result)
        elif is_high_score_user(message):
            score = is_high_score_user(message)
            result = forward_evidence(client, message, "自动封禁", "用户评分", the_time, the_count, score)
            if result:
                add_bad_user(client, uid)
                ban_user(client, gid, uid)
                delete_message(client, gid, mid)
                declare_message(client, gid, mid)
                ask_for_help(client, "ban", gid, uid)
                send_debug(client, message.chat, "评分封禁", uid, mid, result)
        elif is_watch_user(message, "delete"):
            result = forward_evidence(client, message, "自动删除", "敏感追踪", the_time, the_count)
            if result:
                add_watch_user(client, "ban", uid)
                delete_message(client, gid, mid)
                declare_message(client, gid, mid)
                ask_for_help(client, "delete", gid, uid, "global")
                previous = add_detected_user(gid, uid)
                if not previous:
                    update_score(client, uid)

                send_debug(client, message.chat, "追踪删除", uid, mid, result)
        elif is_detected_user(message) or uid in glovar.recorded_ids[gid]:
            delete_message(client, gid, mid)
            add_detected_user(gid, uid)
            declare_message(client, gid, mid)
        else:
            result = forward_evidence(client, message, "自动删除", "群组自定义", the_time, the_count)
            if result:
                glovar.recorded_ids[gid].add(uid)
                delete_message(client, gid, mid)
                declare_message(client, gid, mid)
                if glovar.configs[gid].get("delete", True):
                    ask_for_help(client, "delete", gid, uid)

                previous = add_detected_user(gid, uid)
                if not previous:
                    update_score(client, uid)

                send_debug(client, message.chat, "自动删除", uid, mid, result)

        return True
    except Exception as e:
        logger.warning(f"Terminate user error: {e}", exc_info=True)

    return False
