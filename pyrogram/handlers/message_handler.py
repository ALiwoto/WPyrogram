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

from typing import Callable
import pyrogram

from pyrogram.types import ListenerTypes

from .handler import Handler


class MessageHandler(Handler):
    """The Message handler class. Used to handle new messages.
    It is intended to be used with :meth:`~pyrogram.Client.add_handler`

    For a nicer way to register this handler, have a look at the
    :meth:`~pyrogram.Client.on_message` decorator.

    Parameters:
        callback (``Callable``):
            Pass a function that will be called when a new Message arrives. It takes *(client, message)*
            as positional arguments (look at the section below for a detailed description).

        filters (:obj:`Filters`):
            Pass one or more filters to allow only a subset of messages to be passed
            in your callback function.

    Other parameters:
        client (:obj:`~pyrogram.Client`):
            The Client itself, useful when you want to call other API methods inside the message handler.

        message (:obj:`~pyrogram.types.Message`):
            The received message.
    """

    def __init__(self, callback: Callable, filters=None):
        self.registered_handler = callback
        super().__init__(callback, filters)

    async def check(self, client, message):
        listener = client.match_listener(
            (message.chat.id, message.from_user.id, message.id),
            ListenerTypes.MESSAGE,
        )[0]

        listener_does_match = handler_does_match = False

        if listener:
            filters = listener["filters"]
            listener_does_match = (
                await filters(client, message) if callable(filters) else True
            )
        handler_does_match = (
            await self.filters(client, message)
            if callable(self.filters)
            else True
        )

        # let handler get the chance to handle if listener
        # exists but its filters doesn't match
        return listener_does_match or handler_does_match

    async def resolve_future(self, client, message, *args):
        listener_type = ListenerTypes.MESSAGE
        listener, identifier = client.match_listener(
            (message.chat.id, message.from_user.id, message.id),
            listener_type,
        )
        listener_does_match = False
        if listener:
            filters = listener["filters"]
            listener_does_match = (
                await filters(client, message) if callable(filters) else True
            )

        if listener_does_match:
            if not listener["future"].done():
                listener["future"].set_result(message)
                del client.listeners[listener_type][identifier]
                raise pyrogram.StopPropagation
        else:
            await self.registered_handler(client, message, *args)
