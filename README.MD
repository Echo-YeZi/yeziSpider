# 叶子爬虫项目
>用于爬取视频的简易脚本，目前仅支持B站和抖音
> 
>默认爬取最高画质

# 使用
- 修改config.ini，特别是browser
- 在对应浏览器上打开视频网站的任意页面（不需要打开视频源地址）
  - 画质默认为最高，未登录会降低画质
- 修改对应脚本中的main方法下的url为目标网站
- 运行python脚本

# 基础环境配置
- 基本环境：python3.12（向下兼容版本未知）
- 第三方库清单：
  - rookiepy：捕获浏览器的cookie
  - moviepy：处理视频和音频（仅B站使用）
- 配置文件：根目录下的config.ini

# 已支持
- 爬取B站视频数据，下载合并视频和音频（有水印）
  - 下载后会包括无声视频，音频，有声视频三个文件
- 爬取抖音视频数据，下载（无水印）

# 未支持
- 数据已抓取，但未做存储，请自行处理数据
- B站视频会带有水印，后期可能会更新去水印功能
- 可视化UI

# LICENSE
MIT