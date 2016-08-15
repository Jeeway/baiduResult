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
		IPS.append(tempip)
		print '[*] 域名: '+domain+' --> '+tempip
	except Exception,e:
		IPS.append('null')

def saveToDB(titleArr,realDomains,realLinks,ips):
	try:
		cx = sqlite3.connect(sys.path[0]+"/baidu.db")
		cx.text_factory = str
		cu = cx.cursor()
		for item in titleArr:
			thisIndex = titleArr.index(item)
			thisTitle = item
			thisDomain = realDomains[thisIndex]
			thisIP = ips[thisIndex]
			thisURL = realLinks[thisIndex]

			if thisIP != 'null':
				cu.execute("select * from search where domain='%s' and ip='%s'" % (thisDomain,thisIP))
				if not cu.fetchone():
					cu.execute("insert into search (title,domain,url,ip) values (?,?,?,?)", (thisTitle,thisDomain,thisURL,thisIP))
					cx.commit()
					print '[√] Found ' +thisTitle +' => Insert successly!'
				else:
					print '[x] Found ' +thisTitle +' <= Found in database!'
			else:
				print '[x] Pass ' +thisTitle +' <= IP is null!'
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
	HEADERS = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"}
	IPS = []
	realDomains = []
	realLinks = []
	
	print '[*] 当前设置获取前'+ str(MAXPAGE*10) +'个结果'
	print '[*] 获取结果页标题和百度原始链接...'
	titleArr,oldinkArr = getUrls()
	print '[√] 获取到'+ str(len(titleArr)) +'个标题和原始链接'

	print '[*] 开始提取真实链接...'
	for link in oldinkArr:
		thisHeaders = requests.head(link,timeout = 5).headers
		thisdomain = thisHeaders['Location'].split('://')[1].split('/')[0]
		thisRealUrl = thisHeaders['Location'].split('://')[0] + '://' +thisHeaders['Location'].split('://')[1]
		realDomains.append(thisdomain)
		realLinks.append(thisRealUrl)
		print '[*] 域名:'+thisdomain+' --> '+thisRealUrl
	print '[√] 提取真实链接完成'

	print '[*] 根据域名反查IP...'
	bThread(realDomains)

	print '[*] 存储到数据库..'
	saveToDB(titleArr,realDomains,realLinks,IPS)
