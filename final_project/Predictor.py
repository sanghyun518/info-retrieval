"""
Uses machine learning model to predict chances of admission
"""

import numpy as np
import pandas
import QueryUtil

from sklearn import svm
from sklearn import neighbors
from sklearn import decomposition

class Predictor:

    # Constructor
    def __init__(self, gradResults, goResults):
        # Dimension of dictionary
        self.dimension = 8

        # Pre-process the data to create full training/testing data
        data = self.preProcess(gradResults, goResults)

        # Partition the data into training and testing
        numTraining = int(0.8 * data.shape[0])
        self.trainingData   = data[0:numTraining,0:self.dimension-1]
        self.testingData    = data[numTraining:,0:self.dimension-1]
        self.trainingLabels = data[0:numTraining,self.dimension-1:]
        self.testingLabels  = data[numTraining:,self.dimension-1:]

        # Perform PCA for dimensionality reduction
        self.performPCA(5)

        # Fit the machine learning model
        self.fitKnn(5)
        self.fitSvm(10)

    # Returns structured data to be used in machine learning library
    def preProcess(self, gradResults, goResults):
        data = np.ndarray(shape=(self.dimension, 0), dtype=np.float)

        for results in [gradResults, goResults]:
            for result in results:
                vector = np.ndarray(shape=(self.dimension, 1), dtype=np.float)

                gpa = result[QueryUtil.gpaScore]
                achievedGpa = None
                maxPossibleGpa = None

                if gpa:
                    if isinstance(gpa, float):
                        if float(gpa) > 0:
                            achievedGpa = float(gpa)
                            maxPossibleGpa = 4.0
                    else:
                        if '/' in gpa:
                            tokens = gpa.split('/')
                            achievedGpa = tokens[0]
                            maxPossibleGpa = tokens[1]

                if achievedGpa and maxPossibleGpa:
                    gpa = QueryUtil.normalizeGpa(achievedGpa, maxPossibleGpa)
                    if gpa > 1:
                        continue
                    else:
                        vector[0,0] = gpa
                else:
                    continue

                verbal = result[QueryUtil.greVerbal]

                if isinstance(verbal, float) or (verbal and verbal.isdigit() and int(verbal) > 0):
                    vector[1,0] = QueryUtil.normalizeGre(verbal)
                else:
                    continue

                quant = result[QueryUtil.greQuant]

                if isinstance(quant, float) or (quant and quant.isdigit() and int(quant) > 0):
                    vector[2,0] = QueryUtil.normalizeGre(quant)
                else:
                    continue

                writing = result[QueryUtil.greWriting]

                try:
                    if isinstance(writing, float) or (writing and float(writing) > 0):
                        vector[3,0] = float(writing)
                    else:
                        continue
                except Exception:
                    continue

                vector[4,0] = float(result[QueryUtil.workExp])
                vector[5,0] = float(result[QueryUtil.research])
                vector[6,0] = float(result[QueryUtil.status])
                vector[7,0] = float(result[QueryUtil.decision])

                data = np.hstack((data, vector))

        data = data.transpose()

        np.random.shuffle(data)

        return data

    # Perform PCA on training data for dimensionality reduction
    def performPCA(self, numComponents):
        self.pca = decomposition.PCA(n_components=numComponents)
        self.pca.fit(self.trainingData)

    # Fit the ML model based on acquired training data
    def fitKnn(self, numNeighbors):
        numTraining = self.trainingData.shape[0]
        self.knn = neighbors.KNeighborsClassifier(numNeighbors, weights='distance')
        self.knn.fit(self.pca.transform(self.trainingData), self.trainingLabels.reshape((numTraining,)))

    def fitSvm(self, gamma):
        numTraining = self.trainingData.shape[0]
        self.svm = svm.SVC(decision_function_shape='ovo',kernel='rbf',gamma=gamma,C=1000)
        self.svm.fit(self.pca.transform(self.trainingData), self.trainingLabels.reshape((numTraining,)))

    # Perform prediction on held-out test data
    def predict(self):
        numTraining = self.trainingData.shape[0]
        numTests = self.testingLabels.shape[0]

        print "\n\nNumber of Training Data: {}".format(numTraining)
        print "Number of Testing Data: {}".format(numTests)

        print "\nClassification using k-Nearest Neighbors"

        self.printResults(self.knn)

        print "\nClassification using SVM with RBF kernel"

        self.printResults(self.svm)

        print '\n\n'

    # Prints the result of predictions
    def printResults(self, model):
        numTests = self.testingLabels.shape[0]

        header = ['GPA', 'GRE(V)', 'GRE(Q)', 'GRE(W)', 'Work Exp.', 'Research Exp.', 'Status', 'Decision', 'Predicted']

        results = list()

        predictedLabels = model.predict(self.pca.transform(self.testingData))
        res = self.getResults(predictedLabels, results)

        print 'Accuracy: {:.2f} ({}/{})'.format(res[0], res[1], numTests)
        print 'Details:'

        pandas.set_option('display.width', 1000)
        print pandas.DataFrame(results, columns=header, index=range(len(results)))

    # Returns a tuple of accuracy and number of correct predictions
    def getResults(self, predictedLabels, results):
        numCorrect = 0
        numTests = self.testingLabels.shape[0]

        for i in range(numTests):
            if predictedLabels[i] == self.testingLabels[i][0]:
                numCorrect = numCorrect + 1

            result = []

            for j in range(self.testingData.shape[1]):
                if j > 3:
                    result.append(int(self.testingData[i, j]))
                else:
                    result.append('{:.2f}'.format(self.testingData[i, j]))

            result.append(int(self.testingLabels[i][0]))
            result.append(int(predictedLabels[i]))

            results.append(result)

        return (float(numCorrect) / float(numTests), numCorrect)

    # Runs experiment to fit the model using various combination of parameters
    def runExperiment(self):
        numTraining = self.trainingData.shape[0]

        print "\nClassification using k-Nearest Neighbors"

        results = list()

        for i in range(1, self.dimension - 1, 2):
            self.performPCA(i)
            for j in range(1, int(numTraining / 3), 2):
                self.fitKnn(j)
                predictedLabels = self.knn.predict(self.pca.transform(self.testingData))
                res = self.getResults(predictedLabels, list())

                result = list()
                result.append(i)
                result.append(j)
                result.append('{:.2f}'.format(res[0]))

                results.append(result)

        header = ['Num. Dimensions', 'Num. Neighbors', 'Accuracy']

        pandas.set_option('display.width', 1000)
        print pandas.DataFrame(results, columns=header, index=range(len(results)))

        print "\nClassification using SVM with RBF kernel"

        results = list()

        for i in range(1, self.dimension - 1, 2):
            self.performPCA(i)
            for j in range(100, 1000, 100):
                self.fitSvm(j)
                predictedLabels = self.svm.predict(self.pca.transform(self.testingData))
                res = self.getResults(predictedLabels, list())

                result = list()
                result.append(i)
                result.append(j)
                result.append('{:.2f}'.format(res[0]))

                results.append(result)

        header = ['Num. Dimensions', 'Gamma', 'Accuracy']

        pandas.set_option('display.width', 1000)
        print pandas.DataFrame(results, columns=header, index=range(len(results)))
