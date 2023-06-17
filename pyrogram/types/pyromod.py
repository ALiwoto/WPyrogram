from enum import Enum


class ListenerStopped(Exception):
    pass


class ListenerTimeout(Exception):
    pass


class ListenerTypes(Enum):
    MESSAGE = "message"
    CALLBACK_QUERY = "callback_query"
