from xml.etree import ElementTree
from urllib.parse import unquote

import requests

from kishimenpy import auth

GET_THUMB_INFO_URL = "http://ext.nicovideo.jp/api/getthumbinfo/{video_id}"
THUMB_URL = "http://ext.nicovideo.jp/thumb/{video_id}"
GET_FLV_URL = "http://flapi.nicovideo.jp/api/getflv/{video_id}"
GET_MARQUEE_URL = "http://flapi.nicovideo.jp/api/getmarquee?"
GET_RELATION_URL = (
    "http://flapi.nicovideo.jp/api/getrelation"
    "?page={page}"
    "&sort={sort}"
    "&order={order}"
    "&video={video_id}"
)
MSG_URL = "http://msg.nicovideo.jp/{video_id}/api"


class VideoDeleted(Exception):
    pass


class VideoNotFound(Exception):
    pass


class UnknownError(Exception):
    pass


class ThumbnailInfo(dict):
    def __init__(self, element):
        self.element = element
        for e in element.getchildren():
            if e.tag == "tags":
                self.__setitem__(e.tag, [
                    tag.text
                    for tag in e.getchildren()
                ])
            else:
                self.__setitem__(e.tag, e.text)


def get_thumb_info(video_id):
    res = requests.get(GET_THUMB_INFO_URL.format(video_id=video_id))

    root = ElementTree.fromstring(res.text)
    status = root.get("status")
    if not status == "ok":
        error = root.getchildren()[0]
        code, description = error.getchildren()
        if code.text == "DELETED":
            raise VideoDeleted(description.text)
        if code.text == "NOT_FOUND":
            raise VideoNotFound(description.text)
        else:
            raise UnknownError(
                "code: {code}, description: {description}".format(
                    code=code.text,
                    description=description.text,
                )
            )
    return ThumbnailInfo(root.getchildren()[0])


def get_flv(session, video_id):
    res = session.get(GET_FLV_URL.format(video_id=video_id))
    flv = {
        p.split("=")[0]: unquote(p.split("=")[1])
        for p in res.text.split("&")
    }
    if "closed" in flv and flv["closed"] == "1":
        raise auth.LoginError(flv)
    else:
        return flv
