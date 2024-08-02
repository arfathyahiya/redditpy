from redditpy.base import _RedditBase


class RedditChat(_RedditBase):
    def __init__(self, username: str, password: str, proxy: dict = None ):
        super(_RedditBase, self).__init__(username, password, proxy)

    def matrix_login(self):
        pass

    def get_filter_id(self):
        pass

    def get_new_messages(self):
        pass

    def send_message(self, message):
        pass

    def read_markers(self):
        pass

