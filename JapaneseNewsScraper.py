################################################
# Written by: William N Kentris
# Description: This script is designed to scrape various Japanese News Websites and store the contents of their articles 
# in a database (including but not limited to Title, Publication Datetime, Body). 

############# Libraries ########################
import urllib.request, re, sqlite3, datetime, traceback, logging, time, os
import JapaneseNewsScraperParser as parser, JapaneseNewsScraperValidation as valid
from JapaneseNewsArticle import newsArticle
# from JapaneseNewsScraperConstants import *
import JapaneseNewsScraperConstants as constants 
from datetime import date, datetime
from bs4 import BeautifulSoup

# Dictionaries for our various functions based on the news source
# PARSE_PUBDATE = {NHK_SOURCE: parser.parseNhkPubDate, ASAHI_SOURCE: parser.parseAsahiPubDate}
# GET_NEWS_ARTICLE_BODY = {NHK_SOURCE: parser.getNhkNewsArticleBody, ASAHI_SOURCE: parser.getAsahiNewsArticleBody}
# GET_IMG_URL = {NHK_SOURCE: parser.getNhkImgUrl, ASAHI_SOURCE: parser.getAsahiImgUrl}
# GET_RSS_ARTICLES = {NHK_SOURCE: parser.getNhkRssArticles, ASAHI_SOURCE: parser.getAsahiRssArticles}

#** Contains reference to CONSTANTs		
def scrapeNews():
	""" Main function of the JapaneseNewsScraper. 

	Starts logging, establishes database connection, gets news articles form website sources, commits new articles to the database, and then closes the database.	"""
	startLogger()
	conn, db = createDbConnection(constants.DATABASE_NAME, constants.CREATE_TABLE)
	newsArticles = getNewsArticles( db, constants.URL_GENRE_SOURCE )
	processNewsArticles(conn, db, newsArticles)
	closeDbConnection(db)

#** Contains reference to CONSTANTs
def startLogger():
	"""	Starts the logging of the JapaneseNewsScraper. 

	Creates new text log file based off of the current timestamp. Stores log file in the corresponding Log folder of the application. Sets the writing mode to debugging.	"""
	ts = time.time()
	currentTs = datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
	if not os.path.exists(constants.LOG_DIRECTORY):
		os.makedirs(constants.LOG_DIRECTORY)
	fileName = "Logs/JapaneseNewsScraper_" + currentTs + ".log" 
	logging.basicConfig(filename=fileName, filemode = 'w', level=logging.DEBUG)
	logging.debug("Logging initiated for JapaneseNewsScraper.")
	
def createDbConnection(database, sqlCreateTable):
	"""  Establishes a database connection to our Japanese News Database. """
	logging.debug("Entering createDbConnection()...")
	print("Starting database connection...")
	conn = sqlite3.connect(database)
	db = conn.cursor()
	db.execute(sqlCreateTable)
	print("Database connection established.\n")
	logging.debug("Exiting createDbConnection().")
	return (conn, db)
	
def getNewsArticles(db, urlGenreSource):
	"""	Retrieves all News Articles for the specified News Source URLs.

	Using the provided list of URLs, Genres, and Sources, a list of new News Articles is retrieved.	"""

	logging.debug("Entering getNewsArticles()...")
	newsArticles = []
	for (url, genre, source) in urlGenreSource:
		newNewsArticles = getNewNewsArticles(db, url, genre, source)
		newsArticles.extend(newNewsArticles)
	logging.debug("Retrieved a total of %d news articles. Exiting getNewsArticles()." % len(newsArticles))
	print("Retrieved a total of %d news articles." % len(newsArticles))
	return newsArticles

def getNewNewsArticles(db, url, genre, source):
	""" Retrieves all New News Articles for the specified News Source URL.
	
	Using the provided URL, Genre, and Source, a list of new News Articles is retrieved.  Copies in the database are removed by checking against the database. This is to remove excessive page requests to the website. """

	logging.debug("Entering getNewNewsArticles(). Retrieving Source: " + source + ", URL: " + url + " articles...")
	print("Retrieving Source: " + source + ", URL: " + url + " articles...")
	page = getUrlPage(url)		
	articles = getPageArticles(page, source)
	newsArticles = processPageArticles(db, articles, genre, source)
	print("Retrieval complete. %d %s article(s) to process.\n" % (len(newsArticles), source))
	logging.debug("Exiting getNewNewsArticles(). Retrieval complete. %d %s article(s) to process.\n" % (len(newsArticles), source))
	return newsArticles

