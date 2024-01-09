#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from typing import Union

import pyrogram
from pyrogram import raw


class ReadMentions:
    async def read_mentions(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        topic_id: int = None
    ) -> bool:
        """Mark a mention in the chat as read.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            topic_id (``int``, *optional*):
                Mark as read only mentions to messages within the specified forum topic.
                By default, no topic is applied and all mentions marked as read.

        Returns:
            ``bool`` - On success, True is returned.

        Example:
            .. code-block:: python

                # Mark the chat mention as read
                await app.read_mentions(chat_id)

                # Mark the chat mention as read in specified topic
                await app.read_mentions(chat_id, topic_id)
        """
        r = await self.invoke(
            raw.functions.messages.ReadMentions(
                peer=await self.resolve_peer(chat_id),
                top_msg_id=topic_id
            )
        )

        return bool(r)
