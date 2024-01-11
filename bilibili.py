import json
import re
import requests
import util

# 参考：https://zhuanlan.zhihu.com/p/104769022

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "referer": "https://www.bilibili.com"
}


def get_data(url: str) -> str:
    cookies = util.get_cookies(['.bilibili.com'], util.cfg.get('bilibili', 'browser'))
    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code != 200:
        return None
    return response.text


def get_base_info(text) -> dict:
    data = re.findall(r'<script>window.__INITIAL_STATE__=(.*?);', text, re.S)[0]
    data_json = json.loads(data)['videoData']
    return {
        'vid': data_json['bvid'],
        'title': data_json['title'],
        'cover': data_json['pic'],
        'desc': data_json['desc'],
        'author': data_json['owner'],
        'stat': {
            'view': data_json['stat']['view'],
            'like': data_json['stat']['like'],
            'share': data_json['stat']['share'],
            'coin': data_json['stat']['coin'],
            'favorite': data_json['stat']['favorite'],
            'danmaku': data_json['stat']['danmaku'],
            'reply': data_json['stat']['reply']
        }

    }


def get_video_info(text: str) -> dict:
    data = re.findall(r'<script>window.__playinfo__=(.*?)</script>', text)[0]
    json_data = json.loads(data)
    max_data = max(json_data['data']['dash']['video'], key=lambda x: x["bandwidth"])
    video_url = max_data['base_url']
    audio_url = json_data['data']['dash']['audio'][0]['base_url']
    return {
        "video_url": video_url,
        "audio_url": audio_url,
    }


def download(data: dict, merge: bool) -> str:
    title = data['title']
    video_url = data['video_url']
    audio_url = data['audio_url']
    video_path = util.download(video_url, f"video_{title}.mp4", headers)
    audio_path = util.download(audio_url, f"video_{title}.mp3", headers)
    if merge:
        path = util.merge_video_audio(video_path, audio_path, f"{title}.mp4")
        return path
    else:
        return video_url


def bilibili(url: str) -> str:
    url = util.redirect_url(url, headers)
    data = get_data(url)
    info = get_base_info(data)
    video_info = get_video_info(data)
    info.update(video_info)
    print("data is {}".format(info))

    return download(info, util.cfg.getboolean('bilibili', 'autoMerge'))


if __name__ == '__main__':
    url = 'https://m.bilibili.com/video/BV1wK411v78T'
    res = bilibili(url)
    print("file url is {}".format(res))
