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


class SendPaidReaction:
    async def send_paid_reaction(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        amount: int,
        is_private: bool = None
    ) -> bool:
        """Send a paid reaction to a message.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the message.

            amount (``int``):
                Amount of stars to send.

            is_private (``bool``, *optional*):
                Pass True to hide you from top reactors.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Send paid reaction with 1 star
                await app.send_paid_reaction(chat_id, message_id, amount=1)
        """
        rpc = raw.functions.messages.SendPaidReaction(
            peer=await self.resolve_peer(chat_id),
            msg_id=message_id,
            count=amount,
            random_id=self.rnd_id(),
            private=is_private
        )

        await self.invoke(rpc)

        return True
