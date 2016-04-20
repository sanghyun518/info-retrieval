"""
Scrapes http://www.gohackers.com/ for admission results
"""
import re
import requests
import QueryUtil
from bs4 import BeautifulSoup
import pandas
import threading

########################################################################################################################
# The parameter 'query' is a dictionary of query information,
# for example, { 'school' : 'Johns Hopkins', 'degree' : 'PhD' }
# This function inputs a query with format specified as above and boolean value doPrint as an indicator to print or not
# and reuturns the list of results in dictionary format with keys that are written in QueyUtil.py
# for example, { 'decision': 1, 'greVerbal': 500, 'greQuant': 700, 'greWriting': 4.0, 'gpaScore':3.5/4.0 and etc}
########################################################################################################################
# Note to concern:
# 1. Display format ex. decision, workExp, researchExp instead of 1,
#    want to display Accepted/Rejected or True/False in the future.
# 2. Note that it may take a significantly long time depending on the number of posts to look for. (apprx. 2.4 sec per post)
# 3. Number of results can be decreased if query is complex. (ex. school name & non-popular major & phd)
#    Almost less than 5 or None
# 4. There are some special cases where user did not followed the format as the others write the post.
#    For example, id='content_5' mostly contains GRE or Test Scores, but rarely some people put it in id='content_1'/
#    In this case, the scores are stated as 0.
# 5. Improvements can be made to handle special cases, date of notice.
######################################################################################################################
def getResults(query, doPrint) :
    # Base url
    base_url = "http://www.gohackers.com"

    # Construct URL with query parameters
    url = "http://www.gohackers.com/?r=gohackers&c=prepare/prepare_info/admission&m=bbs&bid=admission&sort=gid&orderby=asc&where=subject|content&degree=%EB%8C%80%ED%95%99%EC%9B%90&keyword="
    if query[QueryUtil.degreeKey].lower() is "phd" :
        url = url + query[QueryUtil.schoolKey].lower() + "%26%26" + query[QueryUtil.majorKey].lower() + "%26%26ph.d"
    else :
        url = url + query[QueryUtil.schoolKey].lower() + "%26%26" + query[QueryUtil.majorKey].lower() + "%26%26" + query[QueryUtil.degreeKey].lower()



    # Initialize tot_page that indicates total pages
    tot_pages = 1

    # If not need to print, get actual total number of pages
    if not doPrint :
        tot_pages = getTotalPageNum(url)

    # A list to store result from each post
    results = list()

    # A list of active threads
    threads = list()

    for i in range (1, tot_pages+1) :
        if doPrint :                         # Update page number until it searches all pages
            url += "&recnum=15&p=" + str(i)  # Also give different limit of number of posts to check
        else :                               # depending on doPrint flag
            url += "&recnum=70&p=" + str(i)

        # Get post subjects
        post_subjects = getPostSubjects(url)

        if doPrint :
            print "Total : " + str(len(post_subjects)-5) + " posts"

        # Get result from each post in one page
        for subject in post_subjects :

            # Check if the post is a Notice or Ads
            if subject.a.b == None :
                a = subject.find("a", href=True)

                # Get Result from each post
                thread = threading.Thread(target=getResult, args=(base_url+a['href'], query[QueryUtil.schoolKey].lower(), results))
                threads.append(thread)
                print ">>",
    print

    # Start each thread
    for thread in threads:
        thread.start()

    # Wait for each thread to finish
    for thread in threads:
        thread.join()

    if doPrint:
        if len(results) > 0 :
            # Use 'pandas' library for neat tabular representation
            pandas.set_option('display.width', 1000)

            # Print only the first 15 results
            print pandas.DataFrame(results[0:15])
        else :
            "Could not find any result that matches to given query."

    return results

###############################################################
# Helper function to retrieve information from each post
# This function requires a single url that leads to a post
# and returns the results from its post such as
# "decision(accepted/rejected)", "GRE or Test Scores", and etc.
###############################################################
def getResult(url, schoolName, results) :

    # Get HTML result form a post
    html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, "lxml")

    header = [QueryUtil.decision, QueryUtil.greVerbal, QueryUtil.greQuant, QueryUtil.greWriting, QueryUtil.gpaScore, QueryUtil.workExp, QueryUtil.research, QueryUtil.status, QueryUtil.postId]
    result = {}

    # Initialize the values in result to 0
    for key in range(len(header)-2) :
        result[header[key]] = 0

    # Initialize the value for Applicant Status to 1 (International Student)
    result[header[len(header)-2]]= 1

    # Check if school name is listed on the acceptance list
    try :
        if (schoolName in soup.find("td",id="content_1").text.encode("utf-8","ignore").lower()) :
            result[header[0]] = 1
    except Exception as ex :
        print "Cannot find Acceptance List"

    try :
        # Get gre scores
        testScores = soup.find("td",id="content_5").text
        # print testScores.encode("utf-8","ignore")

        regex = re.compile("[A-Z]*([0-9]{3})[\/\s]*[A-Z]*([0-9]{3})[\/\s]*[A-Z]*([0-9].[0-9])")
        match = re.search(regex,testScores)

        if match :
            result[header[1]] = match.group(1)
            result[header[2]] = match.group(2)
            result[header[3]] = match.group(3)
        else :
            "=============== Cannot Find GRE Schores ==============="
    except Exception as ex :
        print "Cannot find TestScores"

    # Get GPA
    try :
        gpaScore = soup.find("td", id="content_4").text
        # print gpaScore.encode("utf-8","ignore")

        # searches for the gpa format from the text
        regex = re.compile("[0-9].[0-9][0-9]?\/[0-9].[0-9][0-9]?")
        match = re.search(regex, gpaScore)

        if match :
            result[header[4]] = match.group(0)
        else :
            "=============== Cannot find GPA ================"
    except Exception as ex :
        print "Cannot find GPAs"

    # Get Work and Research experience
    try :
        exp = soup.find("td", id="content_7").text
        # print exp.encode("utf-8","ignore")

        # check if the text has word "intern" in Korean
        wrkMatch = re.search(u'\uc778\ud134', exp)
        # check if the text has word "research" in Korean
        resMatch = re.search(u'\uc5f0\uad6c', exp)

        if wrkMatch :
            # print wrkMatch.group()
            result[header[5]] = 1

        if resMatch :
            # print resMatch.group()
            result[header[6]] = 1
    except Exception as ex :
        print "Cannot find experiences"

    # Store the post ID
    try :
        gid_regex = re.search("uid=([0-9]+)", url)
        result[header[8]] = gid_regex.group(1)
    except Exception as ex :
        print "Cannot get the UID"

    results.append(result)

#####################################################################################
# Helper function for getResults.
# This function requires a url and computes the total number of pages that can cover
# the entire list of results that was retrieved.
#####################################################################################
def getTotalPageNum(url) :
    url += "&recnum=1"
    post_subjects = getPostSubjects(url)

    # Find the number of the total results
    tot_num = 0
    for subject in post_subjects :
        if subject.a.b == None :
            tr_tag = subject.parent
            tot_num = int(tr_tag.find("td").text)
            print "Total : " + str(tot_num) + " posts"
            break

    tot_pages = tot_num / 70

    if (tot_num % 70 != 0) :
        tot_pages += 1

    return tot_pages

#################################################################################
# Helper function.
# This function inputs a url and outputs html component that contains all subject
# of posts in the given url.
#################################################################################
def getPostSubjects(url) :
    # Get HTML Text
    html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, "lxml")

    # Start scraping posts by searching for subjects
    post_subjects = soup.find_all("td", class_="sbj")

    return post_subjects