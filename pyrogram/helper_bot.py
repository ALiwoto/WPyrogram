# pyright: strict

from __future__ import annotations

import logging
from copy import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, TypedDict, Union, cast
from uuid import uuid4

from pyrogram import enums, raw, types, utils

if TYPE_CHECKING:
    from pyrogram import Client


log = logging.getLogger(__name__)


SendRequest = Union[raw.functions.messages.SendMessage, raw.functions.messages.SendMedia]


class InvokeOptions(TypedDict):
    retries: int
    timeout: float
    sleep_threshold: Optional[float]


@dataclass
class HelperBotQuery:
    user_id: int
    result: raw.base.InputBotInlineResult
    error: Optional[Exception] = None


async def answer_helper_bot_query(client: Client, update: raw.base.Update) -> bool:
    if not isinstance(update, raw.types.UpdateBotInlineQuery):
        return False

    pending = client._helper_bot_queries.get(update.query)  # pyright: ignore[reportPrivateUsage]
    if pending is None or pending.user_id != update.user_id:
        return False

    try:
        await client.invoke(
            raw.functions.messages.SetInlineBotResults(
                query_id=update.query_id, results=[pending.result], cache_time=0, private=True
            )
        )
    except Exception as error:
        pending.error = error
        log.exception("Failed to answer a helper bot query")

    return True


async def send_with_helper_bot(
    client: Client,
    query: SendRequest,
    retries: int,
    timeout: float,
    sleep_threshold: Optional[float],
) -> raw.base.Updates:
    helper = client.helper_bot
    if helper is None or not helper.is_connected or helper.me is None or not helper.me.is_bot:
        raise ValueError("helper_bot must be a started bot Client")
    if helper.no_updates or not helper.me.username:
        raise ValueError("helper_bot needs a username and incoming updates enabled")

    # Fail explicitly when the inline API cannot preserve a send option.
    content_fields = {"message", "entities", "reply_markup", "no_webpage", "invert_media", "media"}
    send_fields = {
        "peer",
        "random_id",
        "silent",
        "background",
        "clear_draft",
        "reply_to",
        "schedule_date",
        "send_as",
        "quick_reply_shortcut",
        "allow_paid_stars",
    }
    for name in query.__slots__:
        if name not in send_fields and name not in content_fields:
            if getattr(query, name) not in (None, False):
                raise ValueError(f"The helper bot inline API does not support {name}")

    invoke_options: InvokeOptions = {
        "retries": retries,
        "timeout": timeout,
        "sleep_threshold": sleep_threshold,
    }
    result = await build_inline_result(client, helper, query, invoke_options)
    if result is None:
        # The staging send was not confirmed. Do not send or retry the destination message.
        return raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0)

    token = "wpy_helper_" + uuid4().hex
    pending = HelperBotQuery(cast(types.User, client.me).id, result)
    helper._helper_bot_queries[token] = pending  # pyright: ignore[reportPrivateUsage]
    try:
        results = cast(
            raw.types.messages.BotResults,
            await client.invoke(
                raw.functions.messages.GetInlineBotResults(
                    bot=cast(raw.base.InputUser, await client.resolve_peer(helper.me.username)),
                    peer=query.peer,
                    query=token,
                    offset="",
                ),
                **invoke_options,
            ),
        )
    except Exception:
        if pending.error is not None:
            raise pending.error
        raise
    finally:
        helper._helper_bot_queries.pop(token, None)  # pyright: ignore[reportPrivateUsage]

    if not any(item.id == result.id for item in results.results):
        raise ValueError("The helper bot returned no matching inline result")

    # Reuse the caller's random_id, including across transport and flood-wait retries.
    return cast(
        raw.base.Updates,
        await client.invoke(
            raw.functions.messages.SendInlineBotResult(
                peer=query.peer,
                random_id=query.random_id,
                query_id=results.query_id,
                id=result.id,
                silent=query.silent,
                background=query.background,
                clear_draft=query.clear_draft,
                reply_to=query.reply_to,
                schedule_date=query.schedule_date,
                send_as=query.send_as,
                quick_reply_shortcut=query.quick_reply_shortcut,
                allow_paid_stars=query.allow_paid_stars,
            ),
            **invoke_options,
        ),
    )


