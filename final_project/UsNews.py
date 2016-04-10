import re
import requests
from bs4 import BeautifulSoup

def getTop20(industry) :
	url = ""
	if (industry.lower() == "business") :
		url = "http://grad-schools.usnews.rankingsandreviews.com/best-graduate-schools/top-business-schools/mba-rankings"
	elif (industry.lower() == "education") :
		url = "http://grad-schools.usnews.rankingsandreviews.com/best-graduate-schools/top-education-schools/edu-rankings"
	elif (industry.lower() == "engineering") :
		url = "http://grad-schools.usnews.rankingsandreviews.com/best-graduate-schools/top-engineering-schools/eng-rankings"
	elif (industry.lower() == "law") :
		url = "http://grad-schools.usnews.rankingsandreviews.com/best-graduate-schools/top-law-schools/law-rankings"
	elif (industry.lower() == "medicine") : 
		# medicine has two differnt ranking system. 1: research, 2: primary care (default: 1)
		
		# research
		url = "http://grad-schools.usnews.rankingsandreviews.com/best-graduate-schools/top-medical-schools/research-rankings"
		
		# primary care
		# url = "http://grad-schools.usnews.rankingsandreviews.com/best-graduate-schools/top-medical-schools/primary-care-rankings"
	elif (industry.lower() == "nursing") :
		# nursing has two different ranking system. 1: Master's, 2: Doctor of Nursing Practice (default: 2)
		
		# master's
		# url = "http://grad-schools.usnews.rankingsandreviews.com/best-graduate-schools/top-nursing-schools/nur-rankings"
		
		# dnp
		url = "http://grad-schools.usnews.rankingsandreviews.com/best-graduate-schools/top-nursing-schools/dnp-rankings"

	print url
	print industry.lower(), ":"
	html_content = requests.get(url).text
	soup = BeautifulSoup(html_content, "lxml")
	school_names = soup.find_all(True, {"class":"school-name"})
	school_locations = soup.find_all(True, {"class" : "location"})
	school_tuitions = soup.find_all("td", class_=re.compile("search_tuition[\_a-zA-Z]*"))
	for i in range (len(school_names)) :
		print i+1, school_names[i].text.encode("utf-8","ignore"), "|", school_locations[i].text.encode("utf-8","ignore"), "|", school_tuitions[i].text.encode("utf-8","ignore").strip()
	print
	 		
def main() :
	# getTop20("business")
	fields = ["business", "education", "engineering", "law", "medicine", "nursing"]
	for field in fields :
		getTop20(field)

main()
