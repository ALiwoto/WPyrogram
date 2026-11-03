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

from pyrogram import raw, types
from .input_message_content import InputMessageContent


class InputRichMessageContent(InputMessageContent):
    """Rich content to send as an inline query result."""

    def __init__(self, rich_message: "types.InputRichMessage"):
        super().__init__()
        self.rich_message = rich_message

    async def write(self, client, reply_markup):
        return raw.types.InputBotInlineMessageRichMessage(
            rich_message=self.rich_message.write(),
            reply_markup=await reply_markup.write(client) if reply_markup else None,
        )
