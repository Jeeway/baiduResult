#!/usr/bin/env python
# coding=utf-8
# code by 92ez.com

from threading import Thread
import requests
import sqlite3
import Queue
import json
import sys
import re

# Console colors
W = '\033[0m'  # white (normal)
R = '\033[31m'  # red
G = '\033[32m'  # green

reload(sys)
sys.setdefaultencoding('utf8')


def getUrls():
    titles = []
    oldlinks = []
    try:
        for page in range(0, MAXPAGE):
            thisPageUrl = "https://www.baidu.com/s?wd=" + KEYWORDS + '&pn=' + str(page * 10)
            print thisPageUrl
            htmlpage = requests.get(url=thisPageUrl, headers=HEADERS).content.replace('\n', '').replace('\t', '')
            titlesStr = re.findall(r'<h3 class="t">(.*?)</h3>', htmlpage)

            for tit in titlesStr:
                try:
                    tmpstr = tit.replace('<em>', '').replace('</em>', '').replace(' ', '')
                    thisTitle = re.findall(r'blank\">(.+?)</a>', tmpstr)[0]
                    thisOldlink = re.findall(r'href=\"(.+?)"target', tmpstr)[0]
                    titles.append(thisTitle)
                    oldlinks.append(thisOldlink)
                except:
                    pass
        return titles, oldlinks
    except Exception, e:
        print e


def clearDB():
    try:
        cx = sqlite3.connect(sys.path[0] + "/baidu.db")
        cx.text_factory = str
        cu = cx.cursor()
        cu.execute("DELETE FROM search")
        cu.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name ='search'")
        cx.commit()
        cu.close()
        cx.close()
    except Exception, e:
        print e


def saveToDB(titleArr, realDomains, realLinks):
    clearDB()
    try:
        cx = sqlite3.connect(sys.path[0] + "/baidu.db")
        cx.text_factory = str
        cu = cx.cursor()
        for item in titleArr:
            thisIndex = titleArr.index(item)
            thisTitle = item
            thisDomain = realDomains[thisIndex]
            thisURL = realLinks[thisIndex]

            cu.execute("select * from search where domain='%s'" % thisDomain)
            if not cu.fetchone():
                cu.execute("INSERT INTO search (title,domain,url) VALUES (?,?,?)", (thisTitle, thisDomain, thisURL))
                cx.commit()
                print G + '[√] Found ' + thisTitle + ' => Insert successly!' + W
            else:
                print R + '[x] Pass ' + thisTitle + ' <= No position!' + W
        cu.close()
        cx.close()
    except Exception, e:
        print e


if __name__ == '__main__':

    global KEYWORDS
    global MAXPAGE
    global HEADERS
    global IPS

    KEYWORDS = sys.argv[2];
    MAXPAGE = int(sys.argv[1])
    HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"}
    IPS = []
    realDomains = []
    realLinks = []

    print '[*] 当前设置获取前' + str(MAXPAGE * 10) + '个结果'
    print '[*] 获取结果页标题和百度原始链接...'
    titleArr, oldinkArr = getUrls()
    print '[√] 获取到' + str(len(titleArr)) + '个标题和原始链接'

    print '[*] 开始提取真实链接...'
    for link in oldinkArr:
        thisHeaders = requests.head(link, timeout=5).headers
        thisdomain = thisHeaders['Location'].split('://')[1].split('/')[0]
        thisRealUrl = thisHeaders['Location'].split('://')[0] + '://' + thisHeaders['Location'].split('://')[1]
        realDomains.append(thisdomain)
        realLinks.append(thisRealUrl)
        print '[*] 域名:' + thisdomain + ' --> ' + thisRealUrl
    print '[√] 提取真实链接完成'
    print '[*] 存储到数据库..'
    saveToDB(titleArr, realDomains, realLinks)
