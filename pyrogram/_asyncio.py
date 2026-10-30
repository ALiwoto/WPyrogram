import asyncio


def get_event_loop() -> asyncio.AbstractEventLoop:
    """Return the thread's loop, creating one for synchronous client use."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = None

    if loop is None or loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop
