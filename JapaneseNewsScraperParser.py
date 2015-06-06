import urllib.request, re, sqlite3, datetime, traceback
from datetime import date
from bs4 import BeautifulSoup
from JapaneseNewsScraperConstants import *

def getAsahiNewsArticleBody(pageText):
	"""
	Get the News Article Body from the Asahi Article Pagesource.
	Input: 
		pageText -- The html pagesource of the Asahi article
	Output: 
		body -- The text of the Asahi article
	"""
	pageLayout = BeautifulSoup(pageText)
	bodyLayout = pageLayout.find('div', {"class": "ArticleText"})
	body = ""
	for p in bodyLayout.findAll('p'):
		if p.contents:
			body+= p.contents[0]
	body = body.replace("\u3000","")
	return body
	
def getNhkNewsArticleBody(pageText):
	"""
	Get the News Article Body from the NHK Article Pagesource.
	Input: 
		pageText -- The html pagesource of the NHK article
	Output: 
		body -- The text of the NHK article
	"""
	textBodyMatch = re.findall(TEXT_BODY_REGEXP, pageText)
	textMoreMatch = re.findall(TEXT_MORE_REGEXP, pageText)
	newsAddMatch = re.findall(NEWS_ADD_REGEXP, pageText)
	# Mock up our body
	body = ""
	if textBodyMatch and textMoreMatch:
		body = textBodyMatch[0][1] + textMoreMatch[0][1]
	if newsAddMatch:
		newsAddBody = newsAddMatch[0][1] + newsAddMatch[0][3]
		body += body + '\n'*2 + newsAddBody
	# Get rid of breakline tags
	body = body.replace("<br />", "")
	return body

def getAsahiImgUrl(pageText, article):
	"""
	Get the News Image URL from the Asahi Article Pagesource, if it exists.
	Input: 
		pageText -- The html pagesource of the Asahi article
		article  -- The processed newsArticle of the pageText. At this point it should have the Title, Pub Datetime, Url, Body, Genre, and Source
	Output: 
		body -- The News Image URL of the pageText, if it exists
	"""
	imgUrl = ""
	newsImageMatch = re.findall(ASAHI_IMAGE_URL_REGEXP, pageText)
	if newsImageMatch:
		imgUrl = newsImageMatch[0][2]
	return imgUrl
	
def getNhkImgUrl(pageText, article):
	"""
	Get the News Image URL from the NHK Article Pagesource, if it exists.
	Input: 
		pageText -- The html pagesource of the NHK article
		article  -- The processed newsArticle of the pageText. At this point it should have the Title, Pub Datetime, Url, Body, Genre, and Source
	Output: 
		body -- The News Image URL of the pageText, if it exists
	"""
	imgUrl = ""
	newsImageMatch = re.findall(NHK_IMAGE_URL_REGEXP, pageText)
	if newsImageMatch:
		baseUrl = article.getUrl().rpartition('/')[0]
		imgUrlExt = newsImageMatch[0][1]
		# Only want valid the imgUrls, not any news image
		if not imgUrlExt[0:4] == "http":
			imgUrl = baseUrl + '/' + imgUrlExt
	return imgUrl
	
def parseNhkPubDate(pubDatetime):
	"""
	Takes the provided NHK datetime and converts it to the python datetime.
	Input: 
		NHK pubDatetime value, e.g. "Thu, 02 Apr 2015 06:10:11 +0900"
	Output: 
		SQLite datetime value 
	"""
	pubDateTime, year, month, day, hour, minute, second = (None, None, None, None, None, None, None)
	# Split on spaces
	if len(pubDatetime) == NHK_PUB_DATETIME_LENGTH:
		pubInfo = pubDatetime.split(' ')
		if len(pubInfo) == NHK_PUB_INFO_LENGTH:
			# Convert string values to integers
			year, month, day = (int(pubInfo[3]), int(MONTHS[pubInfo[2]]),int(pubInfo[1]))
			hour, minute, second = (int(pubInfo[4][0:2]),int(pubInfo[4][3:5]),int(pubInfo[4][6:8]))
			# Use individual time units to create pubDatetime value
			pubDateTime = datetime.datetime(year, month, day, hour, minute, second)
		else:
			print("Incorrect number of arguments for pubDatetime.")
	else:
		print("Incorrect length for pubDateTime.")
	return pubDateTime

def parseAsahiPubDate(pubDatetime):
	"""
	Takes the provided Asahi datetime and converts it to the python datetime.
	Input: 
		Asahi pubDatetime value, e.g. "2015-06-01T00:05:28+09:00"
	Output: 
		SQLite datetime value 
	"""
	pubDateTime, year, month, day, hour, minute, second = (None, None, None, None, None, None, None)
	# Split into components
	if len(pubDatetime) == ASAHI_PUB_DATETIME_LENGTH:
		pubInfo = re.split('[T,+]', pubDatetime)
		if len(pubInfo) == ASAHI_PUB_INFO_LENGTH:
			# Convert string values to integers
			year, month, day = ( int(pubInfo[0][0:4]), int(pubInfo[0][5:7]),int(pubInfo[0][8:10]) )
			hour, minute, second = (int(pubInfo[1][0:2]),int(pubInfo[1][3:5]),int(pubInfo[1][6:8]))
			# Use individual time units to create pubDatetime value
			pubDateTime = datetime.datetime(year, month, day, hour, minute, second)
		else:
			print("Incorrect number of arguments for pubDatetime.")
	else:
		print("Incorrect length for pubDateTime.")
	return pubDateTime
