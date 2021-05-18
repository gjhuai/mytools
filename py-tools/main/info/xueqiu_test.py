# coding=utf-8

import json, time, datetime, ssl
import urllib.request
from bs4 import BeautifulSoup

import requests
from fake_useragent import UserAgent

def get_today_zero_hour():
    today = datetime.datetime.today()
    dt = datetime.datetime(today.year, today.month, today.day-1, 0, 0, 0)
    # delta=datetime.timedelta(days=-1)
    # dt=dt+delta
    # print(dt)
    return int(dt.timestamp()*1000)
    # print(1621067790000)

headers = {"User-Agent":UserAgent().chrome}
login_url = "https://xueqiu.com/u/8115772091" #需要登录的网页地址
list_url = "https://xueqiu.com/v4/statuses/user_timeline.json?page=1&user_id=8115772091" #登录完账号密码以后的网页地址

def get_today_article_from_ershifu():
    session = requests.Session()  #用来保存cookie
    response = session.post(login_url,headers=headers)

    # 获取列表
    resp = session.get(list_url,headers=headers)
    article_list = resp.json()

    zero_hour_time = get_today_zero_hour()
    art_url_tmpl = "https://xueqiu.com/%s/%s"

    art_list = []
    for art in article_list['statuses']:
        created_at = art['created_at']
        if created_at > zero_hour_time:
            art_url = art_url_tmpl % (art['user_id'], art['id'])
            #print(art_url)
            resp = session.get(art_url,headers=headers)
            html = resp.text
            # <h1 class="article__bd__title">警惕三高</h1>
            # <div class="article__bd__detail">
            soup =  BeautifulSoup(html, 'lxml')
            art_title = soup.find('h1', attrs={"class":'article__bd__title'})
            title = art_title.get_text("\n")
            art_content = soup.find('div', attrs={"class":'article__bd__detail'})
            # <p style="display:none;">来源：雪球App，作者： 二师父定投，（https://xueqiu.com/8115772091/179927875）</p>
            display_none = art_content.find('p', attrs={"style":'display:none;'})
            #print(tag.name)
            display_none.extract()

            content = art_content.get_text("\n")
            art_list.append([title, content])
    return art_list

art = get_today_article_from_ershifu()
print(art)