async def build_inline_result(
    client: Client, helper: Client, query: SendRequest, invoke_options: InvokeOptions
) -> Optional[raw.base.InputBotInlineResult]:
    entities: List[raw.base.MessageEntity] = []
    for entity in query.entities or []:
        if isinstance(entity, raw.types.InputMessageEntityMentionName):
            entity = copy(entity)
            if isinstance(entity.user_id, raw.types.InputUserEmpty):
                raise ValueError("A helper bot mention requires a user ID")
            user_id = (
                cast(types.User, client.me).id
                if isinstance(entity.user_id, raw.types.InputUserSelf)
                else entity.user_id.user_id
            )
            entity.user_id = cast(raw.base.InputUser, await helper.resolve_peer(user_id))
        entities.append(entity)

    if isinstance(query, raw.functions.messages.SendMessage):
        return raw.types.InputBotInlineResult(
            id="message",
            type="article",
            title="Message",
            send_message=raw.types.InputBotInlineMessageText(
                no_webpage=query.no_webpage,
                message=query.message,
                entities=entities or None,
                reply_markup=query.reply_markup,
                invert_media=query.invert_media,
            ),
        )

    media = query.media
    inline_message: Optional[raw.base.InputBotInlineMessage] = None
    result_type = "article"
    if isinstance(media, (raw.types.InputMediaGeoPoint, raw.types.InputMediaGeoLive)):
        if isinstance(media, raw.types.InputMediaGeoLive) and media.stopped:
            raise ValueError("The helper bot cannot send a stopped live location")
        result_type = "geo"
        inline_message = raw.types.InputBotInlineMessageMediaGeo(
            geo_point=media.geo_point,
            heading=media.heading if isinstance(media, raw.types.InputMediaGeoLive) else None,
            period=media.period if isinstance(media, raw.types.InputMediaGeoLive) else None,
            proximity_notification_radius=media.proximity_notification_radius
            if isinstance(media, raw.types.InputMediaGeoLive)
            else None,
            reply_markup=query.reply_markup,
        )
    elif isinstance(media, raw.types.InputMediaVenue):
        result_type = "venue"
        inline_message = raw.types.InputBotInlineMessageMediaVenue(
            geo_point=media.geo_point,
            title=media.title,
            address=media.address,
            provider=media.provider,
            venue_id=media.venue_id,
            venue_type=media.venue_type,
            reply_markup=query.reply_markup,
        )
    elif isinstance(media, raw.types.InputMediaContact):
        result_type = "contact"
        inline_message = raw.types.InputBotInlineMessageMediaContact(
            phone_number=media.phone_number,
            first_name=media.first_name,
            last_name=media.last_name,
            vcard=media.vcard,
            reply_markup=query.reply_markup,
        )
    elif isinstance(media, raw.types.InputMediaWebPage):
        inline_message = raw.types.InputBotInlineMessageMediaWebPage(
            url=media.url,
            message=query.message,
            entities=entities or None,
            force_large_media=media.force_large_media,
            force_small_media=media.force_small_media,
            optional=media.optional,
            invert_media=query.invert_media,
            reply_markup=query.reply_markup,
        )

    if inline_message is not None:
        return raw.types.InputBotInlineResult(
            id="message", type=result_type, title="Message", send_message=inline_message
        )

    if not isinstance(
        media,
        (
            raw.types.InputMediaPhoto,
            raw.types.InputMediaUploadedPhoto,
            raw.types.InputMediaPhotoExternal,
            raw.types.InputMediaDocument,
            raw.types.InputMediaUploadedDocument,
            raw.types.InputMediaDocumentExternal,
        ),
    ):
        raise ValueError(f"The helper bot inline API does not support {type(media).__name__}")

    for name in ("ttl_seconds", "spoiler", "video_cover", "video_timestamp"):
        if getattr(media, name, None) not in (None, False):
            raise ValueError(f"The helper bot inline API does not support media option {name}")
    if isinstance(media, raw.types.InputMediaUploadedDocument):
        for attribute in media.attributes:
            if isinstance(attribute, raw.types.DocumentAttributeVideo) and attribute.round_message:
                raise ValueError("The helper bot inline API does not support video notes")

    if not client.helper_bot_chat_id:
        raise ValueError("Sending media through helper_bot requires helper_bot_chat_id")
    peer = await client.resolve_peer(client.helper_bot_chat_id)
    if not isinstance(peer, raw.types.InputPeerChannel):
        raise ValueError(
            "helper_bot_chat_id must be a channel or supergroup accessible to both clients"
        )

    # The bot must see the uploaded media to obtain a file reference for its own account.
    staged = cast(
        Union[raw.types.Updates, raw.types.UpdatesCombined],
        await client.invoke(
            raw.functions.messages.SendMedia(
                peer=peer, media=media, message="", random_id=client.rnd_id(), silent=True
            ),
            **invoke_options,
        ),
    )
    message_id: Optional[int] = None
    for update in staged.updates:
        if isinstance(update, raw.types.UpdateNewChannelMessage):
            message_id = update.message.id
            break

    if message_id is None:
        log.warning("Helper bot media upload returned no message update; destination send skipped")
        return None

    message = cast(types.Message, await helper.get_messages(client.helper_bot_chat_id, message_id))
    if message.empty or message.media is None:
        log.warning("Helper bot staging message is unavailable; destination send skipped")
        return None

    media_types = {
        enums.MessageMediaType.ANIMATION: "gif",
        enums.MessageMediaType.AUDIO: "audio",
        enums.MessageMediaType.DOCUMENT: "file",
        enums.MessageMediaType.VIDEO: "video",
        enums.MessageMediaType.VOICE: "voice",
        enums.MessageMediaType.STICKER: "sticker",
    }
    send_message = raw.types.InputBotInlineMessageMediaAuto(
        message=query.message,
        entities=entities or None,
        reply_markup=query.reply_markup,
        invert_media=query.invert_media,
    )
    if message.photo is not None:
        photo = cast(
            raw.types.InputMediaPhoto, utils.get_input_media_from_file_id(message.photo.file_id)
        )
        return raw.types.InputBotInlineResultPhoto(
            id="message", type="photo", photo=photo.id, send_message=send_message
        )

    file = (
        message.animation
        or message.audio
        or message.document
        or message.video
        or message.voice
        or message.sticker
    )
    if file is None or message.media not in media_types:
        raise ValueError(f"The helper bot inline API does not support {message.media}")
    document = cast(raw.types.InputMediaDocument, utils.get_input_media_from_file_id(file.file_id))
    return raw.types.InputBotInlineResultDocument(
        id="message",
        type=media_types[message.media],
        title="Media",
        document=document.id,
        send_message=send_message,
    )
