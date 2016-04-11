"""
The main script for gathering various graduate school information.
"""
import GoHackers
import GradCafe
import QueryUtil
import UsNews

# Ask user if he/she wants to initiate another query
def continueQuery():
    print "Continue with another query [y/n, default: y]:"
    input = raw_input()
    return not input or input.lower() == 'y'

# Main loop
while True:
    print "    ============================================================"
    print "    ==    Welcome to the 600.466 Graduate School IR Engine"
    print "    ============================================================"
    print ""
    print "    OPTIONS:"
    print "      1 = Find top 20 schools for specified area"
    print "      2 = Find schools in certain location"
    print "      3 = View admission history for specified school"
    print "      4 = Quit"
    print ""
    print "    ============================================================"

    input = raw_input()
    input = int(input) if input.isdigit() else 4

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
        break
    elif input == 3:
        # Get query parameters from user
        school = None
        major  = None
        degree = None

        while not school or school.strip() == '':
            print "    Enter school name:"
            school = raw_input()

        while not major or major.strip() == '':
            print "    Enter major:"
            major = raw_input()

        while not degree or degree.strip() == '':
            print "    Enter degree:"
            degree = raw_input()

        # Create dictionary of query parameters
        query = dict()
        query[QueryUtil.schoolKey] = school
        query[QueryUtil.degreeKey] = degree
        query[QueryUtil.majorKey]  = major

        # Print results from different sites
        print "GradCafe Results:\n"
        GradCafe.getResults(query)

        print "GoHackers Results:\n"
        GoHackers.getResults(query)

        if not continueQuery():
            break
    else:
        break
