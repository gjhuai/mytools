# coding=utf-8

import json, time, datetime, ssl
import urllib.request
from bs4 import BeautifulSoup

novel_list = [
    {
        'name': '汉乡',
        'url': 'https://www.biquge.com.cn/book/29843/',
        'prefix': 'https://www.biquge.com.cn/book/29843/',
        'download': True
    },
    {
        'name': '大医凌然',
        'url': 'https://www.biquge.com.cn/book/32697/',
        'prefix': 'https://www.biquge.com.cn/book/32697/',
        'download': True
    },
    {
        'name': '医路坦途',
        'url': 'https://www.dingdiann.com/ddk176731/',
        'prefix': 'https://www.dingdiann.com/ddk176731/',
        'download': True
    },
    {
        'name': '放开那个女巫',
        'url': 'https://www.biquge.com.cn/book/16556/',
        'prefix': 'https://www.biquge.com.cn/book/16556/',
        'download': False
    },

]

default_headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

ssl._create_default_https_context = ssl._create_unverified_context


def getHtml(url, headers=default_headers):
    req = urllib.request.Request(url = url , headers = headers)
    res = urllib.request.urlopen(req)
    html = res.read()
    return html


def getChapters(catalogUrl , urlPrefix, headers=default_headers):
    emap = {}
    
    idx = catalogUrl.index("/", catalogUrl.index("//") + 2)
    # 抓取站点url
    siteUrl = catalogUrl[:idx]
    # 文字根url
    subUrl = catalogUrl[idx:]
    
    #html = html.decode('utf-8')
    html = getHtml(catalogUrl , headers)
    #soup =  BeautifulSoup(html,'lxml')
    soup =  BeautifulSoup(html,'html.parser')

    links = soup.find_all('a', href=True)
    for link in links:
        href = link.get('href')
        if href==None or href.strip()=='':
            continue
        if href.find("javascript")>-1 or href.startswith("#"):
            continue

        # e.g. /2546/89898.html, 从根路径开始
        #print(href)
        if href[0]=='/':
            href = siteUrl + href
        elif not href.startswith("http"):	# // e.g. 2546/89898.html, 从当前页面相对开始
            href = siteUrl + subUrl[0:subUrl.rindex('/')] + "/" + href;
        if not href.startswith(urlPrefix) or href.strip()==urlPrefix.strip():
            continue;

        emap[link.string] = href

    return  emap


def get_last_max_url_map(novel_list):
    with open('.last_chapter','r', encoding='UTF-8') as f:
        last_chapter = f.readline()
    # posMap = {'汉乡':'446724918.html','大医凌然':'https://www.biquge.com.cn/book/32697/1084062.html'}
    posMap = json.loads(last_chapter)
    newPosMap = {}
    for novel in novel_list:
        newPosMap[novel['name']] = posMap.get(novel['name'])
    return newPosMap


def get_posted_chapter(last_max_url, novel):
    url = novel['url']
    urlPrefix = novel['prefix']
    print(datetime.datetime.now().strftime('[%m-%d %H:%M] ') + "获取【" + novel['name'] + "】的章节：")
    chapters = getChapters(url, urlPrefix).items()

    need_post_urls = []
    for (chName, chUrl) in chapters:
        if not last_max_url or (len(chUrl) >= len(last_max_url) and chUrl > last_max_url):
            need_post_urls.append(chUrl)
    # 排序
    import functools
    def cmp(a, b):
        la = len(a);
        lb = len(b)
        if la > lb:
            return 1
        elif la == lb and a > b:
            return 1
        elif a == b:
            return 0
        else:
            return -1
    sorted_links = sorted(need_post_urls, key=functools.cmp_to_key(cmp))
    return sorted_links

def post_chapter(novel_list):
    max_url_map = get_last_max_url_map(novel_list)

    for novel in novel_list:
        if (novel['download']==True):
            success = 1
            last_max_url = max_url_map.get(novel['name'])
            sorted_links = get_posted_chapter(last_max_url, novel)
            if len(sorted_links)>0:
                max_url_map[novel['name']] = sorted_links[-1]
            for link in sorted_links:
                print(datetime.datetime.now().strftime('[%m-%d %H:%M]') + " Posting: " + link)
                poster = pocket.PagePoster()
                success = poster.post_page(link)
                if success==-1:
                    break
                time.sleep(5)

            # print(max_url_map)
            if success==1:
                with open('.last_chapter','w', encoding='UTF-8') as f:
                    f.write(str(max_url_map).replace("'",'"'))

while(True):
    try:
        post_chapter(novel_list)
    except Exception as e:
        print("app catch: %s\n" % ( e))
    time.sleep(2*60*60)
