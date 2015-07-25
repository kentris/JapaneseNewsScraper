########## NHK News Variables ##########################
NHK_GENRE = ["Society", "Culture/Entertainment", "Science/Medicine", "Politics", "Economics", "International", "Sports"]
NHK_URL = ["http://www3.nhk.or.jp/rss/news/cat1.xml", "http://www3.nhk.or.jp/rss/news/cat2.xml", "http://www3.nhk.or.jp/rss/news/cat3.xml", "http://www3.nhk.or.jp/rss/news/cat4.xml", "http://www3.nhk.or.jp/rss/news/cat5.xml", "http://www3.nhk.or.jp/rss/news/cat6.xml", "http://www3.nhk.or.jp/rss/news/cat7.xml"]
NHK_TAG = {'title': 'title', 'url': 'guid', 'pubdate':'pubdate'}
NHK_SOURCE = "NHK"
TEXT_BODY_REGEXP = r'(<div id="news_textbody">)(.*)(</div>)'
TEXT_MORE_REGEXP = r'(<div id="news_textmore">[\r\n]*)(.*)([\r\n]*</div>)'
NEWS_ADD_REGEXP = r'(<div class="news_add">[\r\n]*<h3>)(.*)(</h3>[\r\n]*<div>)(.*)(</div>)'  
NHK_IMAGE_URL_REGEXP = r'(<img id="news_image" src=")(.*)(" alt)'
NHK_PUB_DATETIME_LENGTH = 31
NHK_PUB_INFO_LENGTH = 6
########## Asahi News Variables ##########################
ASAHI_GENRE = ["Society", "Politics", "Sports", "Economics", "International", "Culture/Entertainment"]
ASAHI_URL = ["http://www3.asahi.com/rss/national.rdf", "http://www3.asahi.com/rss/politics.rdf", "http://www3.asahi.com/rss/sports.rdf", "http://www3.asahi.com/rss/business.rdf", "http://www3.asahi.com/rss/international.rdf", "http://www3.asahi.com/rss/culture.rdf"]
ASAHI_TAG = {'title':'title', 'url':'link', 'pubdate':'dc:date'}
ASAHI_SOURCE = "Asahi"
ASAHI_IMAGE_URL_REGEXP = r'(<div class="Image">)([\n\r]*.*[\n\r]*src=")(.*)(" />)'
ASAHI_PUB_DATETIME_LENGTH = 25
ASAHI_PUB_INFO_LENGTH = 3


MONTHS = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
DATABASE_NAME = 'JAPAN_NEWS.db'
########### SQLite Queries ######################
CREATE_TABLE = "CREATE TABLE IF NOT EXISTS ARTICLES(TITLE TEXT NOT NULL, BODY TEXT NOT NULL, URL TEXT NOT NULL, PUBDATETIME DATE NOT NULL, GENRE TEXT NOT NULL, SOURCE TEXT NOT NULL, IMAGE_URL TEXT, PRIMARY KEY(TITLE, PUBDATETIME, BODY))"
CHECK_FOR_ARTICLE = "SELECT * FROM ARTICLES WHERE TITLE = ? AND PUBDATETIME = ?"
INSERT_ARTICLE = "INSERT INTO ARTICLES VALUES (?,?,?,?,?,?,?)"  

URL_GENRE_SOURCE = [("http://www3.nhk.or.jp/rss/news/cat1.xml", "Society", "NHK"), ("http://www3.nhk.or.jp/rss/news/cat2.xml", "Culture/Entertainment", "NHK"), ("http://www3.nhk.or.jp/rss/news/cat3.xml", "Science/Medicine", "NHK"), ("http://www3.nhk.or.jp/rss/news/cat4.xml", "Politics", "NHK"), ("http://www3.nhk.or.jp/rss/news/cat5.xml", "Economics", "NHK"), ("http://www3.nhk.or.jp/rss/news/cat6.xml", "International", "NHK"), ("http://www3.nhk.or.jp/rss/news/cat7.xml", "Sports", "NHK"), ("http://www3.asahi.com/rss/national.rdf", "Society", "Asahi"), ("http://www3.asahi.com/rss/politics.rdf", "Politics", "Asahi"), ("http://www3.asahi.com/rss/sports.rdf", "Sports", "Asahi"), ("http://www3.asahi.com/rss/business.rdf", "Economics", "Asahi"), ("http://www3.asahi.com/rss/international.rdf", "International", "Asahi"), ("http://www3.asahi.com/rss/culture.rdf", "Culture/Entertainment", "Asahi") ]
LOG_DIRECTORY = "Logs"