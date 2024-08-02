from redditpy.chat import RedditChat


class RedditBot(RedditChat):
    def __init__(self, username: str, password: str, proxy: dict = None):
        super(RedditChat, self).__init__(username, password, proxy)

