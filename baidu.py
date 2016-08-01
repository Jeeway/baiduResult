#!/usr/bin/env python
# coding=utf-8
# code by 92ez.com

import requests
import sys
import re

def getResultCount():
	url = "https://www.baidu.com/s?wd=" + KEYWORDS
	try:	
		req = requests.get(url = url,headers = HEADERS)
		htmlpage = req.content.replace('\n','').replace('\t','')
		countResult = re.findall(r'找到相关结果约(.*?)个',htmlpage)[0].replace(',','')
		return countResult
	except Exception,e:
		print e

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

if __name__ == '__main__':

	global KEYWORDS
	global MAXPAGE
	global HEADERS

	KEYWORDS = sys.argv[1];
	MAXPAGE = 5
	HEADERS = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"}

	realLinks = []
	ips = []
	myresult = []
	
	print '[*] 获取结果数...'
	totalCount = getResultCount()

	print '[√] 找到相关结果约'+totalCount+'个'
	print '[*] 当前设置获取前'+ str(MAXPAGE*10) +'个结果'
	print '[*] 提取结果页标题和百度原始链接...'
	titleArr,oldinkArr = getUrls()
	print '[√] 提取到'+ str(len(titleArr)) +'个标题和原始链接'

	print '[*] 开始提取真实链接...'
	for link in oldinkArr:
		tmpHeaders = requests.head(link).headers
		tmplink = tmpHeaders['Location']
		realLinks.append(tmplink)
		print '提取 '+tmplink+' 完成'
	print '[√] 提取真实链接完成'

	print '[*] 根据域名反查IP...'
	for dom in realLinks:
		tmpdom = dom.split('://')[1].split('/')[0]
		tmpresult = requests.get('http://ip138.com/ips1388.asp?ip='+tmpdom+'&action=2').content
		ipres = re.findall(r'<font color="blue">(.*?)</font>',tmpresult)[0]
		print ipres
