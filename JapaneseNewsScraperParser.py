import urllib.request, re, sqlite3, datetime, traceback
from datetime import date
from bs4 import BeautifulSoup
# from JapaneseNewsScraperConstants import *
import JapaneseNewsScraperConstants as constants
from JapaneseNewsArticle import newsArticle

################## getRssArticles() ###########################
def getAsahiRssArticles(page):
	""" Processes the Asahi RSS Page Source into a list of Titles, PubDatetimes, and URLs.
	A list of News Articles is then formed from the list of News Article information.  """
	items = page.findAll('item')
	titlePubdateUrl = getAsahiPageArticleTitlePubdateUrl(items)
	articles = [ newsArticle(title, pubdate, url) \
		for (title, pubdate, url) in titlePubdateUrl ]
	return articles

def getNhkRssArticles(page):
	""" Processes the NHK RSS Page Source into a list of Titles, PubDatetimes, and URLs.
	A list of News Articles is then formed from the list of News Article information.  """
	items = page.findAll('item')
	titlePubdateUrl = getNhkPageArticleTitlePubdateUrl(items)
	articles = [ newsArticle(title, pubdate, url) \
		for (title, pubdate, url) in titlePubdateUrl ]
	return articles	

def getYomiuriRssArticles(page):
	""" Processes the Yomiuri RSS Page Source into a list of Titles, PubDatetimes, and URLs.
	A list of News Articles is then formed from the list of News Article information.  """
	unorderedList = page.findAll('ul', {'class':'list-common'})
	items = []
	if unorderedList:
		items = unorderedList[0].findAll('li')
	titlePubdateUrl = getYomiuriPageArticleTitlePubdateUrl(items)
	articles = [ newsArticle(title, pubdate, url) \
		for (title, pubdate, url) in titlePubdateUrl ]
	return articles	


################# getTitlePubdateUrl() ########################
def getAsahiPageArticleTitlePubdateUrl(items):
	""" Processes the Asahi RSS Page Source list of items into a list of  Titles, PubDatetimes, and URLs for each Asahi News Article. """
	titlePubdateUrl = [ ( (item.find('title').contents[0]), parseAsahiPubDate(item.find('dc:date').contents[0]), (item.find('link').contents[0]) ) for item in items if( (item.find('title') is not None) and (item.find('link') is not None) and (item.find('dc:date') is not None) ) ]
	return titlePubdateUrl

def getNhkPageArticleTitlePubdateUrl(items):
	""" Processes the NHK RSS Page Source list of items into a list of  Titles, PubDatetimes, and URLs for each NHK News Article. """
	titlePubdateUrl = [ ( (item.find('title').contents[0]), parseNhkPubDate(item.find('pubdate').contents[0]), (item.find('guid').contents[0]) ) for item in items if( (item.find('title') is not None) and (item.find('guid') is not None) and (item.find('pubdate') is not None) ) ]
	return titlePubdateUrl

def getYomiuriPageArticleTitlePubdateUrl(items):
	""" Processes the Yomiuri RSS Page Source list of items into a list of  Titles, PubDatetimes, and URLs for each Yomiuri News Article. """
	titlePubdateUrl = [ ( (item.find('span', {'class':'headline'}).contents[0]), parseYomiuriPubDate(item.find('span', {'class':'update'}).contents[0]), (item.find('a')['href']) ) for item in items if( (item.find('span', {'class':'headline'}) is not None) and (item.find('span', {'class':'update'}) is not None) and (item.find('a') is not None) ) ]
	return titlePubdateUrl


################# parsePubDate() #################################
def parseNhkPubDate(pubDatetime):
	""" Processes and returns the database compliant Pub Datetime from the provided NHK Pub Datetime. """
	pubDateTime, year, month, day, hour, minute, second = (None, None, None, None, None, None, None)
	# Split on spaces
	if len(pubDatetime) == constants.NHK_PUB_DATETIME_LENGTH:
		pubInfo = pubDatetime.split(' ')
		if len(pubInfo) == constants.NHK_PUB_INFO_LENGTH:
			# Convert string values to integers
			year, month, day = (int(pubInfo[3]), int(constants.MONTHS[pubInfo[2]]),int(pubInfo[1]))
			hour, minute, second = (int(pubInfo[4][0:2]),int(pubInfo[4][3:5]),int(pubInfo[4][6:8]))
			# Use individual time units to create pubDatetime value
			pubDateTime = datetime.datetime(year, month, day, hour, minute, second)
		else:
			print("Incorrect number of arguments for pubDatetime.")
	else:
		print("Incorrect length for NHK pubDateTime. Expected length of %d, length was %d" % (constants.NHK_PUB_DATETIME_LENGTH, len(pubDatetime)))
		print(pubDatetime)
	return pubDateTime

