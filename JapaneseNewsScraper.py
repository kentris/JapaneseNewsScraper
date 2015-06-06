################################################
# Written by: William N Kentris
# Description: This script is designed to scrape various Japanese News Websites and store the contents of their articles in a database (including but not limited to Title, Publication Datetime, Body). 

############# Libraries ########################
import urllib.request, re, sqlite3, datetime, traceback, logging, time
import JapaneseNewsScraperParser as parser, JapaneseNewsScraperValidation as valid
from JapaneseNewsArticle import newsArticle
from JapaneseNewsScraperConstants import *
from datetime import date, datetime
from bs4 import BeautifulSoup

# Dictionaries for our various functions based on the news source
PARSE_PUBDATE = {NHK_SOURCE: parser.parseNhkPubDate, ASAHI_SOURCE: parser.parseAsahiPubDate}
PARSE_BODY = {NHK_SOURCE: parser.getNhkNewsArticleBody, ASAHI_SOURCE: parser.getAsahiNewsArticleBody}
PARSE_IMG_URL = {NHK_SOURCE: parser.getNhkImgUrl, ASAHI_SOURCE: parser.getAsahiImgUrl}
		
def scrapeNews():
	"""Our main function for scraping/parsing news articles"""
	startLogger()
	
	# Start connection to DB
	conn, db = createDbConnection(DATABASE_NAME, CREATE_TABLE)
	
	newsArticles = []
	# Retrieve NHK articles (w/ title, url, pubDatetime, source, genre)
	nhkNewsArticles = getNewsArticles(db, NHK_URL, NHK_GENRE, NHK_SOURCE, NHK_TAG)
	newsArticles.extend(nhkNewsArticles)
	
	# Retrieve Asahi articles (w/ title, url, pubDatetime, source, genre)
	asahiNewsArticles = getNewsArticles(db, ASAHI_URL, ASAHI_GENRE, ASAHI_SOURCE, ASAHI_TAG)
	newsArticles.extend(asahiNewsArticles)
	
	# Get remaining info for Articles, body and imgUrl if exists
	processNewsArticles(conn, db, newsArticles)
	
	closeDbConnection(db)

def startLogger():
	ts = time.time()
	currentTs = datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
	fileName = "JapaneseWebScraper_" + currentTs + ".log" 
	logging.basicConfig(filename=fileName, filemode = 'w', level=logging.DEBUG)
	logging.debug("Logging initiated for JapaneseNewsScraper.")
	
def createDbConnection(database, sqlCreateTable):
	"""
	Creates our database connection.
	"""
	logging.debug("Entering createDbConnection()...")
	print("Starting database connection...")
	conn = sqlite3.connect(database)
	db = conn.cursor()
	# Create DB if not yet instantiated
	db.execute(sqlCreateTable)
	print("Database connection established.\n")
	return (conn, db)
	
def getNewsArticles(db, urls, genres, source, tags):
	"""# Parameters: db: Sqlite3 database cursor, urls: list of XML urls, genres: list of news genres, source: the news source
	# Output: list of newsArticles (w/ Title, URL, PubDatetime)"""
	logging.debug("Entering getNewsArticles()...")
	print("Retrieving " + source + " Article URLs...")
	# Store articles in this list
	newsArticles = []
	# Iterate through each page of articles in provided list
	for i in range(0, len(urls)):
		try: 
			# Attempt to get the page source as a string
			response = urllib.request.urlopen(urls[i])
			pageText = str(response.read(), 'UTF-8')
			# Match for article items with bs4
			pageLayout = BeautifulSoup(pageText)
			items = pageLayout.findAll('item')
			# Use BeautifulSoup to parse the XML layout
			articles = [newsArticle(item.find(tags['title']).contents[0], PARSE_PUBDATE[source](item.find(tags['pubdate']).contents[0]), item.find(tags['url']).contents[0]) for item in items if((item.find(tags['title']) is not None) and (item.find(tags['url']) is not None) and (item.find(tags['pubdate']) is not None))]
			# Check if article is already in the database, add it to returned list if not present
			for a in articles:
				db.execute(CHECK_FOR_ARTICLE, a.getCheckTuple())
				results = db.fetchall()
				# If the article is not in the database, then we will want to process it
				if not results:
					a.setGenre(genres[i])
					a.setSource(source)
					newsArticles.append(a)
					
		# Catch exception if unable to read URL
		except urllib.error.URLError:
			# Add logging later - output to text file
			print("Unable to read URL")
	print("Retrieval complete. %d %s article(s) to process.\n" % (len(newsArticles), source))
	logging.debug("Retrieval complete. %d %s article(s) to process.\n" % (len(newsArticles), source))
	return newsArticles
	
def processNewsArticles(conn, db, newsArticles):
	logging.debug("Entering processNewsArticles()...")
	logging.debug("Retrieved a total of %d news articles." % len(newsArticles))
	print("Retrieved a total of %d news articles." % len(newsArticles))
	print("Processing individual news article URLs...")
	successHits = 0
	failureHits = 0
	totalProcessed = 0
	for article in newsArticles:
		totalProcessed += 1
		try: 
			body = getNewsArticleBody(article)
			article.setBody(body)
			imgUrl = getNewsArticleImgUrl(article)
			article.setImgUrl(imgUrl)
			db.execute(INSERT_ARTICLE, article.getInsertTuple())
			conn.commit()
			successHits += 1
			print("Processed %d of %d articles..." % (totalProcessed, len(newsArticles)))
		except sqlite3.IntegrityError:
			print("Article already exists in database: "+ str(article))
			failureHits += 1
		except urllib.error.HTTPError:
			print("Failed to retrieve page for article: "+ str(article))
			failureHits += 1
		except Exception:
			print("Uncaught error occurred: " + str(article))
			print(traceback.format_exc())
			failureHits += 1
	print("Finished processing News articles. There were %d successful commit(s) and %d failure(s).\n" % (successHits, failureHits))
	logging.debug("Finished processing News articles. There were %d successful commit(s) and %d failure(s).\n" % (successHits, failureHits))
	
def getNewsArticleBody(article):
	"""# Parameters: A news article w/o the body
	# Output: The news article body"""
	response = urllib.request.urlopen(article.getUrl())
	pageText = str(response.read(), 'UTF-8')
	body = ""
	try:
		body = PARSE_BODY[article.getSource()](pageText)
	except:
		print("Unable to parse body: " + str(article))
		logging.debug("Unable to parse body: " + str(article))
	return body	
	
def getNewsArticleImgUrl(article):
	"""
	# Parameters: news article
	# Output: imgUrl of news article if it exists"""
	response = urllib.request.urlopen(article.getUrl())
	pageText = str(response.read(), 'UTF-8')
	imgUrl = ""
	try:
		imgUrl = PARSE_IMG_URL[article.getSource()](pageText, article)
	except:
		print("Unable to parse imgUrl: " + str(article))
		logging.debug("Unable to parse imgUrl: " + str(article))
	return imgUrl	
	
def closeDbConnection(db):
	logging.debug("Closing database connections...")
	print("Closing database connections...")
	db.close()
	print("Database closed. Exiting program.\n")
	
###################################################  
# Beginning of the program
###################################################  
if __name__ == '__main__':
	scrapeNews()
