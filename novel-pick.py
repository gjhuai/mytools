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
    # ץȡվ��url
    siteUrl = catalogUrl[:idx]
    # ���ָ�url
    subUrl = catalogUrl[idx:]
    
    #html = html.decode('utf-8')
    html = getHtml(catalogUrl , headers)
    soup =  BeautifulSoup(html,'lxml')

    for link in soup.find_all('a'):
        href = link.get('href')
        if href.find("javascript")>-1:
            continue

        # e.g. /2546/89898.html, �Ӹ�·����ʼ
        if href[0]=='/':
            href = siteUrl + href
        elif not href.startswith("http"):	# // e.g. 2546/89898.html, �ӵ�ǰҳ����Կ�ʼ
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
# "###"���������Ӧ�Ĵ��λ�ã�Ȼ����Ӧ�Ķ���ı��ļ������novel�ļ�����
    chapters = getChapters(url , urlPrefix, headers)

    path = "d:\\novel.txt"
    for (chName, chUrl) in chapters.items():
        novelText = pickChapter(chUrl, headers, "BookText")
        saveTxt(path , novelText)

main()