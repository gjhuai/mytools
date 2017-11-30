# coding=gbk 
import urllib.request, codecs
from bs4 import BeautifulSoup

def getHtml(url, headers):
    req = urllib.request.Request(url = url , headers = headers)
    res = urllib.request.urlopen(req)
    html = res.read()
    return html

def getChapters(catalogUrl , urlPrefix, headers):
    emap = {}
    
    idx = catalogUrl.index("/", catalogUrl.index("//") + 2)
    # 抓取站点url
    siteUrl = catalogUrl[:idx]
    # 文字根url
    subUrl = catalogUrl[idx:]
    
    #html = html.decode('utf-8')
    html = getHtml(catalogUrl , headers)
    soup =  BeautifulSoup(html,'lxml')

    for link in soup.find_all('a'):
        href = link.get('href')
        if href==None:
            continue
        if href.find("javascript")>-1 or href.startswith("#"):
            continue

        # e.g. /2546/89898.html, 从根路径开始
        if href[0]=='/':
            href = siteUrl + href
        elif not href.startswith("http"):	# // e.g. 2546/89898.html, 从当前页面相对开始
            href = siteUrl + subUrl[0:subUrl.rindex('/')] + "/" + href;
			
        if not href.startswith(urlPrefix):
            continue;

        emap[link.string] = href
        
    return emap

def pickChapter(chapterUrl, headers, contentId, excludeTags=[]):
    html = getHtml(chapterUrl, headers)
    soup =  BeautifulSoup(html,'lxml')
    novelBody = soup.find(id=contentId)
    import re
    for tagName in excludeTags:
        for tag in novelBody.find_all(re.compile(tagName)):
            #print(tag.name)
            tag.extract()
    return novelBody.get_text("\n")

def saveTxt(path, text, encoding="gb18030"):
    with open(path, "a") as myfile:
        myfile.write(text.encode('gbk', 'ignore').decode('gbk'))

def main(novel_list):
    basePath = ".\\"
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    for novel in novel_list:
        if (novel['download']==True):
            url = novel['url']
            urlPrefix = novel['prefix']
            contentId = novel['contentId']
            excludeTags = novel['excludeTags']
    
            chapters = getChapters(url , urlPrefix, headers)
            path = basePath+ novel['name'] + ".txt"
            with open(path, "w") as myfile:
                myfile.write('')
            for (chName, chUrl) in chapters.items():
                print("Download: " + chName)
                print(chUrl)
                novelText = pickChapter(chUrl, headers, contentId, ['^h4'])
                novelText = novelText.replace('\n\n\n', '')
                saveTxt(path , novelText)

def main1():
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    novelText = pickChapter("http://www.hanxiangxiaoshuo.com/book/2543.html", headers, "BookText", ['^h4'])
    print(novelText)
    path = "d:\\novel.txt"
    with open(path, "a") as myfile:
        myfile.write(novelText.encode('gbk', 'ignore').decode('gbk'))


novel_list = [
    {
        'name':'汉乡',
        'url':'http://www.hanxiangxiaoshuo.com/hanxiang/',
        'prefix':'http://www.hanxiangxiaoshuo.com/book/',
        'contentId':'BookText',
        'excludeTags':['^h4'],
        'download':False
    },
    {
        'name':'音乐系',
        'url':'http://www.qingfxy.com/modules/article/reader.php?aid=1375',
        'prefix':'http://www.qingfxy.com/modules/article/reader.php?aid=1375',
        'contentId':'chapter_bd_924915',
        'excludeTags':['^h4'],
        'download':True
    }
]
main(novel_list)