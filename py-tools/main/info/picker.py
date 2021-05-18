# coding=utf-8 
import urllib.request, codecs, re, time, requests, collections
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class Picker(object):
    headers = {"User-Agent":UserAgent(verify_ssl=False).chrome}
    FAILED = "FAILED"
    retry_num = 3

    def __init__(self):
        with open("debug.log", "w") as myfile:
            myfile.write("")
        self.chapter_map = collections.OrderedDict()

    def get_html_content(self, url, encoding='gb18030', headers=headers):
        now = time.strftime("%H:%M:%S", time.localtime())
        self.log("下载： " + url+" " + str(now))

        r = requests.get(url, headers, timeout=30)
        r.encoding = encoding
        html_text = r.text
        self.log(html_text)
        # html_text = str(html, encoding = "gbk")
        return html_text

    def get_lastest_urls(self, catalogUrl , catalog_pattern):
        html = self.get_html_content(catalogUrl)

        pattern = re.compile(catalog_pattern)
        matchs = pattern.finditer(html)
        for m in matchs:
            title = str(m.group(2))
            url = str(m.group(1))
            self.log(title + " = " + url)
            #print(title + " = " + url)
            self.chapter_map[url] = str(title)

        return self.chapter_map

    def get_chapter_content(self, chapterUrl, attrsFilters, excludeTags=[]):
        html = self.get_html_content(chapterUrl)
        soup =  BeautifulSoup(html,'lxml')
        novelBody = soup.find(attrs=attrsFilters)
        if (novelBody==None):
            return ""

        for tagName in excludeTags:
            for tag in novelBody.find_all(re.compile(tagName)):
                #print(tag.name)
                tag.extract()

        novelText = novelBody.get_text("\n")
        return novelText.replace('\n\n\n', '')

    def __write_file(self, path, text, encoding="gb18030"):
        with open(path, "a") as myfile:
            myfile.write(text.encode('gbk', 'ignore').decode('gbk'))
            
    def log(self, log_content):
        self.__write_file("debug.log", '\n#######################################\n#######################################\n' + log_content)
        
    def download(self, novel):
        basePath = ".\\"

        print(novel)
        if (novel['download']==True):
            url = novel['url']
            catalog_pattern = novel['catalogPattern']
            attrsFilters = novel['attrsFilters']
            excludeTags = novel['excludeTags']

            print("》》》获取【"+ novel['name'] + "】的章节：")
            self.chapter_map = self.get_lastest_urls(url , catalog_pattern)
            path = basePath+ novel['name'] + ".txt"
            with open(path, "w") as myfile:
                myfile.write('')
            for (chUrl, chName) in self.chapter_map.items():
                print("Download: " + chName)
                try:
                    novelText = self.get_chapter_content(chUrl, attrsFilters, ['^h4'])
                    self.chapter_map[chUrl] = novelText
                except Exception:
                    self.chapter_map[chUrl] = Picker.FAILED

            self.__retry_failed_chapters(attrsFilters)
            self.__write_file(path, "\n".join(self.chapter_map.values()))

    def __retry_failed_chapters(self, attrsFilters):
        for i in range(Picker.retry_num):
            failed_chapter_urls = [chUrl for (chUrl, chName) in self.chapter_map.items() if chName==Picker.FAILED]
            if not failed_chapter_urls:
                return
            for chUrl in failed_chapter_urls:
                print("retry:")
                try:
                    novelText = self.get_chapter_content(chUrl, attrsFilters, ['^h4'])
                    self.chapter_map[chUrl] = novelText
                except Exception:
                    self.chapter_map[chUrl] = Picker.FAILED

def test_download_single_chapter():
    picker = Picker()
    novelText = picker.get_chapter_content("http://www.hanxiangxiaoshuo.com/book/2543.html", headers, {"id":"BookText"}, ['^h4'])
    print(novelText)
    path = "d:\\novel.txt"
    with open(path, "a") as myfile:
        myfile.write(novelText.encode('gbk', 'ignore').decode('gbk'))


novel_list = [
    {
        'name':'yl',
        'url':'https://www.va-etong.com/xs/44126/',
        'catalogPattern': '<li>\s*<a href="([^"\']+?)">(.+?)</a>\s*</li>',
        'prefix':'https://www.va-etong.com/xs/44126/',
        #'attrsFilters': {"id":"content"},
        'attrsFilters': {"class":"txt", "id":"txt"},
        'excludeTags':['^h4'],
        'download':True
    },
    #{
    #    'name':'novel',
    #    'url':'http://www.5xxs.org/mulu.asp?id=27586',
    #    'prefix':'http://www.5xxs.org/page.asp?id=2701',
    #    'attrsFilters': {"class":"mview"},
    #    'excludeTags':['^h4'],
    #    'download':False
    #}
]

# picker = Picker()
# for novel in novel_list:
#     picker.download(novel)
