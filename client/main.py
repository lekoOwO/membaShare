import sys
import socket
from contextlib import closing
import os
import urllib.request
import shlex
import subprocess
from pyngrok import ngrok

def get_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('localhost', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

def run_proxy(port=8080):
    cmd = f"'{sys.executable}' ./proxy.py {port} localhost"
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def run_ngrok(port, key):
    ngrok.set_auth_token(key)
    tunnel = ngrok.connect(port, "tcp")
    return tunnel.public_url.replace("tcp://", "socks5h://")

def get_m3u8(video_id, server, proxy):
    url = f"{server}/{video_id}"
    data = proxy.encode('utf8')
    req = urllib.request.Request(url, data=data)

    response = urllib.request.urlopen(req)
    resp_data = response.read().decode('utf8')
    return resp_data

if __name__ == '__main__':
    if not os.path.isfile("./apikey.txt"):
        print("[ERROR] No ngrok API Key found!")
        sys.exit(1)
        
    if sys.argv[1:]:
        video_id = sys.argv[1]
    else:
        video_id = input("Video ID: ")
    
    if sys.argv[2:]:
        server = sys.argv[2]
    else:
        server = input("Server: ")

    proxy_port = get_free_port()
    run_proxy(proxy_port)

    f = open('./apikey.txt', 'r')
    api_key = f.readlines()[0]
    f.close()

    proxy = run_ngrok(proxy_port, api_key)

    m3u8_url = get_m3u8(video_id, server, proxy).rstrip()
    print(m3u8_url)
