"""
Scrapes school official website for a list of faculty members and their research areas
"""

import re
import requests
import json
import QueryUtil

from bs4 import BeautifulSoup
from urlparse import urlparse

# The parameter 'query' is a dictionary of query information,
# for example, { 'school' : 'Johns Hopkins', 'degree' : 'PhD' }
def getResults(query):
    school = query[QueryUtil.schoolKey]
    major = query[QueryUtil.majorKey]

    # Search using Google

    queryStr = school +  ' ' + major + ' faculty'
    facultyLink = QueryUtil.google(queryStr)

    # Start scraping if a link to the faculty page has been found

    counter = 0

    if facultyLink:
        print '\nSearching "' + facultyLink + '"\n'

        # Get base URL to deal with relative URLs
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(facultyLink))

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

                numWords = len(anchor.text.split())

                # Minimum qualification for anchor text to match a faculty name
                if len(anchor.text.strip()) == 0 or numWords < 2 or numWords > 3:
                    continue

                # Handle relative URL
                if url.startswith('/'):
                    url = domain + url[1:] if domain.endswith('/') else domain + url

                # Skip visited sites
                if url in visitedUrls:
                    continue

                visitedUrls[url] = 0

                # Check obvious bad URLs
                if validUrl(url):
                    try:
                        # Visit link
                        content = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
                        soup = BeautifulSoup(content, "lxml")

                        # Remove header and footer since these are definitely not relevant
                        if soup.header:
                            soup.header.decompose()
                        if soup.footer:
                            soup.footer.decompose()

                        # Check if this is a page related to faculty information
                        if validContent(soup):
                            matches = re.finditer(r'>(.+\S+\s+(research|holds|received|area|director|member|fellow|earned)[^<]+)', content)

                            longestStr = None # Hack to avoid getting irrelevant short sentences containing above keywords.

                            if matches:
                                for match in matches:
                                    matchStr = match.group(1)
                                    if longestStr is None or len(longestStr) < len(matchStr):
                                        if matchStr[0].isupper():
                                            longestStr = matchStr
                            if longestStr:
                                counter = counter + 1
                                print str(counter) + '. ' + anchor.text
                                print removeTags(longestStr)
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
    if not 'Professor' in soup.text:
        return False

    anchors = soup.find_all("a", href=True)

    if anchors:
        for anchor in anchors:
            for keyword in [ 'teaching', 'teachings', 'publication', 'publications', 'cv', 'curriculum vitae' ]:
                if keyword == anchor.text.lower().strip():
                    return True

    headings = soup.findAll(re.compile("^h\d"))

    if headings:
        for heading in headings:
            for keyword in [ 'research interest', 'areas of interest', 'publications', 'bio' ]:
                if keyword in heading.text.lower():
                    return True

    return False

# Removes HTML related tags in given string
def removeTags(str):
    soup = BeautifulSoup('<p>' + str + '<p>', "lxml")
    for tag in soup.find_all(True):
        tag.replaceWith(tag.text)
    return soup.renderContents()