def getUrlPage(url):
	""" Returns a BeautifulSoup page of the specified URL. 	"""
	page = []
	try:
		response = urllib.request.urlopen(url)
		pageText = str(response.read(), 'UTF-8')
		page = BeautifulSoup(pageText)
	except urllib.error.URLError:
		# Add logging later - output to text file
		print("Unable to read URL: " + url)
		logging.debug("Unable to read URL: " + url)
	return page

def getPageArticles(page, source):
	""" Returns list of articles from specified source and RSS feed. """
	items = page.findAll('item') # <- This might need abstracted for websites other than Asahi and NHK
	getRssArticles = getattr(parser, "get" + source.title() + "RssArticles")
	# articles = GET_RSS_ARTICLES[source](items)
	articles = getRssArticles(items)
	return articles

def processPageArticles(db, articles, genre, source):
	""" Removes potentially new News Articles that are already in the database. This is to limit which pages we request to process the News Article Body	"""
	newsArticles = []
	for article in articles:
		if notInDatabase(article, db):
			newsArticles.append( updatePageArticle(article, genre, source) )
	return newsArticles

#** Contains reference to CONSTANTS
def notInDatabase(article, db):
	""" Checks for the existence of current News Article in the database. 	"""
	db.execute(constants.CHECK_FOR_ARTICLE, article.getCheckTuple())
	matches = db.fetchall()
	return not matches

def updatePageArticle(article, genre, source):
	""" Add the Genre and Source to a newly processed News Article. 	"""
	article.setGenre(genre)
	article.setSource(source)
	return article

def processNewsArticles(conn, db, newsArticles):
	""" Retrieves the News Articles bodies, and attempts to commit to the database. Keeps track of successes and failures.	"""
	successHits, failureHits, totalProcessed = 0, 0, 0
	for newsArticle in newsArticles:
		(successHits, failureHits, totalProcessed) = processNewsArticle(conn, db, newsArticle, successHits, failureHits, totalProcessed)
		print("Processed %d of %d articles..." % (totalProcessed, len(newsArticles)))
	print("Finished processing News articles. There were %d successful commit(s) and %d failure(s).\n" % (successHits, failureHits))
	logging.debug("Finished processing News articles. There were %d successful commit(s) and %d failure(s).\n" % (successHits, failureHits))

def processNewsArticle(conn, db, newsArticle, successHits, failureHits, totalProcessed):
	""" Retrieves the News Article body, and attempts to commit to the database. Keeps track of successes and failures. """
	logging.debug("Entering processNewsArticle()...")
	totalProcessed += 1
	try: 
		newsArticle.setBody( getNewsArticleBody(newsArticle) )
		# newsArticle.setImgUrl( getNewsArticleImgUrl(newsArticle) ) <- We'll improve this later; not imprtant now.
		if newsArticle.getBody() == "":
			failureHits += 1
			logging.debug("Failed to process the Article Body.")
			print("Failed to process the Article Body.")
		else:
			db.execute(constants.INSERT_ARTICLE, newsArticle.getInsertTuple())
			conn.commit()
			successHits += 1
	# Need to update logging; cannot store Japanese characters at the moment.
	# Try just putting in the URL for now?
	except sqlite3.IntegrityError:
		logging.debug("Article already exists in database.")
		print("Article already exists in database: "+ str(newsArticle))
		failureHits += 1
	except urllib.error.HTTPError:
		logging.debug("Failed to retrieve page for article.")
		print("Failed to retrieve page for article: "+ str(newsArticle))
		failureHits += 1
	except Exception:
		logging.debug("Uncaught error occurred.")
		print("Uncaught error occurred: " + str(newsArticle))
		print(traceback.format_exc())
		failureHits += 1
	return (successHits, failureHits, totalProcessed)
	
def getNewsArticleBody(newsArticle):
	""" Retrieves the News Article body from the News Article's URL.	"""
	page = getUrlPage(newsArticle.getUrl())
	body = ""
	retrieveNewsArticleBody = getattr(parser, "get" + newsArticle.getSource().title() + "NewsArticleBody")
	# body = GET_NEWS_ARTICLE_BODY[newsArticle.getSource()](page)
	body = retrieveNewsArticleBody(page)
	return body	
	
def getNewsArticleImgUrl(newsArticle):
	page = getUrlPage(newsArticle.getUrl())
	imgUrl = ""
	imgUrl = GET_IMG_URL[newsArticle.getSource()](page, newsArticle) # <- Need to update from pageText to page in further function calls
	return imgUrl	
	
def closeDbConnection(db):
	""" Closes the database connection.  """
	logging.debug("Closing database connections...")
	print("Closing database connections...")
	db.close()
	logging.debug("Database closed. Exiting program.\n")
	print("Database closed. Exiting program.\n")
	


###################################################  
# Beginning of the program
###################################################  
if __name__ == '__main__':
	scrapeNews()
