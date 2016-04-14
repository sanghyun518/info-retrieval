"""
Contains common constants and functions useful for querying data
"""

# Query keys

schoolKey = 'school'
degreeKey = 'degree'
majorKey  = 'major'

# Vector keys (let's keep these simple for now)

greVerbal  = 'greVerbal'  # Use 'normalizeGre' function below
greQuant   = 'greQuant'   # Use 'normalizeGre' function below
greWriting = 'greWriting' # Raw score between 0.0 and 6.0
gpaScore   = 'gpaScore'   # Use 'normalizeGpa' function below
workExp    = 'workExp'    # 1 if there is work experience, otherwise 0
research   = 'research'   # 1 if there is research experience (or published papers), otherwise 0
status     = 'status'     # 1 if international student, otherwise 0

# Additional keys that can be used later
decision   = 'decision'   # 1 if acceted from the school, otherwise 0
postId     = 'postId'     # post Id to check for unusual data such as all '0' gre_scores or gpaScore 

# Normalizes GRE V/Q scores to account for different versions
def normalizeGre(score):
    if score > 200:
        # Old GRE
        return float(score) / 800.0
    else:
        # New GRE
        return float(score) / 170.0

# Normalizes GPA scores to account for different formats
def normalizeGpa(achievedGpa, maxPossibleGpa):
    return float(achievedGpa) / float(maxPossibleGpa)

# Searches text for given keywords
def searchKeywords(text, negativeKeywords, positiveKeywords):
    text = text.lower()

    # Immediately return if there is a negative keyword
    for negativeKeyword in negativeKeywords:
        if negativeKeyword in text:
            return 0

    # Now search for positive keywords
    for positiveKeyword in positiveKeywords:
        if positiveKeyword in text:
            return 1

    return 0

