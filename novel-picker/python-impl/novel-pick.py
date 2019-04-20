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
    #soup =  BeautifulSoup(html,'lxml')
    soup =  BeautifulSoup(html,'html.parser')

    for link in soup.find_all('a'):
        href = link.get('href')
        if href==None or href.strip()=='':
            continue
        if href.find("javascript")>-1 or href.startswith("#"):
            continue

        # e.g. /2546/89898.html, �Ӹ�·����ʼ
        print(href)
        if href[0]=='/':
            href = siteUrl + href
        elif not href.startswith("http"):	# // e.g. 2546/89898.html, �ӵ�ǰҳ����Կ�ʼ
            href = siteUrl + subUrl[0:subUrl.rindex('/')] + "/" + href;
			
        if not href.startswith(urlPrefix) or href.strip()==urlPrefix.strip():
            continue;

        emap[link.string] = href
        
    return emap

def pickChapter(chapterUrl, headers, attrsFilters, excludeTags=[]):
    html = getHtml(chapterUrl, headers)
    soup =  BeautifulSoup(html,'lxml')
    ({"data-foo": "value"})
    
    novelBody = soup.find(attrs=attrsFilters)
    if (novelBody==None):
        return ""
    
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
        print(novel)
        if (novel['download']==True):
            url = novel['url']
            urlPrefix = novel['prefix']
            attrsFilters = novel['attrsFilters']
            excludeTags = novel['excludeTags']

            print("��������ȡ��"+ novel['name'] + "�����½ڣ�")
            chapters = getChapters(url , urlPrefix, headers)
            path = basePath+ novel['name'] + ".txt"
            with open(path, "w") as myfile:
                myfile.write('')
            for (chName, chUrl) in chapters.items():
                #print("Download: " + chName)
                print(chUrl)
                novelText = pickChapter(chUrl, headers, attrsFilters, ['^h4'])
                novelText = novelText.replace('\n\n\n', '')
                saveTxt(path , novelText)

def main1():
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    novelText = pickChapter("http://www.hanxiangxiaoshuo.com/book/2543.html", headers, {"id":"BookText"}, ['^h4'])
    print(novelText)
    path = "d:\\novel.txt"
    with open(path, "a") as myfile:
        myfile.write(novelText.encode('gbk', 'ignore').decode('gbk'))


novel_list = [
    {
        'name':'��Ұ����',
        'url':'http://www.lfs025.com/xyycha/',
        'prefix':'http://www.lfs025.com/xyycha/',
        #'attrsFilters': {"id":"BookText"},
        'attrsFilters': {"class":"content"},
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
main(novel_list)