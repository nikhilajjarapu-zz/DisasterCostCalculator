#IMPORT MODULES
import sys
import os
if ".".join([str(x) for x in sys.version_info[:2]]) != "3.4":
	print("This script requires Python version 3.4. Relaunching now...")	 
	os.system('python3.4 main.py')

from urlbuilder import UrlBuilder
from sklearn import svm
from PIL import Image
import requests
import numpy as np
import dateutil as du
import dateutil.parser
import xml.dom.minidom as md
import datetime
from random import choice
from string import ascii_letters
from bs4 import BeautifulSoup
import warnings

#IGNORE WARNINGS
warnings.filterwarnings("ignore")

#CONSTANTS
API_KEY_GEOCODING = "AIzaSyDEKJP62VjBEYsmIHWhcuOrgAPGrgPHYus"
API_KEY_LANDSAT = "WxZhake5MpviSqNjOfu2e4Rcc9P70AVEwOySreR9"
DISASTERS_API_URL = "http://www.gdacs.org/rss.aspx?profile=ARCHIVE"
DATE_DICT = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
STANDARD_SIZE = (300, 167)

#FUNCTION DECLARATIONS
def getArrayFromScaledImage(filename):
	"""
	takes a filename and turns it into a numpy array of RGB pixels
	"""
	img = Image.open(filename)
	img = img.resize(STANDARD_SIZE)
	img = list(img.getdata())
	#img = map(list, img)
	img = np.array(img)
	return img

def flatten_image(img):
	"""
	takes in an (m, n) numpy array and flattens it 
	into an array of shape (1, m * n)
	"""
	s = img.shape[0] * img.shape[1]
	img_wide = img.reshape(1, s)
	return img_wide[0]

def getArrayFromImageURL(url):
	"""
	Uses URL to download an image and return its scaled version
	"""
	filename = downloadImage(url, "".join([choice(ascii_letters) for x in range(0,6)])+".png")
	if filename == "-1":
		sys.exit(1)
	else:
		return getArrayFromScaledImage(filename)

def downloadImage(url, fname):
	"""
	Download an image with Requests.
	"""
	img = requests.get(url)
	if img.status_code == 200:
		with open("/Users/nikhil/Documents/ScienceFairProject2015/images/" + fname, 'wb') as f:
			f.write(img.content)
		return "/Users/nikhil/Documents/ScienceFairProject2015/images/" + fname
	else:
		print("ERROR: Not a valid image.")
		return "-1"

def getURL(cityorlon, date=None, lat=None):
	"""
	Uses a custom UrlBuilder class that I wrote to build the API url based on the parameters provided.
	"""
	if lat != None:
		ub = UrlBuilder("https://api.nasa.gov/planetary/earth/imagery?")
		ub.addParam("lon", cityorlon)
		ub.addParam("lat", lat)
		if date != None:
			ub.addParam("date", date)
		ub.addParam("cloud_score", "true")
		ub.addParam("api_key", API_KEY_LANDSAT)
		return ub.getURL()[:len(ub.getURL()) - 1]
	else:
		ubb = UrlBuilder("https://maps.googleapis.com/maps/api/geocode/json?")
		ubb.addParam("address", cityorlon)
		ubb.addParam("key", API_KEY_GEOCODING)
		long = str(round(int(requests.get(ubb.getURL()).json()['results'][0]["geometry"]["location"]["lng"]),4))
		lat = str(round(int(requests.get(ubb.getURL()).json()['results'][0]["geometry"]["location"]["lat"]),4))
		if date != None:
			return getURL(long, date, lat)
		else:
			return getURL(long, lat)

def getAttrsFromTree(date):
	"""
	Retrieve the list of disasters from the XML GDACS document.
	"""
	retlist = []
	newurl = DISASTERS_API_URL + "&from=" + str(date)
	tree = md.parseString(requests.get(newurl).content)
	items = tree.getElementsByTagName("item")
	for item in items:
		severity = item.getElementsByTagName('gdacs:severity')[0].getAttribute('value')
		coordinates = [float(x) for x in [item.getElementsByTagName('geo:Point')[0].getElementsByTagName('geo:lat')[0].firstChild.nodeValue,item.getElementsByTagName('geo:Point')[0].getElementsByTagName('geo:long')[0].firstChild.nodeValue]]
		date = item.getElementsByTagName('pubDate')[0].firstChild.nodeValue.split(' ')[1:4][::-1]
		date[1] = DATE_DICT.get(date[1])
		date = '-'.join(date)
		retlist.append([severity, coordinates, date])
	return retlist
	
def runRegressionOnImageURL(url,satmagmdl, magcostmdl):
	"""
	Takes a URL and 2 Regression Models to recreate the entire program in one function.
	"""
	print("ESTIMATED MAGNITUDE: " + str(satmagmdl.predict(flatten_image(getArrayFromImageURL(url)))[0]))
	return magcostmdl.predict(satmagmdl.predict(flatten_image(getArrayFromImageURL(url)))[0])[0]
	
#VARIABLE DECLARATIONS - PART 1
start1 = datetime.datetime.now()

