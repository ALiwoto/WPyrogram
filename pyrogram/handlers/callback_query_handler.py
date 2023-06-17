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

from pyrogram.utils import PyromodConfig
from pyrogram.types import ListenerTypes

from .handler import Handler


class CallbackQueryHandler(Handler):
    """The CallbackQuery handler class. Used to handle callback queries coming from inline buttons.
    It is intended to be used with :meth:`~pyrogram.Client.add_handler`

    For a nicer way to register this handler, have a look at the
    :meth:`~pyrogram.Client.on_callback_query` decorator.

    Parameters:
        callback (``Callable``):
            Pass a function that will be called when a new CallbackQuery arrives. It takes *(client, callback_query)*
            as positional arguments (look at the section below for a detailed description).

        filters (:obj:`Filters`):
            Pass one or more filters to allow only a subset of callback queries to be passed
            in your callback function.

    Other parameters:
        client (:obj:`~pyrogram.Client`):
            The Client itself, useful when you want to call other API methods inside the message handler.

        callback_query (:obj:`~pyrogram.types.CallbackQuery`):
            The received callback query.
    """

    def __init__(self, callback: Callable, filters=None):
        self.registered_handler = callback
        super().__init__(callback, filters)

    async def check(self, client, query):
        listener = client.match_listener(
            (query.message.chat.id, query.from_user.id, query.message.id),
            ListenerTypes.CALLBACK_QUERY,
        )[0]

        # managing unallowed user clicks
        if PyromodConfig.unallowed_click_alert:
            permissive_listener = client.match_listener(
                identifier_pattern=(
                    query.message.chat.id,
                    None,
                    query.message.id,
                ),
                listener_type=ListenerTypes.CALLBACK_QUERY,
            )[0]

            if (permissive_listener and not listener) and permissive_listener[
                "unallowed_click_alert"
            ]:
                alert = (
                    permissive_listener["unallowed_click_alert"]
                    if type(permissive_listener["unallowed_click_alert"])
                    == str
                    else PyromodConfig.unallowed_click_alert_text
                )
                await query.answer(alert)
                return False

        filters = listener["filters"] if listener else self.filters

        return await filters(client, query) if callable(filters) else True

    async def resolve_future(self, client, query, *args):
        listener_type = ListenerTypes.CALLBACK_QUERY
        listener, identifier = client.match_listener(
            (query.message.chat.id, query.from_user.id, query.message.id),
            listener_type,
        )

        if listener and not listener["future"].done():
            listener["future"].set_result(query)
            del client.listeners[listener_type][identifier]
        else:
            await self.registered_handler(client, query, *args)
