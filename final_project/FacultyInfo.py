"""
Scrapes school official website for a list of faculty members and their research areas
"""

import re
import requests
import pandas
import json
import QueryUtil

from bs4 import BeautifulSoup

# The parameter 'query' is a dictionary of query information,
# for example, { 'school' : 'Johns Hopkins', 'degree' : 'PhD' }
def getResults(query):
    header = {'User-Agent': 'Mozilla/5.0'}

    school = query[QueryUtil.schoolKey]
    major = query[QueryUtil.majorKey]

    # Search using Google

    queryStr = school +  ' ' + major + ' faculty'
    searchResult = QueryUtil.google(queryStr)

    jsonData = json.loads(searchResult)

    facultyLink = None

    if jsonData:
        results = jsonData['responseData']['results']

        if len(results) > 0:
            # Assume first result has the correct faculty link (trusting Google)
            facultyLink = results[0]['url']

    # Start scraping if a link to the faculty page has been found

    if facultyLink:
        # Get all links within faculty page
        content = requests.get(str(facultyLink), headers=header).text
        soup = BeautifulSoup(content, "lxml")
        refs = soup.find_all("a", href=True)

        if refs:
            # Visit each link to see if there is information about a faculty member
            for ref in refs:
                url = ref['href']
                if url.startswith('http') and not url.endswith('.edu') and not url.endswith('.edu/'):
                    try:
                        content = requests.get(ref['href'], headers=header).text
                        soup = BeautifulSoup(content, "lxml")
                        links = soup.find_all("a", href=True)

                        # Check if the content contains certain keywords related to faculty member's homepage
                        isValid = False

                        if links:
                            for link in links:
                                for keyword in [ 'teaching', 'publication', 'CV' ]:
                                    if keyword == link.text.lower().strip():
                                        isValid = True
                                        break
                                if isValid:
                                    break

                        if isValid or 'Research Interest' in content:
                            print url
                    except:
                        continue

    print ''

