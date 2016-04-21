"""
Scrapes school official website for a list of faculty members and their research areas
"""

import re
import requests
import json
import QueryUtil

from bs4 import BeautifulSoup

# The parameter 'query' is a dictionary of query information,
# for example, { 'school' : 'Johns Hopkins', 'degree' : 'PhD' }
def getResults(query):
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

    counter = 0

    if facultyLink:
        visitedUrls = dict() # Keeps track of visited urls

        # Get all links within faculty page
        content = requests.get(str(facultyLink), headers={'User-Agent': 'Mozilla/5.0'}).text
        soup = BeautifulSoup(content, "lxml")

        # Remove header and footer since these are definitely not relevant
        if soup.header:
            soup.header.decompose()
        if soup.footer:
            soup.footer.decompose()

        anchors = soup.find_all("a", href=True)

        if anchors:
            # Visit each link to see if there is information about a faculty member
            for anchor in anchors:
                url = anchor['href']

                if len(anchor.text.strip()) == 0:
                    continue

                if url in visitedUrls:
                    continue

                visitedUrls[url] = 0

                if validUrl(url):
                    try:
                        content = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
                        soup = BeautifulSoup(content, "lxml")

                        if validContent(soup):
                            match = re.search(r'>(.+\S+\s+(research|holds|received|area|director|member|fellow|earned)[^<]+)', content)

                            if match:
                                counter = counter + 1
                                print str(counter) + '. ' + anchor.text
                                print removeTags(match.group(1))
                                print '\n'
                    except:
                        continue

    if counter == 0:
        print 'Could not find information...\n'

# Pre-screening of URLs that definitely would not contain information about faculty member
def validUrl(url):
    if url.endswith('.edu') or url.endswith('.edu/'):
        return False
    if not url.startswith('http'):
        return False
    return True

# Check if the content contains certain keywords related to faculty member's homepage
def validContent(soup):
    anchors = soup.find_all("a", href=True)

    if anchors:
        for anchor in anchors:
            for keyword in [ 'teaching', 'teachings', 'publication', 'publications', 'cv', 'curriculum vitae' ]:
                if keyword == anchor.text.lower().strip():
                    return True

    headings = soup.findAll(re.compile("^h\d"))

    if headings:
        for heading in headings:
            for keyword in [ 'research interest', 'areas of interest' ]:
                if keyword in heading.text.lower():
                    return True

    return False

# Removes HTML related tags in given string
def removeTags(str):
    soup = BeautifulSoup('<p>' + str + '<p>', "lxml")
    for tag in soup.find_all(True):
        tag.replaceWith(tag.text)
    return soup.renderContents()