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

from datetime import datetime
from typing import Optional, List

import pyrogram
from pyrogram import raw
from pyrogram import types
from pyrogram import utils
from ..object import Object


class StarGift(Object):
    """A star gift.

    Parameters:
        id (``int``):
            Unique star gift identifier.

        sticker (:obj:`~pyrogram.types.Sticker`):
            Information about the star gift sticker.

        caption (``str``, *optional*):
            Text message.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            For text messages, special entities like usernames, URLs, bot commands, etc. that appear in the text.

        message_id (``int``, *optional*):
            Unique message identifier.

        date (``datetime``, *optional*):
            Date when the star gift was received.

        first_sale_date (``datetime``, *optional*):
            Date when the star gift was first purchased.

        last_sale_date (``datetime``, *optional*):
            Date when the star gift was last purchased.

        from_user (:obj:`~pyrogram.types.User`, *optional*):
            User who sent the star gift.

        price (``int``, *optional*):
            Price of this gift in stars.

        convert_price (``int``, *optional*):
            The number of stars you get if you convert this gift.

        available_amount (``int``, *optional*):
            The number of gifts available for purchase.
            Returned only if is_limited is True.

        total_amount (``int``, *optional*):
            Total amount of gifts.
            Returned only if is_limited is True.

        is_limited (``bool``, *optional*):
            True, if the number of gifts is limited.

        is_name_hidden (``bool``, *optional*):
            True, if the sender's name is hidden.

        is_saved (``bool``, *optional*):
            True, if the star gift is saved in profile.

        is_sold_out (``bool``, *optional*):
            True, if the star gift is sold out.
    """

    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        id: int,
        sticker: "types.Sticker",
        caption: Optional[str] = None,
        caption_entities: List["types.MessageEntity"] = None,
        message_id: Optional[int] = None,
        date: Optional[datetime] = None,
        first_sale_date: Optional[datetime] = None,
        last_sale_date: Optional[datetime] = None,
        from_user: Optional["types.User"] = None,
        price: Optional[int] = None,
        convert_price: Optional[int] = None,
        available_amount: Optional[int] = None,
        total_amount: Optional[int] = None,
        is_limited: Optional[bool] = None,
        is_name_hidden: Optional[bool] = None,
        is_saved: Optional[bool] = None,
        is_sold_out: Optional[bool] = None
    ):
        super().__init__(client)

        self.id = id
        self.sticker = sticker
        self.caption = caption
        self.caption_entities = caption_entities
        self.message_id = message_id
        self.date = date
        self.first_sale_date = first_sale_date
        self.last_sale_date = last_sale_date
        self.from_user = from_user
        self.price = price
        self.convert_price = convert_price
        self.available_amount = available_amount
        self.total_amount = total_amount
        self.is_limited = is_limited
        self.is_name_hidden = is_name_hidden
        self.is_saved = is_saved
        self.is_sold_out = is_sold_out

    @staticmethod
    async def _parse(
        client,
        star_gift: "raw.types.StarGift",
    ) -> "StarGift":
        doc = star_gift.sticker
        attributes = {type(i): i for i in doc.attributes}

        return StarGift(
            id=star_gift.id,
            sticker=await types.Sticker._parse(client, doc, attributes),
            price=star_gift.stars,
            convert_price=star_gift.convert_stars,
            available_amount=getattr(star_gift, "availability_remains", None),
            total_amount=getattr(star_gift, "availability_total", None),
            is_limited=getattr(star_gift, "limited", None),
            first_sale_date=utils.timestamp_to_datetime(getattr(star_gift, "first_sale_date", None)),
            last_sale_date=utils.timestamp_to_datetime(getattr(star_gift, "last_sale_date", None)),
            is_sold_out=getattr(star_gift, "sold_out", None),
            client=client
        )

    @staticmethod
    async def _parse_user_star_gift(
        client,
        user_star_gift: "raw.types.UserStarGift",
        users: dict
    ) -> "StarGift":
        doc = user_star_gift.gift.sticker
        attributes = {type(i): i for i in doc.attributes}

        caption, caption_entities = (
            utils.parse_text_with_entities(
                client, getattr(user_star_gift, "message", None), users
            )
        ).values()

        return StarGift(
            id=user_star_gift.gift.id,
            sticker=await types.Sticker._parse(client, doc, attributes),
            price=user_star_gift.gift.stars,
            convert_price=user_star_gift.gift.convert_stars,
            available_amount=getattr(user_star_gift.gift, "availability_remains", None),
            total_amount=getattr(user_star_gift.gift, "availability_total", None),
            date=utils.timestamp_to_datetime(user_star_gift.date),
            is_limited=getattr(user_star_gift.gift, "limited", None),
            is_name_hidden=getattr(user_star_gift, "name_hidden", None),
            is_saved=not user_star_gift.unsaved if getattr(user_star_gift, "unsaved", None) else None,
            from_user=types.User._parse(client, users.get(user_star_gift.from_id)) if getattr(user_star_gift, "from_id", None) else None,
            message_id=getattr(user_star_gift, "msg_id", None),
            caption=caption,
            caption_entities=caption_entities,
            client=client
        )

    @staticmethod
    async def _parse_action(
        client,
        message: "raw.base.Message",
        users: dict
    ) -> "StarGift":
        action = message.action

        doc = action.gift.sticker
        attributes = {type(i): i for i in doc.attributes}

        caption, caption_entities = (
            utils.parse_text_with_entities(
                client, getattr(action, "message", None), users
            )
        ).values()

        return StarGift(
            id=action.gift.id,
            sticker=await types.Sticker._parse(client, doc, attributes),
            price=action.gift.stars,
            convert_price=action.gift.convert_stars,
            available_amount=getattr(action.gift, "availability_remains", None),
            total_amount=getattr(action.gift, "availability_total", None),
            date=utils.timestamp_to_datetime(message.date),
            is_limited=getattr(action.gift, "limited", None),
            is_name_hidden=getattr(action, "name_hidden", None),
            is_saved=getattr(action, "saved", None),
            from_user=types.User._parse(client, users.get(utils.get_raw_peer_id(message.peer_id))),
            message_id=message.id,
            caption=caption,
            caption_entities=caption_entities,
            client=client
        )

    async def show(self) -> bool:
        """Bound method *show* of :obj:`~pyrogram.types.StarGift`.

        Use as a shortcut for:

        .. code-block:: python

            await client.show_star_gift(
                chat_id=message.chat.id,
                message_id=message_id
            )

        Example:
            .. code-block:: python

                await star_gift.show()

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self._client.show_star_gift(
            chat_id=self.from_user.id,
            message_id=self.message_id
        )

    async def hide(self) -> bool:
        """Bound method *hide* of :obj:`~pyrogram.types.StarGift`.

        Use as a shortcut for:

        .. code-block:: python

            await client.hide_star_gift(
                chat_id=message.chat.id,
                message_id=message_id
            )

        Example:
            .. code-block:: python

                await star_gift.hide()

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self._client.hide_star_gift(
            chat_id=self.from_user.id,
            message_id=self.message_id
        )
