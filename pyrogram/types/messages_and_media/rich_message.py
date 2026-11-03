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

from typing import List, Optional

from pyrogram import raw, types
from ..object import Object


class RichMessage(Object):
    """Received rich content, preserving raw blocks and their media objects."""

    def __init__(
        self,
        *,
        blocks: List["raw.base.PageBlock"],
        photos: List["raw.base.Photo"],
        documents: List["raw.base.Document"],
        users: Optional[List["raw.base.InputUser"]] = None,
        is_rtl: bool = False,
        is_partial: bool = False,
    ):
        super().__init__()
        self.blocks = blocks
        self.photos = photos
        self.documents = documents
        self.users = users
        self.is_rtl = is_rtl
        self.is_partial = is_partial

    @staticmethod
    def _parse(message: "raw.types.RichMessage", users: dict) -> "RichMessage":
        return RichMessage(
            blocks=message.blocks,
            photos=message.photos,
            documents=message.documents,
            users=[
                raw.types.InputUser(user_id=user.id, access_hash=user.access_hash)
                for user in users.values()
                if isinstance(user, raw.types.User) and user.access_hash is not None
            ],
            is_rtl=message.rtl,
            is_partial=message.part,
        )

    def to_input(self) -> "types.InputRichMessage":
        """Reuse this message's blocks and uploaded media in another message."""
        return types.InputRichMessage(
            blocks=self.blocks,
            photos=[
                raw.types.InputPhoto(
                    id=photo.id,
                    access_hash=photo.access_hash,
                    file_reference=photo.file_reference,
                )
                for photo in self.photos
                if isinstance(photo, raw.types.Photo)
            ],
            documents=[
                raw.types.InputDocument(
                    id=document.id,
                    access_hash=document.access_hash,
                    file_reference=document.file_reference,
                )
                for document in self.documents
                if isinstance(document, raw.types.Document)
            ],
            is_rtl=self.is_rtl,
            users=self.users,
        )
