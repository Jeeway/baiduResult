#!/usr/bin/env python
# coding=utf-8
# code by 92ez.com

from threading import Thread
import requests
import sqlite3
import Queue
import sys
import re

reload(sys)
sys.setdefaultencoding('utf8')

#main function
def bThread(domainList):
    threadl = []
    queue = Queue.Queue()
    for domain in domainList:
        queue.put(domain)
    for x in xrange(0, 50):
        threadl.append(tThread(queue))
    for t in threadl:
        try:
            t.daemon = True
            t.start()
        except:
            pass
    for t in threadl:
        t.join()

#create thread
class tThread(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while not self.queue.empty():
            domain = self.queue.get()
            try:
                getIPbyDomain(domain)
            except Exception,e:
                continue

def getUrls():
	titles = []
	oldlinks = []
	try:
		for page in range(0,MAXPAGE):
			thisPageUrl = "https://www.baidu.com/s?wd=" + KEYWORDS +'&pn='+str(page*10)
			req = requests.get(url = thisPageUrl,headers = HEADERS)
			htmlpage = req.content.replace('\n','').replace('\t','')
			titlesStr = re.findall(r'<h3 class="t">(.*?)</h3>',htmlpage)

			for tit in titlesStr:
				tmpstr = tit.replace('<em>','').replace('</em>','').replace(' ','')
				titles.append(re.findall(r'blank">(.*?)</a>',tmpstr)[0])
				oldlinks.append(re.findall(r'href="(.*?)"target',tmpstr)[0])

		return titles,oldlinks
	except Exception,e:
		print e

def getIPbyDomain(domain):
	try:
		tmpresult = requests.get('http://ip138.com/ips1388.asp?ip='+domain+'&action=2').content
		tempip = re.findall(r'<font color="blue">(.*?)</font>',tmpresult)[0].split('>> ')[1]
		print tempip
		IPS.append(tempip)
	except Exception,e:
		print e

def saveToDB(titleArr,realLinks,ips):
	try:
		cx = sqlite3.connect(sys.path[0]+"/baidu.db")
		cx.text_factory = str
		cu = cx.cursor()
		for item in titleArr:
			thisIndex = titleArr.index(item)
			thisTitle = item
			thisDomain = realLinks[thisIndex]
			thisIP = ips[thisIndex]

			cu.execute("select * from search where domain='%s'" % (thisDomain))
			if not cu.fetchone():
				cu.execute("insert into search (title,domain,ip) values (?,?,?)", (thisTitle,thisDomain,thisIP))
				cx.commit()
				print '[√] Found ' +thisTitle +' => Insert successly!'
			else:
				print '[x] Found ' +thisTitle +' <= Found in database!'
		cu.close()
		cx.close()
	except Exception, e:
		print e

if __name__ == '__main__':

	global KEYWORDS
	global MAXPAGE
	global HEADERS
	global IPS

	KEYWORDS = sys.argv[1];
	MAXPAGE = int(sys.argv[2])
	HEADERS = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"}
	IPS = []
	realLinks = []
	
	print '[*] 当前设置获取前'+ str(MAXPAGE*10) +'个结果'
	print '[*] 提取结果页标题和百度原始链接...'
	titleArr,oldinkArr = getUrls()
	print '[√] 提取到'+ str(len(titleArr)) +'个标题和原始链接'

	print '[*] 开始提取真实链接...'
	for link in oldinkArr:
		tmpHeaders = requests.head(link).headers
		tmplink = tmpHeaders['Location'].split('http://')[1].split('/')[0]
		realLinks.append(tmplink)
		print '提取 '+tmplink+' 完成'
	print '[√] 提取真实链接完成'

	print '[*] 根据域名反查IP...'
	bThread(realLinks)
	saveToDB(titleArr,realLinks,IPS)
