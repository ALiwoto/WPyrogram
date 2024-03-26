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

import logging
from typing import Union, List

import pyrogram
from pyrogram import raw
from pyrogram import types
from pyrogram import utils

log = logging.getLogger(__name__)


class GetMessageByLink:
    async def get_message_by_link(
        self: 'pyrogram.Client',
        link: str,
        continue_til_found: bool = False,
        chunk_amount: int = 10,
    ) -> types.Message:
        """Gets a single message from a certain link. 
        If necessary, continues message iteration till it finds a valid link.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            link (``str``):
                The message link.

        Returns:
            :obj:`~pyrogram.types.Message`: a single message is returned.

        Example:
            .. code-block:: python

                # Get message via a link
                await app.get_message_by_link(chat_id)

        Raises:
            ValueError: In case of invalid arguments.
        """
        link = link.replace('telegram.me', 't.me')
        link = link.replace('telegram.dog', 't.me')
        link = link.replace('https://', '')
        link = link.replace('http://', '')
        if link.find('t.me') == -1:
            return None

        chat_id = None
        message_id: int = 0
        # the format can be either like t.me/c/1627169341/1099 or
        # t.me/username/123
        if link.find('/c/') != -1:
            my_strs = link.split('/c/')
            if len(my_strs) < 2:
                return None
            my_strs = my_strs[1].split('/')
            if len(my_strs) < 2:
                return None
            chat_id = utils.get_channel_id(int(my_strs[0]))
            message_id = int(my_strs[1])
        else:
            my_strs = link.split('/')
            if len(my_strs) < 3:
                return None
            chat_id = my_strs[1]
            message_id = int(my_strs[2])

        if not chat_id:
            return None

        if not continue_til_found:
            return await self.get_messages(chat_id, message_id)

        messages = await self.get_history(
            chat_id=chat_id,
            limit=1,
        )
        if messages:
            to_id = messages[0].id

        while message_id <= to_id:
            the_messages: List[types.Message] = \
                await self.get_messages(chat_id, [i for i in range(message_id, message_id + chunk_amount)])
            for msg in the_messages:
                if msg and not msg.empty:
                    return msg

            message_id += chunk_amount

        return None

    async def get_scheduled_messages(
        self: "pyrogram.Client",
        chat_id: Union[int, str]
    ) -> List["types.Message"]:
        
        r = await self.invoke(
            raw.functions.GetScheduledHistory(peer=await self.resolve_peer(chat_id), hash=0)
        )

        return await utils.parse_messages(self, r, replies=0)
