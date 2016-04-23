"""
Scrapes school official website for a list of current students and their backgrounds
"""

import re
import requests
import pandas
import json
import QueryUtil
from bs4 import BeautifulSoup

# The parameter 'query' is a dictionary of query information,
# for example, { 'school' : 'Johns Hopkins', 'major' : computer science }
# The function will run the query with school name and major. However,
# if there is no result that matches the query, it will rerun the query with
# school name only.
# NOTE : Still need to work on the printing the data

# ============================
# Get Results using Indeed.com
# ============================
def getResults(query) :
    school = query[QueryUtil.schoolKey]
    major = query[QueryUtil.majorKey]

    # get HTML content
    soup = getContent(school, major)
  
    # find links of result resume and get specific information from resume
    if soup.find_all("li", class_="sre") :
        printResume(soup)
    else :
        print "========================================================"
        print "No Result is Found. Now searching only with school name."
        print "========================================================"
        print
        soup = getContent(school)
        if soup.find_all("li", class_="sre") :
            printResume(soup)
        else :
            print "No Result Available, Please try with different school."

# Helper function to get html content
def getContent(schoolName, major="") :
    if len(major) > 0 :
        q = "q=title%3A%28phd candidate%29 school:%28" + schoolName + "%29 fieldofstudy:%28" + major + "%29"
    else :
        q = "q=title%3A%28phd candidate%29 school:%28" + schoolName + "%29"
        
    webpage = "http://www.indeed.com/resumes?co=US&" + q

    # get HTML content
    html_content = requests.get(webpage).text
    soup = BeautifulSoup(html_content, "lxml")

    return soup

# Helper function to find link for each resume and calls scrape_resume function
def printResume(soup) :
    for link in soup.find_all("li", class_="sre") :
        postId = link.get("id")
        name = link.find("div","app_name").find("a").text
        name = name.replace(" ", "-")
        link = "http://www.indeed.com/r/" + name + "/" + postId
        print scrape_resume(link)
        print

# Helper function to grap information from a resume
def scrape_resume(url) :
    html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, "lxml")
    person = {}
    item = ['name','job_title','location', 'education', 'webpage', 'work_experience']
    
    # name
    person[item[0]] = soup.find(id="resume-contact").string
    
    # job_title
    try :
        person[item[1]] = soup.find(id="headline").string
    except Exception as e :
        person[item[1]] = ""
    
    # location
    try :
        person[item[2]] = soup.find(id = "headline_location").string
    except Exception as e :
        person[item[2]] = ""
    
    # education
    educations = []
    try :    
        edu = soup.find("div", "section-item education-content")
        edus = edu.find_all("div", "data_display")
        edu_info = ["degree", "school_name","school_location", "edu_dates"]
        for i in edus :
            education = {}
            try :
                education[edu_info[0]] = i.find("p", "edu_title").string
            except Exception as e :
                education[edu_info[0]] = ""
            try :
                education[edu_info[1]] = i.find("span", itemprop="name").string
            except Exception as e :
                education[edu_info[1]] = ""
            try :
                education[edu_info[2]] = i.find("span", itemprop="addressLocality").string
            except Exception as e :
                education[edu_info[2]] = ""
            try : 
                education[edu_info[3]] = i.find("p", "edu_dates").string
            except Exception as e :
                education[edu_info[3]] = ""
            educations.append(education)
        person[item[3]] = educations
    except Exception as e :
        person[item[3]] = ""
    
    # webpages
    webpages = []
    try :
        webpage = soup.find("div", "section-item links-content")
        urls = webpage.find_all("p", "link_url")
        for i in urls :
            webpages.append(i.find("a").string)
        person[item[4]] = webpages
    except Exception as e :
        person[item[4]] = ""
    
    # work_experiences
    works = []
    try :
        w = soup.find("div", "section-item workExperience-content") # html for work expeirnce item section
        work_experiences = w.find_all("div", "data_display") # find all work expeirnces
        work_info = ["work_title","company_name","company_location","work_dates"] # create a list of info for work-exp
        for i in work_experiences :
            work = {}
            # work title
            try :
                work[work_info[0]] = i.find("p", "work_title title").string
            except Exception as e :
                work[work_info[0]] = ""
            # company name
            try :
                work[work_info[1]] = i.find("div", "work_company").find("span", "bold").string
            except Exception as e :
                work[work_info[1]] = ""
            # company location
            try :
                work[work_info[2]] = i.find("div", "inline-block").string
            except Exception as e :
                work[work_info[2]] = ""
            # work dates
            try :
                work[work_info[3]] = i.find("p", "work_dates").string
            except Exception as e :
                work[work_info[3]] = ""
            works.append(work)
        person[item[5]] = works # add work-exps to person dictionary
    except Exception as e :
        person[item[5]] = ""
    
    return person

# =========================================
# Get Results from Google
# =========================================
# def getResults(query):
#     header = {'User-Agent': 'Mozilla/5.0'}

#     school = query[QueryUtil.schoolKey]
#     major = query[QueryUtil.majorKey]
#     degree = query[QueryUtil.degreeKey]

#     # Search using Google

#     queryStr = school + " " + major + " " + degree + " student"
#     searchResult = QueryUtil.google(queryStr)

#     jsonData = json.loads(searchResult)
#     studentLink = None

#     if jsonData:
#         results = jsonData['responseData']['results']

#         if len(results) > 0 :
#             # Assume the first result has the correct link for student directory
#             studentLink = results[0]['url']

#     # Check if the link is actually student directory

#     # Start scraping if a link to the student page has been found


#     if studentLink :
#         # Get all links within student directory page
#         content = requests.get(str(studentLink), headers = header).text
#         soup = BeautifulSoup(content, "lxml")
#         refs = soup.find_all("a", href=True)

#         # if refs :
            
#     print ""
