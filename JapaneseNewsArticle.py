class newsArticle:
	def __init__(self, title, pubDatetime, url):
		self.__title = title
		self.__pubDatetime = pubDatetime
		self.__url = url
		self.__body = None
		self.__genre = None
		self.__source = None
		self.__imgUrl = None
	def __str__(self):
		return self.__title + "|" + str(self.__pubDatetime) + "|" + str(self.__url)
	def __repr__(self):
		return self.__title + "|" + str(self.__pubDatetime)
	def getTitle(self):
		return self.__title
	def getUrl(self):
		return self.__url
	def getPubDatetime(self):
		return str(self.__pubDatetime)
	def getBody(self):
		return self.__body
	def setBody(self, body):
		self.__body = body
	def getGenre(self):
		return self.__genre
	def setGenre(self, genre):
		self.__genre = genre
	def getSource(self):
		return self.__source
	def setSource(self, source):
		self.__source = source
	def getImgUrl(self):
		return self.__imgUrl
	def setImgUrl(self, imgUrl):
		self.__imgUrl = imgUrl
	def getInsertTuple(self):
		insertTuple = (self.__title, self.__body, self.__url, self.__pubDatetime, self.__genre, self.__source, self.__imgUrl)
		return insertTuple
	def getCheckTuple(self):
		checkTuple = (self.__title, self.__pubDatetime)
		return checkTuple
