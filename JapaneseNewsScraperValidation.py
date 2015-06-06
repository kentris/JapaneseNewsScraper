###################################################
# Our validation methods for the publication datetime
# Paramters: unit of time
# Output: Boolean
###################################################
def isValidHour(hour):
	isValid = False
	if hour >= 0 and hour<= 24:
		isValid = True
	return isValid
def isValidMinute(minute):
	isValid = False
	if minute >= 0 and minute <= 60:
		isValid = True
	return isValid
def isValidSecond(second):
	isValid = False
	if second >= 0 and second <= 60:
		isValid = True
	return isValid
def isValidYear(year):
	isValid = False
	if year>=1990 and year <= (date.today().year + 1):
		isValid = True
	return isValid
def isValidMonth(month):
	isValid = False
	if month >= 1 and month <= 12:
		isValid = True
	return isValid
def isValidDay(day):
	isValid = False
	if day >= 1 and day <= 31:
		isValid = True
	return isValid
