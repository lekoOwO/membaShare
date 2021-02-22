import falcon
import sys

import multiprocessing
import subprocess
import shlex
import re

def get_cookie():
    cookies = {}
    result = ''
    with open("./cookies.txt", 'r') as fp:
        for line in fp:
            if not re.match(r'^\#', line):
                lineFields = line.strip().split('\t')
                if len(lineFields) <= 6:
                    continue
                cookies[lineFields[5]] = lineFields[6]
    for k in cookies:
        result += f" --http-cookie \"{k}={cookies[k]}\""
    return result

cookie_param = get_cookie()

def get_m3u8(video_id, proxy):
    cmd = f"streamlink --https-proxy '{proxy}' --stream-url 'https://www.youtube.com/watch?v={video_id}' {cookie_param}"
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    if type(out) == bytes:
        out = out.decode(sys.stdout.encoding)
    if type(err) == bytes:
        err = err.decode(sys.stdout.encoding)

    return out

class M3u8:
    def on_post(self, req, resp, video_id):
        proxy = req.bounded_stream.read().decode('utf-8')

        m3u8_link = get_m3u8(video_id, proxy)

        resp.body = m3u8_link
        resp.status = falcon.HTTP_200

api = falcon.API()
api.add_route('/{video_id}', M3u8())