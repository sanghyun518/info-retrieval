This perl script produces an '*.arff' file that can be consumed by Weka.

---------------------------------------------------------------------------

To produce .arff for training data: hw1b.prl < segment.data.train
To produce .arff for testing data: hw1b.prl < segment.data.test

---------------------------------------------------------------------------

Please use Weka as following:

1. Choose classifier
-> MultiClassClassifier -M 0 -R 2.0 -S 1 -W weka.classifiers.functions.Logistic -- -R 1.0E-8 -M -1

2. Use training set
-> .arff file from "hw1b.prl < segment.data.train"

3. Supplied test set
-> .arff file from "hw1b.prl < segment.data.test"

---------------------------------------------------------------------------

Correctly classified instances: 93.3266% (923 blocks)
Incorrectly classified instances: 6.6734% (66 blocks)

---------------------------------------------------------------------------

Logistic classifier was chosen because it showed the best compromise between
overfitting and accuracy. Decision trees showed the highest performance on
training data itself (around 98%) but these classifiers literally memorized
the training data. That is, once the training data was split, the decision trees
performed very poorly on test data. Other classifiers didn't do very well at all.



