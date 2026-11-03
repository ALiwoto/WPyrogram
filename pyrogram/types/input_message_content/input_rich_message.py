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

from pyrogram import raw
from ..object import Object


class InputRichMessage(Object):
    """Rich content to send. Supply exactly one of html, markdown, or blocks.

    HTML and Markdown are parsed by Telegram. Use files to associate their
    tg://photo?id= or tg://document?id= references with InputRichFile objects.
    Structured blocks use raw PageBlock/RichText objects and the photos,
    documents, and users input-reference lists.
    """

    def __init__(
        self,
        *,
        html: Optional[str] = None,
        markdown: Optional[str] = None,
        blocks: Optional[List["raw.base.PageBlock"]] = None,
        files: Optional[List["raw.base.InputRichFile"]] = None,
        photos: Optional[List["raw.base.InputPhoto"]] = None,
        documents: Optional[List["raw.base.InputDocument"]] = None,
        users: Optional[List["raw.base.InputUser"]] = None,
        is_rtl: bool = False,
        disable_auto_link: bool = False,
    ):
        super().__init__()
        if sum(value is not None for value in (html, markdown, blocks)) != 1:
            raise ValueError("Supply exactly one of html, markdown, or blocks")
        if blocks is not None and files is not None:
            raise ValueError("Use photos and documents with blocks, not files")
        if blocks is None and any(value is not None for value in (photos, documents, users)):
            raise ValueError("photos, documents, and users require blocks")

        self.html = html
        self.markdown = markdown
        self.blocks = blocks
        self.files = files
        self.photos = photos
        self.documents = documents
        self.users = users
        self.is_rtl = is_rtl
        self.disable_auto_link = disable_auto_link

    def write(self) -> "raw.base.InputRichMessage":
        if self.html is not None:
            return raw.types.InputRichMessageHTML(
                html=self.html,
                files=self.files,
                rtl=self.is_rtl,
                noautolink=self.disable_auto_link,
            )
        if self.markdown is not None:
            return raw.types.InputRichMessageMarkdown(
                markdown=self.markdown,
                files=self.files,
                rtl=self.is_rtl,
                noautolink=self.disable_auto_link,
            )
        return raw.types.InputRichMessage(
            blocks=self.blocks,
            photos=self.photos,
            documents=self.documents,
            users=self.users,
            rtl=self.is_rtl,
            noautolink=self.disable_auto_link,
        )
