import requests,time,hashlib, random
from fake_useragent import UserAgent as ua
from bs4 import BeautifulSoup as bs


# 获取音频地址的url
GET_AUDIO_URL = "https://www.ximalaya.com/revision/play/v1/audio?id={}&ptype=1"
# 获取服务器时间的url
SERVER_TIME_URL = 'https://www.ximalaya.com/revision/time'


# 分析目录页面，获取音乐文件列表
def get_media_info_list(headers, music_list_url):
    # 获取专栏HTML源码
    music_list_r = requests.get(music_list_url, headers=headers)
    # 解析 获取所有li标签
    soup = bs(music_list_r.text, "lxml")
    li = soup.find_all("li", {"class": "lF_"})

    media_infos = {}
    # for循序遍历处理
    for i in li:
        a = i.find("a")   # 找到a标签
        # 获取href属性
        # split("/")将字符串以"/"作为分隔符 从右往左数第一项是id号
        music_id = a.get("href").split("/")[-1]
        # 获取title属性 和“.m4a”拼接成文件名
        music_name = a.get("title") + ".m4a"
        media_infos[music_id] = music_name

    return media_infos


# 获取xm_sign，用于获取音乐文件下载url链接
def get_xm_sign(headers):
    response = requests.get(url=SERVER_TIME_URL, headers=headers)
    server_time = response.text
    real_time = str(round(time.time()*1000))
    xm_sign = str(hashlib.md5("himalaya-{}".format(server_time).encode()).hexdigest()) + "({})".format(str(round(random.random()*100))) + server_time + "({})".format(str(round(random.random()*100))) + real_time
    # print('此次请求的反爬xm-sign为{}'.format(xm_sign))
    new_headers = {
        'User-Agent':headers['User-Agent'],
        'xm-sign':xm_sign
    }
    return new_headers

def get_single_music_url(headers, music_id):
    new_headers = get_xm_sign(headers)

    # 获得音频源地址
    r = requests.get(GET_AUDIO_URL.format(music_id), headers=new_headers)
    json_result = r.json()
    link = json_result['data']['src']
    return link

# 获取音乐文件的 url 链接
def get_music_urls(headers, media_infos):
    music_urls = {}
    for music_id, music_name in media_infos.items():
        link = get_single_music_url(headers, music_id)
        music_urls[link] = music_name
    return music_urls

def download_music(music_urls):
    for music_url, music_name in music_urls.items():
        # 获取音频文件并保存
        music_file = requests.get(music_url).content
        with open(music_name, "wb") as f:
            f.write(music_file)
        print("已下载：%s" % music_name)
    print("下载完毕！")


# 构建微软播放列表 asx 文件内容
def build_music_asx_content(music_urls):
    content = ''
    for music_url, music_name in music_urls.items():
        music_name = music_name.replace('<', '(').replace('>', ')')
        content = content + '<Entry><Title>%s</Title><Ref href = "%s"/></Entry>\n' % (music_name, music_url)
    return content


# 获取整个专辑的 music 链接
def get_all_init_music_urls(album_name, music_list_url, page_start, page_end):
    # UA伪装
    headers = {
        "User-Agent": ua(path=r"fake_useragent_0.1.11.json").random
    }

    with open(album_name+'.asx', "a") as f:
        f.write('<ASX version = "3.0">\n')
    for i in range(page_start,page_end+1):
        media_infos = get_media_info_list(headers, music_list_url + ("p%d/" % i))
        music_urls = get_music_urls(headers, media_infos)
        # download_music(music_urls)
        content = build_music_asx_content(music_urls)
        with open(album_name+'.asx', "a", encoding='gb18030') as f:
            f.write(content)
        print("已获取第[%d]页" % i)

    with open(album_name+'.asx', "a") as f:
        f.write('</ASX>')


# 获取专辑最近更新的 music 链接
def get_update_music_urls(album_name, music_list_url):
    # UA伪装
    headers = {
        "User-Agent": ua(path=r"fake_useragent_0.1.11.json").random
    }

    content = ''
    with open(album_name+'.asx', "r", encoding='gb18030') as f:
        content = f.read()

    media_infos = get_media_info_list(headers, music_list_url)
    music_urls = {}
    for music_id, music_name in media_infos.items():
        if content.__contains__(music_name):
            continue
        link = get_single_music_url(headers, music_id)
        music_urls[link] = music_name
        
    # download_music(music_urls)
    update_content = build_music_asx_content(music_urls)

    if update_content:
        content = content.replace('\n','\n'+update_content, 1) # 只替换第一次出现的c字符
        with open(album_name+'.asx', "w", encoding='gb18030') as f:
            f.write(content)


# get_all_init_music_urls('小南-老歌情怀', 'https://www.ximalaya.com/yinyue/230311/', 1, 28)
# get_all_init_music_urls('小七的私房歌', 'https://www.ximalaya.com/yinyue/237771/', 1, 20)
# get_all_init_music_urls('李峙的不老歌', 'https://www.ximalaya.com/yinyue/236268/', 1, 31)
get_all_init_music_urls('经典留声机', 'https://www.ximalaya.com/yinyue/290996/', 1, 22)

# get_update_music_urls('小南-老歌情怀', 'https://www.ximalaya.com/yinyue/230311/')
