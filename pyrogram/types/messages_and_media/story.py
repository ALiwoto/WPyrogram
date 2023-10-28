import pyrogram

class Story:
    peer = None
    story_item: "pyrogram.raw.types.StoryItem" = None

    _client: "pyrogram.Client" = None

    def __init__(self, client: "pyrogram.Client", peer, story_item: "pyrogram.raw.types.StoryItem") -> None:
        self.peer = peer
        self.story_item = story_item
        self._client = client

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        peer,
        the_story: "pyrogram.raw.types.StoryItem"
    ):
        #TODO: parse more stuff here maybe....
        return Story(client=client, peer=peer, story_item=the_story)