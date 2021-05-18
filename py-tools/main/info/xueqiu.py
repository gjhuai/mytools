# coding=utf-8 
import urllib.request, codecs, re, time, requests, collections
from bs4 import BeautifulSoup
from picker import Picker
import requests, datetime, os


class XueQiu(Picker):
    TODAY_TXT = "today.txt"
    basePath = "xueqiu-"
    #需要登录的网页地址
    LOGIN_URL = 'https://xueqiu.com/u/8115772091'
    article_info_list = [
        {
            'blog_name':'ershifu',
            'article_list_url':'https://xueqiu.com/v4/statuses/user_timeline.json?page=1&user_id=8115772091',
            # 'attrsFilters': {"class":"txt", "id":"txt"},
            'download':True
        }
    ]

    def __init__(self):
        # self.chapter_map = collections.OrderedDict()
        pass

    def get_lastest_download_time(self, blog_config_path, delta_days=0):
        last_line = self.__get_last_line(blog_config_path)
        if last_line:
            t = last_line.decode('utf-8').split('|')[0]
            return int(t)
        else:
            today = datetime.datetime.today()
            dt = datetime.datetime(today.year, today.month, today.day+delta_days, 0, 0, 0)
        # delta=datetime.timedelta(days=-1)
        # dt=dt+delta
        # print(dt)
            return int(dt.timestamp()*1000)

    def get_lastest_urls(self, session, article_list_url, lastest_download_time):
        # 获取列表
        resp = session.get(article_list_url, headers=XueQiu.headers)
        article_list = resp.json()

        art_url_tmpl = "https://xueqiu.com/%s/%s"

        art_url_list = []
        for art in article_list['statuses']:
            created_at = art['created_at']
            if created_at > lastest_download_time:
                art_url = art_url_tmpl % (art['user_id'], art['id'])
                art_url_list.append([art_url, art['title'], created_at])
        return art_url_list

    def get_chapter_content(self, session, art_url, attrsFilters='', excludeTags=[]):
        resp = session.get(art_url, headers=XueQiu.headers)
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

        # content = art_content.get_text("\n")
        content = self.html_to_text(art_content)
        return [title, content]



    def html_to_text(self, art_content):
        from bs4 import BeautifulSoup, NavigableString
        "Creates a formatted text email message as a string from a rendered html template (page)"

        # Ignore anything in head
        body, text = art_content, []
        for element in body.descendants:
            # We use type and not isinstance since comments, cdata, etc are subclasses that we don't want
            if type(element) == NavigableString:
                # We use the assumption that other tags can't be inside a script or style
                if element.parent.name in ('script', 'style'):
                    continue

                # remove any multiple and leading/trailing whitespace
                string = ' '.join(element.string.split())
                if string:
                    if element.parent.name == 'a':
                        a_tag = element.parent
                        # replace link text with the link
                        string = a_tag.text
                        # concatenate with any non-empty immediately previous string
                        if ( type(a_tag.previous_sibling) == NavigableString and
                                a_tag.previous_sibling.string.strip() ):
                            text[-1] = text[-1] + '' + string
                            continue
                    elif element.previous_sibling and element.previous_sibling.name == 'a':
                        text[-1] = text[-1] + '' + string
                        continue
                    elif element.parent.name == 'p':
                        # Add extra paragraph formatting newline
                        string = '\n' + string
                    text += [string]
        doc = '\n'.join(text)
        return doc

    def download(self, delta_day=0):
        self.__backup_article_file()
        session = requests.Session()  #用来保存cookie
        session.post(self.LOGIN_URL, headers=XueQiu.headers)

        for article_info in XueQiu.article_info_list:
            if (article_info['download']==True):
                blog_config_path = XueQiu.basePath + article_info['blog_name']+'.txt'
                lastest_download_time = self.get_lastest_download_time(blog_config_path, delta_day)

                # 获取列表
                art_map = {} #collections.OrderedDict()
                art_url_list = self.get_lastest_urls(session, article_info['article_list_url'], lastest_download_time)
                for art_url in art_url_list:
                    if art_url[2] <= lastest_download_time:
                        continue
                    art = self.get_chapter_content(session, art_url[0])
                    print(art)
                    self.__write_file(XueQiu.TODAY_TXT, "\n\n\n\n\n\n第1章 %s\n\n" % art[0])
                    self.__write_file(XueQiu.TODAY_TXT, art[1])
                    # 记录本次下载的信息
                    # 文件名： xueqiu-${blog_name}, 例如： xueqiu-ershifu
                    # 内容： time|${art.title}
                    art_map[art_url[2]] = art[0]

                art_map = sorted(art_map.items(), key=lambda t: t[0])
                art_str = '\n'.join(["%s|%s" % (str(a[0]), a[1]) for a in art_map])
                self.__write_file(blog_config_path, art_str)

    def __write_file(self, path, text, encoding="gb18030"):
        with open(path, mode="a", encoding='utf-8') as myfile:
            myfile.write(text.encode('utf-8', 'ignore').decode('utf-8'))

    def log(self, log_content):
        self.__write_file("debug.log", '\n#######################################\n#######################################\n' + log_content)

    def __backup_article_file(self):
        now = datetime.datetime.now()
        if now.hour==9:
            yesterday = now + datetime.timedelta(days=-1)
            bak_filename = "article_%d-%d-%d.txt" % (yesterday.year, yesterday.month, yesterday.day)
            if os.path.exists(bak_filename):
                return
            if os.path.exists(XueQiu.TODAY_TXT):
                os.rename(XueQiu.TODAY_TXT, bak_filename)

    def __get_last_line(self, filename):
        """
        get last line of a file
        :param filename: file name
        :return: last line or None for empty file
        """
        try:
            filesize = os.path.getsize(filename)
            if filesize == 0:
                return None
            else:
                with open(filename, 'rb') as fp: # to use seek from end, must use mode 'rb'
                    offset = -8                 # initialize offset
                    while -offset < filesize:   # offset cannot exceed file size
                        fp.seek(offset, 2)      # read # offset chars from eof(represent by number '2')
                        lines = fp.readlines()  # read from fp to eof
                        if len(lines) >= 2:     # if contains at least 2 lines
                            return lines[-1]    # then last line is totally included
                        else:
                            offset *= 2         # enlarge offset
                    fp.seek(0)
                    lines = fp.readlines()
                    return lines[-1]
        except FileNotFoundError:
            print(filename + ' not found!')
            return None

# picker = XueQiu()
# picker.download(-3)



