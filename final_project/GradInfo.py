"""
The main script for gathering various graduate school information.
"""
import FacultyInfo
import StudentInfo
import GoHackers
import GradCafe
import QueryUtil
import UsNews

from Predictor import Predictor

# Ask user if he/she wants to initiate another query
def continueQuery():
    print "Continue with another query [y/n, default: y]:"
    input = raw_input()
    return not input or input.lower() == 'y'

# Returns a dictionary of query parameters
def getQuery(needSchool, needMajor, needDegree):
    # Get query parameters from user
    school = ''
    major = ''
    degree = ''

    if needSchool:
        while not school or school.strip() == '':
            print "    Enter school name:"
            school = raw_input()

    if needMajor:
        while not major or major.strip() == '':
            print "    Enter major:"
            major = raw_input()

    if needDegree:
        while not degree or degree.strip() == '':
            print "    Enter degree:"
            degree = raw_input()

    # Create dictionary of query parameters
    query = dict()
    query[QueryUtil.schoolKey] = school
    query[QueryUtil.degreeKey] = degree
    query[QueryUtil.majorKey] = major

    return query

# Main loop
while True:
    print "    ============================================================"
    print "    ==    Welcome to the 600.466 Graduate School IR Engine"
    print "    ============================================================"
    print ""
    print "    OPTIONS:"
    print "      1 = View top schools for specified area"
    print "      2 = View faculty members for specified school(s)"
    print "      3 = View current students for specified school(s)"
    print "      4 = View admission history for specified school"
    print "      5 = Predict chance of admission for specified school"
    print "      6 = Quit"
    print ""
    print "    ============================================================"

    input = raw_input()
    input = int(input) if input.isdigit() else 6

    if input == 1:
        # Create options
        options = dict()
        options[1] = 'Business'
        options[2] = 'Education'
        options[3] = 'Engineering'
        options[4] = 'Law'
        options[5] = 'Medicine'
        options[6] = 'Nursing'

        # Print options
        print "    Choose area:"
        for key, value in options.iteritems():
            print "      {} = {}".format(key, value)

        # Get user input
        input = raw_input()
        input = int(input) if input.isdigit() else -1

        if input in options:
            # Print query results if valid input
            UsNews.getTop20(options[input])

            if not continueQuery():
                break
        else:
            break
    elif input == 2:
        # Get query from user
        query = getQuery(True, True, False)

        # Print list of faculty members
        FacultyInfo.getResults(query)

        if not continueQuery():
            break
    elif input == 3:
        # Get query from user
        query = getQuery(True, True, False)

        # Print list of students
        StudentInfo.getResults(query)

        if not continueQuery():
            break
    elif input == 4:
        # Get query from user
        query = getQuery(True, True, True)

        print "\n\n"

        # Print results from different sites
        print "GradCafe Results:\n"
        GradCafe.getResults(query, True)

        print "\n\n"

        print "GoHackers Results:\n"
        GoHackers.getResults(query, True)

        if not continueQuery():
            break
    elif input == 5:
        # Display machine learning results

        # Get query from user
        query = getQuery(True, True, True)

        print "\n"

        # Get results from GradCafe
        gradResults = GradCafe.getResults(query, False)

        QueryUtil.refineQuery(query)

        # Get results from GoHackers
        goResults = GoHackers.getResults(query, False)

        # Predict outcome
        predictor = Predictor(gradResults, goResults)
        predictor.predict()

        if not continueQuery():
            break
    else:
        break
