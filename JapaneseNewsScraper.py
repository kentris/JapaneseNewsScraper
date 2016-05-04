################################################
# Written by: William N Kentris
# Description: This script is designed to scrape various Japanese News Websites and store the contents of their articles 
# in a database (including but not limited to Title, Publication Datetime, Body). 

############# Libraries ########################
import urllib.request, re, sqlite3, datetime, traceback, logging, time, os
import JapaneseNewsScraperParser as parser, JapaneseNewsScraperValidation as valid
from JapaneseNewsArticle import newsArticle
import JapaneseNewsScraperConstants as constants 
from datetime import date, datetime
from bs4 import BeautifulSoup

def scrapeNews():
	""" Main function of the JapaneseNewsScraper. Starts logging, establishes database connection, gets news articles form website sources, commits new articles to the database, and then closes the database.	"""

	startLogger()
	conn, db = createDbConnection(constants.DATABASE_NAME, constants.CREATE_TABLE)
	newsArticles = getNewsArticles( db, constants.URL_GENRE_SOURCE )
	processNewsArticles(conn, db, newsArticles)
	closeDbConnection(db)

def startLogger():
	"""	Starts the logging of the JapaneseNewsScraper. Creates new text log file based off of the current timestamp. Stores log file in the corresponding Log folder of the application. Sets the writing mode to debugging.	"""

	currentTs = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
	if not os.path.exists(constants.LOG_DIRECTORY):
		os.makedirs(constants.LOG_DIRECTORY)
	fileName = "Logs/JapaneseNewsWebScraper_" + currentTs + ".log" 
	global logging
	logging = open(fileName, 'w', encoding='UTF-8')
	logAndPrintMessage("Logging initiated for JapaneseNewsWebScraper.")

def logAndPrintMessage(message):
	logging.write(getCurrentTimestamp() + message + '\n')
	print(getCurrentTimestamp() + message)
	
def getCurrentTimestamp():
	return datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S ')		

def createDbConnection(database, sqlCreateTable):
	"""  Establishes a database connection to our Japanese News Database. """

	logAndPrintMessage("Entering createDbConnection()...")
	conn = sqlite3.connect(database)
	db = conn.cursor()
	db.execute(sqlCreateTable)
	logAndPrintMessage("Succesfully created database connection. Exiting createDbConnection().")
	return (conn, db)
	
def getNewsArticles(db, urlGenreSource):
	"""	Retrieves all News Articles for the specified News Source URLs. Using the provided list of URLs, Genres, and Sources, a list of new News Articles is retrieved.	"""

	logAndPrintMessage("Entering getNewsArticles()...")
	newsArticles = []
	for (url, genre, source) in urlGenreSource:
		try:
			newNewsArticles = getNewRssArticles(db, url, genre, source)
			newsArticles.extend(newNewsArticles)
		except Exception as e:
			print(e)
	logAndPrintMessage("Retrieved a total of %d news articles. Exiting getNewsArticles()." % len(newsArticles))
	return set(newsArticles) # This didn't work; need another method to de-dup the list. Maybe do some list comprehension.

def getNewRssArticles(db, url, genre, source):
	""" Retrieves all New News Articles for the specified News Source URL. 	Using the provided URL, Genre, and Source, a list of new News Articles is retrieved.  Copies in the database are removed by checking against the database. This is to remove excessive page requests to the website. """

	logAndPrintMessage("Entering getNewRssArticles(). Retrieving Source: " + source + ", Genre: " + genre)
	page = getUrlPage(url)		
	getRssArticles = getattr(parser, "get" + source.title() + "RssArticles")
	articles = getRssArticles(page)
	newsArticles = processRssArticles(db, articles, genre, source)
	logAndPrintMessage("Retrieval complete. %d article(s) to process. Exiting getNewRssArticles()." % (len(newsArticles)))
	return newsArticles

def getUrlPage(url):
	""" Returns a BeautifulSoup page of the specified URL. 	"""

	page = BeautifulSoup()
	try:
		response = urllib.request.urlopen(url)
		pageText = str(response.read(), 'UTF-8')
		page = BeautifulSoup(pageText, "lxml")
	except urllib.error.URLError:
		logAndPrintMessage("Unable to read URL: " + url)
	return page

def processRssArticles(db, articles, genre, source):
	""" Removes potentially new News Articles that are already in the database. This is to limit which pages we request to process the News Article Body	"""
	newsArticles = []
	for article in articles:
		if notInDatabase(article, db):
			article.setGenre(genre)
			article.setSource(source)
			newsArticles.append( article )
	return newsArticles

def notInDatabase(article, db):
	""" Checks for the existence of current News Article in the database. 	"""

	db.execute(constants.CHECK_FOR_ARTICLE, article.getCheckTuple())
	matches = db.fetchall()
	return not matches

def processNewsArticles(conn, db, newsArticles):
	""" Retrieves the News Articles bodies, and attempts to commit to the database. Keeps track of successes and failures.	"""

	logAndPrintMessage("Entering processNewsArticles()...")
	processed = {'total':0, 'success':0, 'failure':0}
	for newsArticle in newsArticles:
		processNewsArticle(conn, db, newsArticle, processed)
		logAndPrintMessage("Processed %d of %d articles..." % (processed['total'], len(newsArticles)))
	logAndPrintMessage("Finished processing News articles. There were %d successful commit(s) and %d failure(s). Exiting processNewsArticles()." % (processed['success'], processed['failure']))

def processNewsArticle(conn, db, newsArticle, processed):
	""" Retrieves the News Article body, and attempts to commit to the database. Keeps track of successes and failures. """

	logAndPrintMessage("Entering processNewsArticle() with %s..." % (newsArticle))
	processed['total'] += 1
	try: 
		newsArticle.setBody( getNewsArticleBody(newsArticle) )
		if newsArticle.getBody() == "":
			processed['failure'] += 1
			logAndPrintMessage("Failed to process the Article Body.")
		else:
			db.execute(constants.INSERT_ARTICLE, newsArticle.getInsertTuple())
			conn.commit()
			processed['success'] += 1
	except sqlite3.IntegrityError:
		logAndPrintMessage("Article already exists in database: "+ str(newsArticle))
		processed['failure'] += 1
	except urllib.error.HTTPError:
		logAndPrintMessage("Failed to retrieve page for article: "+ str(newsArticle))
		processed['failure'] += 1
	except Exception:
		logAndPrintMessage("Uncaught error occurred: " + str(newsArticle) +' \n' + traceback.format_exc())
		processed['failure'] += 1
	logAndPrintMessage("Exiting processNewsArticle().")
	
def getNewsArticleBody(newsArticle):
	""" Retrieves the News Article body from the News Article's URL.	"""

	page = getUrlPage(newsArticle.getUrl())
	body = ""
	retrieveNewsArticleBody = getattr(parser, "get" + newsArticle.getSource().title() + "NewsArticleBody")
	body = retrieveNewsArticleBody(page)
	return body	
	
def getNewsArticleImgUrl(newsArticle):
	page = getUrlPage(newsArticle.getUrl())
	imgUrl = ""
	imgUrl = GET_IMG_URL[newsArticle.getSource()](page, newsArticle) # <- Need to update from pageText to page in further function calls
	return imgUrl	
	
def closeDbConnection(db):
	""" Closes the database connection.  """

	logAndPrintMessage("Entering closeDbConnection()...")
	db.close()
	logAndPrintMessage("Database closed. Exiting closeDbConnection().")
	logging.close()
	


###################################################  
# Beginning of the program
###################################################  
if __name__ == '__main__':
	scrapeNews()
