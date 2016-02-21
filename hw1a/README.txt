I have emebedded the logistic classifier that I obtained via Weka into perl code.

To test, simply run "hw1a.prl < sent.data.test"

---------------------------------------------------------------------------

Result on training set:
### HW1A schoi60 - OVERALL CORRECT: 44380 = 98.6%    INCORRECT: 620 = 1.4%

---------------------------------------------------------------------------

Logistic classifier was chosen because, based on my research, this classifier
was considered most suitable for this kind of task. Indeed, other classifiers
either performed poorly or tended to overfit (such as decision trees).

The degree of overfitting was tested by splitting the training data into 
various ratios (e.g. 60% training, 40% test).
