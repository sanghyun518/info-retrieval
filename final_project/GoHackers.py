"""
Scrapes http://www.gohackers.com/ for admission results
"""
import re
import requests
from bs4 import BeautifulSoup

# The parameter 'query' is a dictionary of query information,
# for example, { 'school' : 'Johns Hopkins', 'degree' : 'PhD' }
# This function requires a query with format specified as above 
# and reuturns the list of results from GoHackers by school
# for example, 1. School Name(SAIS/KELLOGG or etc), GRE Score, and etc

def getResults(query):
	url = "http://www.gohackers.com/?r=gohackers&c=prepare/prepare_info/admission&m=bbs&bid=admission&sort=" + "gid&orderby=asc&recnum=20&where=subject|content&degree=%EB%8C%80%ED%95%99%EC%9B%90&keyword=" + query["school"]
	base_url = "http://www.gohackers.com"
	html_content = requests.get(url).text
	soup = BeautifulSoup(html_content, "lxml")

	post_results = []
	post_subjects = soup.find_all("td", class_="sbj")
	for subject in post_subjects :
		a = subject.find("a", href=True)

		# print the result from each posts.
		getResult(base_url+a['href'])

# helper function to retrieve information from each post
# This function requires a single url that leads to a post
# and returns the results from its post such as "accepted school name(and department name)", "GRE or Test Scores", and etc.
# Still in progress.
def getResult(url) :
	result = "" #TO DO
	print

