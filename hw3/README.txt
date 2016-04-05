For the 'custom' position weighting scheme, I gave 100 times more weight to immediate adjacent words than others.
The following is the evaluation result of different permutations (which can be obtained by running option #1):

                Position     Local Collocation                Accuracy
    Stemming    Weighting    Modelling                tank    plant    pers/place
    ===============================================================================

    unstemmed    uniform      bag-of-words             0.93    0.53    0.53
    stemmed      expndecay    bag-of-words             0.94    0.54    0.51
    unstemmed    expndecay    bag-of-words             0.90    0.55    0.53
    unstemmed    expndecay    adj-separate-LR          0.91    0.55    0.59
    unstemmed    stepped      adj-separate-LR          0.90    0.52    0.58
    unstemmed    custom       adj-separate-LR          0.82    0.57    0.58
    stemmed      bayes        bag-of-words             0.91    0.65    0.60

* Note that as an extension, I have implemented the simple Bayesian model.
