import requests
import uuid
from redditpy.url_const import *
from redditpy.exceptions import WrongCreds, APIException
from typing import Optional


class _RedditAuthBase:
    def __init__(self, api_token=None, reddit_session=None, proxy=None):
        self.api_token = api_token
        self.user_id = None
        self.reddit_session = reddit_session
        self.proxy = proxy

    @property
    def is_reauthable(self):
        return self.reddit_session is not None and self.api_token is not None

    def refresh_api_token(self):
        cookies = {'reddit_session': self.reddit_session}
        headers = {
            'User-Agent': WEB_USERAGENT,
            'Authorization': f'Bearer {self.api_token}',
        }
        data = {
            'accessToken': self.api_token,
            'unsafeLoggedOut': 'false',
            'safe': 'true'
        }
        response = requests.post(f'{WWW_REDDIT}/refreshproxy', headers=headers, cookies=cookies, data=data,
                                 proxies=self.proxy).json()
        self.api_token = response['accessToken']
        return self.api_token


class PasswordAuth(_RedditAuthBase):
    def __init__(self, reddit_username: str, reddit_password: str, twofa: Optional[str] = None,
                 proxy: dict[str, str] = None):
        super().__init__(proxy=proxy)
        self.reddit_username = reddit_username
        self.reddit_password = reddit_password
        self.twofa = twofa
        self._client_vendor_uuid = str(uuid.uuid4())
        self.reddit_session = None
        self.proxy = proxy

    def authenticate(self):
        if self.is_reauthable:
            self.refresh_api_token()
        else:
            self.reddit_session = self._do_login()
            self.api_token = self._get_api_token()

    def _get_api_token(self):
        cookies = {'reddit_session': self.reddit_session}
        headers = {
            'Authorization': f'Basic {OAUTH_CLIENT_ID_B64}',
            'User-Agent': MOBILE_USERAGENT,
            'client-vendor-id': self._client_vendor_uuid,
        }
        data = '{"scopes":["*"]}'
        response = requests.post(f'{ACCOUNTS_REDDIT}/api/access_token', headers=headers, cookies=cookies, data=data,
                                 proxies=self.proxy)
        try:
            access_token = response.json()['access_token']
        except KeyError:
            raise APIException(response)
        return access_token

    def _do_login(self):
        headers = {
            'User-Agent': WEB_USERAGENT,
            'Accept': 'application/json, text/javascript, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://old.reddit.com/login',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://old.reddit.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
        data = {
            'op': 'login',
            'user': self.reddit_username,
            'passwd': f'{self.reddit_password}:{self.twofa}' if bool(self.twofa) else self.reddit_password,
            'api_type': 'json'
        }
        response = requests.post(f'{WWW_REDDIT}/api/login/{self.reddit_username}', headers=headers, data=data,
                                 proxies=self.proxy)
        reddit_session = response.cookies.get("reddit_session")
        if reddit_session is None:
            raise WrongCreds(f"Wrong username or password U: {self.reddit_username} | P: {self.reddit_password}")
        return reddit_session


class TokenAuth(_RedditAuthBase):
    def __init__(self, token, reddit_session=None):
        super().__init__(token, reddit_session)

