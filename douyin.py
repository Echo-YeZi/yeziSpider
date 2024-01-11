import json
import re
import requests
import util

# 参考来源：https://cloud.tencent.com/developer/article/2034236, https://cloud.tencent.com/developer/article/1635251?areaId=106001

headers = {
    # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
}


def get_url(url):
    pattern = r'//\S+/(\d+)'
    match = re.search(pattern, url)
    if match:
        return f'https://m.douyin.com/share/video/{match.group(1)}'
    else:
        raise Exception(f'{url}无法识别')


def get_data(url: str) -> str:
    url = get_url(url)

    cookies = util.get_cookies(['.douyin.com'], util.cfg.get('douyin', 'browser'))
    response = requests.get(url, headers=headers, cookies=cookies)

    if response.status_code != 200:
        return None

    return response.text


def get_info(text: str):
    # get video
    data = re.findall(r'<script id="RENDER_DATA" type="application/json">(.*?)</script>', text, re.S)[0]
    data = requests.utils.unquote(data)
    json_data = json.loads(data)
    data = json_data['app']['videoInfoRes']['item_list'][0]

    res = {
        'title': data['desc'],
        'cover': data['video']['cover']['url_list'][0],
        'author': {
            'short_id': data['author']['short_id'],
            'nickname': data['author']['nickname'],
            'avatar': data['author']['avatar_thumb']['url_list'][0],
            'unique_id': data['author']['unique_id']
        },
        'music': {
            'mid': data['music']['mid'],
            'title': data['music']['title'],
            'author': data['music']['author'],
            'cover': data['music']['cover_hd'],
        },
        'video': {
            'uri': data['video']['play_addr']['uri'],
            'height': data['video']['height'],
            'width': data['video']['width'],
        },
        'stat': {

        }
    }
    return res


def download(data: dict):
    url = f'https://aweme.snssdk.com/aweme/v1/play/?video_id={data['video']['uri']}&ratio=1080p'
    return util.download(url, f'{data['title']}.mp4', headers)


def douyin(url: str) -> str:
    url = util.redirect_url(url, headers)
    data = get_data(url)
    info = get_info(data)
    print("data is {}".format(info))

    return download(info)


if __name__ == '__main__':
    url = "https://www.iesdouyin.com/share/video/7322303483225328931/?region=CN&mid=7322303539475254054&u_code=ij254786&did"
    res = douyin(url)
    print("file url is {}".format(res))
