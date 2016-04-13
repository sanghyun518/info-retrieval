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

    # Construct URL with query parameters
    queryStr = re.sub(r"\s+", '+', school + " " + major)
    url = "http://thegradcafe.com/survey/index.php?q=" + queryStr + "&t=a&o=&pp=100"

    # Get HTML result
    html_content = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(html_content, "lxml")

    # Start scraping data from table

    header  = list()
    results = list()

    table = soup.find('table')

    if not table:
        if doPrint:
            print "Could not find information based on given query"
        return

    rows = table.find_all('tr')
    for i in range(len(rows)):
        row = rows[i]
        cols = row.find_all('td')
        cols = [col.text.strip() for col in cols]

        validResult = True

        for j in range(len(cols)):
            col = cols[j]

            if (i > 0 and j == 1 and degree.lower() not in col.lower()):
                validResult = False
                break
            if (i > 0 and j == 2):
                if 'Accepted' in col:
                    cols[j] = 'Accepted'
                elif 'Rejected' in col:
                    cols[j] = 'Rejected'
                else:
                    validResult = False
                    break

        if not validResult:
            continue

        cols = cols[1:] # Do not show 'institution'

        if i == 0:
            cols[1] = 'Decision'
            header.extend(cols)
        else:
            results.append(cols)

    # Use 'pandas' library for neat tabular representation
    if doPrint:
        pandas.set_option('display.width', 1000)
        print pandas.DataFrame(results, columns=header, index=range(len(results)))