inputs = []
testresult = []
date = None
tempList = []
testdate = datetime.datetime.today() - datetime.timedelta(days=20)
#DATA PARSING - PART 1

while len(inputs) < 120:
	try:
		os.system("clear && printf '\e[3J'")
		print("Parsing data for inputs...")
		print("# OF INPUTS FOUND: " + str(len(inputs)))
		datestr = "-".join([str(testdate.year), str(testdate.month), str(testdate.day).zfill(2)])
		print("CURRENT DATE: " + datestr)
		tempList = getAttrsFromTree(datestr)
		for tlist in tempList:
			coords = tlist[1]
			jsonarr = requests.get(getURL(coords[1],lat = coords[0])).json()
			if 'date' in jsonarr and (du.parser.parse(jsonarr['date']) - testdate).days <= 5 and (du.parser.parse(jsonarr['date']) - testdate).days > 0:	
				if len(inputs) == 0:
					inputs = [flatten_image(getArrayFromImageURL(jsonarr['url']))]
				else:	
					if inputs[0].shape == flatten_image(getArrayFromImageURL(jsonarr['url'])).shape:
						inputs.append(flatten_image(getArrayFromImageURL(jsonarr['url'])))
						testresult.append(float(tlist[0]))
		testdate += datetime.timedelta(days=-2)
	except: 
#My program would crash frequently in the beginning, so I didn't want it to stop everytime. 
#So I added this so the current list of inputs could be used.
		os.system("osascript -e 'display notification \"ERROR\" with title \"ERROR\"'")
		break

#TIME PERFORMANCE		
end1 = datetime.datetime.now()
time1 = start1 - end1
start2 = datetime.datetime.now()

#PREPROCESSING DATA
X = np.array(inputs[:int((len(inputs)-1)/2)])
y = np.array(testresult[:int(len(testresult)/2)], dtype=float).reshape(-1, 1).ravel()

#MACHINE LEARNING - PART 1
print("\n\nTraining the model...")
model = svm.SVR()
print("***\nSizes:\n" + str(X.shape) + "\n" + str(y.shape) + "\n***\n")
print("***\nX: \n" + str(X) + "\nY: \n" + str(y) + "\n***\n")
model.fit(X,y)
print("Model 1 trained!...")

#VARIABLE DECLARATIONS - PART 2
model2 = svm.SVR()
inputs2 = []
outputs2 = []
numdict = {"billion":1000000000}

#DATA PARSING - PART 2
bsoup = BeautifulSoup(requests.get("https://en.wikipedia.org/wiki/Lists_of_earthquakes#Costliest_earthquakes").content, "html.parser")
for tr in bsoup.find_all('table')[2].find_all('tr')[1:]:
	temparr = tr.find_all('td')[0].contents[0].strip().split(" ")
	temp1 = temparr[0]
	temp2 = temparr[1]	
	try:
		tempX = [float(tr.find_all('td')[3].contents[0])]
		tempy = int(temp1[1:]) * numdict[temp2]
	except:
		continue
	if len(tempX) == 1:
		inputs2.append(tempX)
		outputs2.append(tempy)
		
#MACHINE LEARNING - PART 2
print("\n***\nX:\n" + str(inputs2) + "\ny:\n" + str(outputs2) + "\n***")
model2.fit(inputs2,outputs2)
print("Model 2 trained!...")


averageError = []
tempCorrect = []
tempGuess = []

#TEST WITH SAMPLE IMAGES

print("Testing...")
for i in range(int((len(inputs)-1)/2)+1, len(inputs)-1):
	tempCorrect.append(float(testresult[i]))
	tempGuess.append(float(model.predict(inputs[i])[0]))
	temp = [abs(i - j) for i, j in zip(tempCorrect, tempGuess)]
	averageError.append(sum(temp)/len(temp))

while (True):
	print("INTERACTIVE INPUT\n")
	ans = raw_input("Enter 1, 2 or 3 to try a different image: ")
	os.system('clear')
	if ans == 1:		
		print("ESTIMATED MAGNITUDE: " +float(model.predict(inputs[4])[0]) + "\nACTUAL: " + testresult[4])
	elif ans == 2:		
		print("ESTIMATED MAGNITUDE: " +float(model.predict(inputs[i])[2]) + "\nACTUAL: " + testresult[2])
	elif ans == 3:		
		print("ESTIMATED MAGNITUDE: " +float(model.predict(inputs[-1])[0]) + "\nACTUAL: " + testresult[-1])	
	else:
		print("INVALID RESPONSE. TRY AGAIN.")
	
#TIME PERFORMANCE
time2 = datetime.datetime.now() - start2

#STORE RESULTS
print("\n\n\n")
print(str(averageError))
print("\n\n\n")
print(str(sum(averageError)/len(averageError)))
os.system('rm /Users/nikhil/Documents/ScienceFairProject2015/images/*')

with open('result.csv','a') as fp:
	fp.write(str(averageError) + "\nT1:" + str(time1.total_seconds()) + "\nT2:" + str(time2.total_seconds()) + "\n")