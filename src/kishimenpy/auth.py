import requests

LOGIN_URL = "https://secure.nicovideo.jp/secure/login"
MYPAGE_URL = "http://www.nicovideo.jp/my/top"


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
        # 0: Logout
        # 1: Login as free user
        # 3: Login as premium user
        return not response.headers["x-niconico-authflag"] == "0"

    def login(self, mail=None, password=None):
        if mail:
            self.mail = mail
        if password:
            self.password = password
        response = self.post(LOGIN_URL, data={
            "mail": self.mail,
            "password": self.password,
        })
        if not self.is_login(response):
            raise LoginError(
                "mail: \"{mail}\", password: \"{password}\"".format(
                    mail=self.mail,
                    password=self.password,
                )
            )

    def logout(self):
        self._session = requests.Session()


def login(mail, password):
    session = Session()
    session.login(mail, password)
    return session