def parseAsahiPubDate(pubDatetime):
	""" Processes and returns the database compliant Pub Datetime from the provided Asahi Pub Datetime. """
	pubDateTime, year, month, day, hour, minute, second = (None, None, None, None, None, None, None)
	# Split into components
	if len(pubDatetime) == constants.ASAHI_PUB_DATETIME_LENGTH:
		pubInfo = re.split('[T,+]', pubDatetime)
		if len(pubInfo) == constants.ASAHI_PUB_INFO_LENGTH:
			# Convert string values to integers
			year, month, day = ( int(pubInfo[0][0:4]), int(pubInfo[0][5:7]),int(pubInfo[0][8:10]) )
			hour, minute, second = (int(pubInfo[1][0:2]),int(pubInfo[1][3:5]),int(pubInfo[1][6:8]))
			# Use individual time units to create pubDatetime value
			pubDateTime = datetime.datetime(year, month, day, hour, minute, second)
		else:
			print("Incorrect number of arguments for pubDatetime.")
	else:
		print("Incorrect length for Asahi pubDateTime. Expected length of %d, length was %d" % (constants.ASAHI_PUB_DATETIME_LENGTH, len(pubDatetime)) )
		print(pubDatetime)
	return pubDateTime

# Needs further validation here; comparable to previous parsePubDate() functions
def parseYomiuriPubDate(pubDatetime):
	""" Processes and returns the database compliant Pub Datetime from the provided Yomiuri Pub Datetime. """
	#（2015年07月25日）
	pubDateTime, year, month, day, hour, minute, second = (None, None, None, None, None, None, None)
	pubInfo = re.split('\D', pubDatetime)
	year, month, day = (int(pubInfo[1]), int(pubInfo[2]), int(pubInfo[3]))
	pubDateTime = datetime.datetime(year, month, day)
	return pubDateTime


################# getNewsArticleBody() ############################
def getAsahiNewsArticleBody(page):
	""" Processes and returns the Asahi News Article Body from the provided News Article page source. """
	bodyLayout = page.find('div', {"class": "ArticleText"})
	body = ""
	if bodyLayout:
		for p in bodyLayout.findAll('p'):
			if p.contents:
				body+= p.contents[0]
	body = body.replace("\u3000","")
	return body
	
def getNhkNewsArticleBody(page):
	""" Processes and returns the Nhk News Article Body from the provided News Article page source. """
	body = ""
	newsTextBody = page.find("div", {"id":"news_textbody"})
	newsTextMore = page.find("div", {"id": "news_textmore"})
	if newsTextBody and newsTextMore: 
		body = newsTextBody.contents[0] + newsTextMore.contents[0]
	# Need to put in extra handling for <div class = "news_add"
	body = body.replace("<br />", "")
	return body

def getYomiuriNewsArticleBody(page):
	""" Processes and returns the Nhk News Article Body from the provided News Article page source. """
	body = ""
	articleBodies = page.findAll('p', {'itemprop':'articleBody'})
	for articleBody in articleBodies:
		if articleBody.contents:
			body += articleBody.contents[0]
	return body


################# getImgUrl() #####################################
def getAsahiImgUrl(pageText, article):
	imgUrl = ""
	newsImageMatch = re.findall(constants.ASAHI_IMAGE_URL_REGEXP, pageText)
	if newsImageMatch:
		imgUrl = newsImageMatch[0][2]
	return imgUrl
	
def getNhkImgUrl(pageText, article):
	imgUrl = ""
	newsImageMatch = re.findall(constants.NHK_IMAGE_URL_REGEXP, pageText)
	if newsImageMatch:
		baseUrl = article.getUrl().rpartition('/')[0]
		imgUrlExt = newsImageMatch[0][1]
		if not imgUrlExt[0:4] == "http":
			imgUrl = baseUrl + '/' + imgUrlExt
	return imgUrl