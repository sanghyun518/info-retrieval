"""
Scrapes http://thegradcafe.com/ for admission results
"""
import re
import requests
import pandas
import QueryUtil

from bs4 import BeautifulSoup

# The parameter 'query' is a dictionary of query information,
# for example, { 'school' : 'Johns Hopkins', 'degree' : 'PhD' }
def getResults(query, doPrint):
    school = query[QueryUtil.schoolKey]
    major  = query[QueryUtil.majorKey]
    degree = query[QueryUtil.degreeKey]

    numResults = 100 if doPrint else 250

    # Construct URL with query parameters
    queryStr = re.sub(r"\s+", '+', school + " " + major)
    url = "http://thegradcafe.com/survey/index.php?q=" + queryStr + "&t=a&o=&pp=" + str(numResults)

    # Get HTML result
    html_content = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(html_content, "lxml")

    # Find total number of pages
    div = soup.find("div", {"class": "pagination"})
    anchors = div.find_all("a", href=True)
    numPages = len(anchors) + 1

    # Start scraping data from table

    header   = list()
    results  = list()
    features = list()  # Vectors to be used for machine learning

    # Get results for first page
    getResult(degree, features, header, results, soup, doPrint, True)

    currentPage = numPages + 1 if doPrint else 2

    # Get results for next pages
    while currentPage <= numPages:
        url = "http://thegradcafe.com/survey/index.php?q=" + queryStr + "&t=a&pp=" + str(numResults) + "&o=&p=" + str(currentPage)

        # Get HTML result
        html_content = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
        soup = BeautifulSoup(html_content, "lxml")

        getResult(degree, features, None, results, soup, doPrint, False)

        currentPage = currentPage + 1

    print "Total : " + str(len(results)) + " posts\n"

    # Use 'pandas' library for neat tabular representation
    if doPrint:
        pandas.set_option('display.width', 1000)
        print pandas.DataFrame(results, columns=header, index=range(len(results)))

    return features

# Scrapes results for a single page
def getResult(degree, featureVectors, header, results, soup, doPrint, fillHeader):
    table = soup.find('table')

    if not table:
        if doPrint:
            print "Total : 0 posts"
        return None

    rows = table.find_all('tr')
    for i in range(len(rows)):
        cols = rows[i].find_all('td')
        colTexts = [col.text.strip() for col in cols]

        validResult = True

        gpaScore = None
        greScore = None

        for j in range(len(colTexts)):
            colText = colTexts[j]

            if i > 0:  # Non-header data
                if j == 1 and degree.lower() not in colText.lower():
                    validResult = False
                    break
                if j == 2:
                    if 'Accepted' in colText:
                        colTexts[j] = 'Accepted'
                    elif 'Rejected' in colText:
                        colTexts[j] = 'Rejected'
                    else:
                        validResult = False
                        break

                    scoresInfo = cols[j].find('a')

                    if scoresInfo:
                        match = re.match(r'.*GPA.*\s([0-9]\.[0-9]{2}).*', scoresInfo.text)
                        gpaScore = match.group(1) if match else None

                        match = re.match(r'.*GRE\s+General.+([0-9]{3}\/[0-9]{3}\/[0-9.]+).*', scoresInfo.text)
                        greScore = match.group(1) if match else None

                        if gpaScore is None or greScore is None:
                            validResult = False
                            break
                    else:
                        validResult = False
                        break

        if not validResult:
            continue

        if i > 0 and (gpaScore is None or greScore is None):
            continue

        colTexts = colTexts[1:]  # Do not show 'institution'

        if i == 0:
            if fillHeader:
                # Header
                colTexts[1] = 'Decision'
                colTexts.insert(0, 'GRE')
                colTexts.insert(0, 'GPA')
                header.extend(colTexts)
        else:
            # Data

            # 1. Add feature vector
            gre = re.match(r'([0-9]+)/([0-9]+)/([0-9.]+)', greScore)

            featureVector = dict()
            featureVector[QueryUtil.decision]   = 1 if 'Accepted' == colTexts[1] else 0
            featureVector[QueryUtil.gpaScore]   = float(gpaScore)
            featureVector[QueryUtil.greVerbal]  = float(gre.group(1))
            featureVector[QueryUtil.greQuant]   = float(gre.group(2))
            featureVector[QueryUtil.greWriting] = float(gre.group(3))
            featureVector[QueryUtil.workExp]    = hasWorkExperience(colTexts[4])
            featureVector[QueryUtil.research]   = hasResearchExperience(colTexts[4])
            featureVector[QueryUtil.status]     = 0 if 'A' == colTexts[2] else 1

            featureVectors.append(featureVector)

            # 2. Add data for display
            colTexts.insert(0, greScore)
            colTexts.insert(0, gpaScore)
            results.append(colTexts)

# Checks whether keywords related to work experience exist it the 'Notes' section
def hasWorkExperience(notes):
    negativeKeywords = ['no work', 'no industry']
    positiveKeywords = ['work', 'industry']

    return QueryUtil.searchKeywords(notes, negativeKeywords, positiveKeywords)

# Checks whether keywords related to research experience exist it the 'Notes' section
def hasResearchExperience(notes):
    negativeKeywords = ['no research', 'no publi']
    positiveKeywords = [ 'research', 'publish', 'publication', 'paper', 'academic', 'author', 'conference' ]

    return QueryUtil.searchKeywords(notes, negativeKeywords, positiveKeywords)
