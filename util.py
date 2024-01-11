import os
import rookiepy
import requests
import re
from moviepy.editor import *
from urllib.parse import urljoin
from configparser import ConfigParser

# 读取配置文件
cfg = ConfigParser()
cfg.read('config.ini', encoding='utf-8')

# 获取输出文件目录
downloadPath = cfg['DEFAULT']['downloadPath']
outputDir = os.path.join(os.path.expanduser(downloadPath))
if not os.path.exists(outputDir):
    os.mkdir(outputDir)
if not os.path.isdir(outputDir):
    raise Exception(f'路径{outputDir}不是文件夹！')


# 从浏览器获取cookie
def get_cookies(domain: list, browser: str):
    match browser:
        case 'firefox':
            cookies = rookiepy.firefox(domain)
        case 'edge':
            cookies = rookiepy.edge(domain)
        case 'chrome':
            cookies = rookiepy.chrome(domain)
        case _:
            cookies = None
    if cookies is None:
        raise Exception('浏览器不正确！')
    return rookiepy.to_cookiejar(cookies)


# 整体下载，已废弃
# def download(url: str, name: str, header=None, cookies=None):
#     if header is None:
#         header = {}
#     if cookies is None:
#         response = requests.get(url, headers=header)
#     else:
#         response = requests.get(url, headers=header, cookies=cookies)
#     dir = os.path.join(os.path.expanduser("~/Desktop/cache"))
#     if not os.path.exists(dir):
#         os.mkdir(dir)
#     if not os.path.isdir(dir):
#         raise Exception(f'路径{dir}不是文件夹！')
#     path = os.path.join(dir, name)
#     open(path, 'wb').write(response.content)
#     return path


# 分片下载
def download(url: str, name: str, headers=None, cookies=None):
    path = os.path.join(outputDir, name)
    if os.path.exists(path):
        os.remove(path)

    session = requests.Session()
    if cookies is not None:
        session.cookies.update(cookies)
    if headers is None:
        headers = {}

    # 分片下载
    begin = 0
    end = 1024 * 512 * 10 - 1
    flag = 0
    while True:
        headers.update({'Range': 'bytes=' + str(begin) + '-' + str(end)})
        res = session.get(url=url, headers=headers, verify=False)
        if res.status_code != 416:
            begin = end + 1
            end = end + 1024 * 512
        else:
            headers.update({'Range': str(end + 1) + '-'})
            res = session.get(url=url, headers=headers, verify=False)
            flag = 1
        with open(path, 'ab') as fp:
            fp.write(res.content)
            fp.flush()

        if flag == 1:
            fp.close()
            session.close()
            return path


# 合并视频和音频
def merge_video_audio(video_path, audio_path, name):
    output_path = os.path.join(outputDir, name)
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    video.set_audio(audio)
    video.write_videofile(output_path)
    return output_path


def redirect_url(url: str, headers: dict):
    urls = re.findall(r'(https?://\S+)', url)
    if urls is None or len(urls) == 0:
        raise Exception('未匹配到url')
    url = urls[0]
    response = requests.get(url, headers=headers, allow_redirects=False)
    if response.status_code == 200:
        pass
    elif response.status_code == 301 or response.status_code == 302:
        location = response.headers.get('Location')
        url = urljoin(url, location)
    else:
        raise Exception('链接检测异常！')
    return url
