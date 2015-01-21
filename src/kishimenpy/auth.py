import enum

import requests

LOGIN_URL = 'https://secure.nicovideo.jp/secure/login?site=niconico'
MYPAGE_URL = 'http://www.nicovideo.jp/my/top'


class AuthFlag(enum.Enum):
    Logout = '0'
    FreeUser = '1'
    PremiumUser = '3'


class LoginError(Exception):
    pass


class Session(object):
    def __init__(self, session=None):
        if not session:
            session = requests.Session()
        self._session = session

    def get(self, *args, **kwargs):
        return self._session.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self._session.post(*args, **kwargs)

    def is_login(self, response=None):
        if not response:
            response = self.get(MYPAGE_URL)
        authflag = response.headers.get('x-niconico-authflag')
        if authflag is None:
            return False
        return AuthFlag(authflag) is not AuthFlag.Logout

    def login(self, mail=None, password=None):
        response = self.post(LOGIN_URL, data={
            'mail': mail,
            'password': password,
        })
        if not self.is_login(response):
            raise LoginError('mail: "%s", password: "****************"' % mail)

    def logout(self):
        self._session = requests.Session()


def login(mail, password):
    session = Session()
    session.login(mail, password)
    return session