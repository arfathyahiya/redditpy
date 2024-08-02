from redditpy.auth import PasswordAuth
from redditpy import exceptions
from redditpy.url_const import *
import typing
import requests


class _RedditBase:
    def __init__(self, username: str, password: str, proxy: dict = None):
        self.username = username
        self.password = password
        self.proxy = proxy
        self.auth = PasswordAuth(reddit_username=username, reddit_password=password, proxy=proxy)
        self.email = None

    def _make_request(
            self, method: typing.Literal["GET", "POST", "PUT", "DELETE"],
            url: str, headers: dict = None, params: dict = None, auth=True, payload: dict = None, data=None,
            proxies=None, cookies=None,
    ):
        if not headers:
            headers = {
                'User-Agent': WEB_USERAGENT,
                'Accept': 'application/json, text/javascript, */*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://reddit.com/',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://reddit.com',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
            }
        if auth is True:
            headers['Authorization'] = f"Bearer {self.auth.api_token}"
        if not proxies:
            proxies = self.proxy

        response = requests.request(
            method=method, url=url, headers=headers, cookies=cookies,
            json=payload, data=data, proxies=proxies, params=params
        )
        if 200 <= response.status_code < 300:
            return response
        elif response.status_code == 400:
            raise exceptions.BadRequest(response)
        elif response.status_code == 401:
            raise exceptions.Unauthorized(response)
        elif response.status_code == 403:
            raise exceptions.Forbidden(response)
        elif response.status_code == 404:
            raise exceptions.NotFound(response)
        elif response.status_code == 429:
            raise exceptions.TooManyRequests(response)
        elif response.status_code >= 500:
            raise exceptions.APIException(response)
        elif not 200 <= response.status_code < 300:
            raise exceptions.HTTPException(response)
        return response

    def refresh_api_token(self):
        self.auth.refresh_api_token()

    def get_oauth_about(self):
        params = {
            "redditWebClient": "desktop2x",
            "app": "desktop2x-client-production",
            "gilding_detail": 1,
            "awarded_detail": 1,
            "raw_json": 1
        }
        response = self._make_request("GET", f"{OAUTH_REDDIT}/user/{self.username}/about.json", params=params)
        return response

    def check_account_suspension(self):
        resp = self.get_oauth_about()
        if resp.ok:
            is_suspended = resp.json().get('data').get('is_suspended')
            return is_suspended

    def check_account_ban(self):
        try:
            self._make_request("GET", f"{WWW_REDDIT}/user/{self.username}.json", auth=False)
            return False
        except exceptions.NotFound:
            return True

    def update_email(self, email: str):
        url = OAUTH_REDDIT + "/api/update_email"
        data = {"email": email}
        if self.email:
            data['curpass'] = self.password
        resp = self._make_request("POST", url, data=data)
        try:
            resp_data = resp.json()
        except requests.exceptions.JSONDecodeError:
            return False
        if resp_data.get("success") is True:
            self.email = email
            return True

    def send_verification_email(self):
        url = OAUTH_REDDIT + "/api/send_verification_email"
        resp = self._make_request("GET", url)
        try:
            resp_data = resp.json()
        except requests.exceptions.JSONDecodeError:
            return False
        if resp_data.get("success") is True:
            return True
