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
        if href.find("javascript")>-1:
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

def pickChapter(chapterUrl, headers, contentId):
    html = getHtml(chapterUrl, headers)
    soup =  BeautifulSoup(html,'lxml')
    novelBody = soup.find(id=contentId)
    return novelBody.get_text()

def saveTxt(path, text, encoding="gbk"):
    with codecs.open(path, "w", encoding) as f:
        f.write(text)

def main():
    url="http://www.hanxiangxiaoshuo.com/hanxiang/"
    urlPrefix = "http://www.hanxiangxiaoshuo.com/book/"
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    path = ".\\" 
# "###"代表的是相应的存放位置，然后将相应的多个文本文件存放在novel文件夹中
    chapters = getChapters(url , urlPrefix, headers)

    path = "d:\\novel.txt"
    for (chName, chUrl) in chapters.items():
        novelText = pickChapter(chUrl, headers, "BookText")
        saveTxt(path , novelText)

main()