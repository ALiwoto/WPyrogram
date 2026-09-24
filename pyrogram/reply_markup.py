# pyright: strict

from __future__ import annotations

import re
from typing import Dict, List, Optional, Union

import pyrogram
from pyrogram import raw, types


InlineButtons = Union[Dict[str, str], List[Dict[str, str]]]
ReplyMarkup = Union[
    "types.InlineKeyboardMarkup",
    "types.ReplyKeyboardMarkup",
    "types.ReplyKeyboardRemove",
    "types.ForceReply",
    InlineButtons,
]


def parse_inline_buttons(buttons: InlineButtons) -> List[List[types.InlineKeyboardButton]]:
    url_pattern = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"

    def make_button(title: str, value: str) -> "types.InlineKeyboardButton":
        is_web_app = value.startswith("app::")
        if is_web_app:
            value = value[len("app::") :]
        if re.search(url_pattern, value):
            if is_web_app:
                return types.InlineKeyboardButton(
                    text=str(title), web_app=types.WebAppInfo(url=value)
                )
            return types.InlineKeyboardButton(text=str(title), url=value)
        return types.InlineKeyboardButton(text=str(title), callback_data=value)

    rows: List[List[types.InlineKeyboardButton]] = []
    if isinstance(buttons, dict):
        for title, value in buttons.items():
            title = str(title)
            same_row = title.startswith("same::")
            if not same_row or not rows:
                rows.append([])
            if same_row:
                title = title[len("same::") :]
            rows[-1].append(make_button(title, value))
    else:
        for row in buttons:
            if row:
                rows.append([make_button(title, value) for title, value in row.items()])

    return rows


async def write_reply_markup(
    client: "pyrogram.Client", reply_markup: Optional[ReplyMarkup], *, for_send: bool = False
) -> Optional["raw.base.ReplyMarkup"]:
    if not reply_markup:
        return None
    if isinstance(reply_markup, (dict, list)):
        reply_markup = types.InlineKeyboardMarkup.from_buttons(reply_markup)
    if (
        for_send
        and isinstance(reply_markup, types.InlineKeyboardMarkup)
        and client.helper_bot is not None
        and client.me is not None
        and not client.me.is_bot
    ):
        client = client.helper_bot
    return await reply_markup.write(client)
