from argparse import ArgumentParser
import os
import re
import sys

from kishimenpy import api, auth

VIDEO_URL_PATTERN = re.compile(r"http://www\.nicovideo\.jp/watch/(\w+)")
BLOCK_SIZE = 1024 * 10  # 10KB


def cmd_download(args):
    mail = args.mail
    password = args.password
    if not (mail and password):
        # TODO: raw input?
        print("Please specify mail and password")
        sys.exit(1)

    dest = os.path.expanduser(args.dest)
    if not os.path.exists(dest):
        os.mkdir(dest)

    session = auth.login(mail, password)

    for video_url in args.video_urls:
        download(session, video_url, dest, args.retry)


def get_video_id(video_url):
    m = VIDEO_URL_PATTERN.match(video_url)
    return m.group(1)


def download(session, video_url, dest, retry):
    video_id = get_video_id(video_url)
    thumb_info = api.get_thumb_info(video_id)
    title = thumb_info["title"]
    movie_type = thumb_info["movie_type"]
    if movie_type == "swf":
        ext = "flv"
    else:
        ext = movie_type

    filename = "{video_id}_{title}.{ext}".format(
        video_id=video_id, title=title, ext=ext
    )
    # TODO: more safe filename
    filename = filename.replace(" ", "")
    filename = filename.replace("　", "")
    filename = filename.replace("/", "_")
    filepath = os.path.join(dest, filename)

    if os.path.exists(filepath):
        print("Already exists: {filename}".format(filename=filename))
        return

    with open(filepath, "wb") as fp:
        print("Directory: {dest}".format(dest=dest))
        print("Filename : {filename}".format(filename=filename))
        print("Downloading video data ...")
        sys.stdout.flush()

        retry_count = 0
        while retry_count <= retry:
            try:
                flv = api.get_flv(session, video_id)
                flv_url = flv["url"]
                # Access once and cache
                session.get(video_url)
                response = session.get(flv_url, stream=True)
                if not (
                    response.status_code == 200 or  # OK
                    response.status_code == 206     # Partial Content
                ):
                    # TODO: Forbidden
                    raise auth.LoginError(response.status_code)
                while True:
                    video_data = response.raw.read(BLOCK_SIZE)
                    if not video_data:
                        break
                    fp.write(video_data)
                    # TODO: Show progress bar
            except (
                api.VideoDeleted,
                api.VideoNotFound,
                api.UnknownError,
            ) as e:
                print(e)
                retry_count += 1
            except (
                auth.LoginError,
            ) as e:
                print(e)
                session.login()
                retry_count += 1
            else:
                break


def create_parser():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()
    download_parser = subparsers.add_parser("download")
    download_parser.add_argument("-m", "--mail", dest="mail")
    download_parser.add_argument("-p", "--password", dest="password")
    download_parser.add_argument("-d", "--dest", dest="dest", default=".")
    download_parser.add_argument("-r", "--retry", dest="retry", default=5)
    download_parser.add_argument("video_urls", nargs="*")
    download_parser.set_defaults(func=cmd_download)
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
