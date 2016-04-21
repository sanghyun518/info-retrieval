"""
Uses machine learning model to predict chances of admission
"""

import numpy as np
import pandas
import QueryUtil

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
        self.performPCA(3)

        # Fit the machine learning model
        self.fit(5)

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
    def fit(self, numNeighbors):
        numTraining = self.trainingData.shape[0]
        self.model = neighbors.KNeighborsClassifier(numNeighbors, weights='distance')
        self.model.fit(self.pca.transform(self.trainingData), self.trainingLabels.reshape((numTraining,)))

    # Perform prediction on held-out test data
    def predict(self, doPrint):
        predictedLabels = self.model.predict(self.pca.transform(self.testingData))

        numTraining = self.trainingData.shape[0]
        numTests = self.testingLabels.shape[0]
        numCorrect = 0

        results = list()

        for i in range(numTests):
            if predictedLabels[i] == self.testingLabels[i][0]:
                numCorrect = numCorrect + 1

            result = []

            for j in range(self.testingData.shape[1]):
                if j > 3:
                    result.append(int(self.testingData[i,j]))
                else:
                    result.append('{:.2f}'.format(self.testingData[i,j]))

            result.append(int(self.testingLabels[i][0]))
            result.append(int(predictedLabels[i]))

            results.append(result)

        accuracy = float(numCorrect) / float(numTests)

        if not doPrint:
            return accuracy

        print "\n\nClassification using k-Nearest Neighbors"
        print "Number of Training Data: {}".format(numTraining)
        print "Number of Testing Data: {}".format(numTests)

        print 'Accuracy: {:.2f} ({}/{})'.format(accuracy, numCorrect, numTests)
        print 'Details:'

        header = ['GPA', 'GRE(V)', 'GRE(Q)', 'GRE(W)', 'Work Exp.', 'Research Exp.', 'Status', 'Decision', 'Predicted']

        pandas.set_option('display.width', 1000)
        print pandas.DataFrame(results, columns=header, index=range(len(results)))
        print '\n\n'

    # Runs experiment to fit the model using various combination of parameters
    def runExperiment(self):
        numTraining = self.trainingData.shape[0]

        results = list()

        for i in range(1, self.dimension-1, 2):
            self.performPCA(i)
            for j in range(1, int(numTraining / 3), 2):
                self.fit(j)
                accuracy = self.predict(False)

                result = list()
                result.append(i)
                result.append(j)
                result.append('{:.2f}'.format(accuracy))

                results.append(result)

        header = [ 'Num. Dimensions', 'Num. Neighbors', 'Accuracy' ]

        pandas.set_option('display.width', 1000)
        print pandas.DataFrame(results, columns=header, index=range(len(results)))
