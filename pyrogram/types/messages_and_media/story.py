import pyrogram

class Story:
    peer = None
    story_item = None

    def __init__(self, peer, story_item) -> None:
        pass

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        peer,
        the_story: "pyrogram.raw.types.StoryItem"
    ):
        #TODO: parse more stuff here maybe....
        return Story(peer=peer, story_item=the_story)