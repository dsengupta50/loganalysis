import feature_utils
import logutils

import numpy as np

# train kNN detector
from pyod.models.knn import KNN

TRAINING_FOLDER = logutils.RESULTS_DIR + "/aau"
TEST_FOLDER = logutils.RESULTS_DIR + "/aau_test"


def main():
    print("Hello anomaly detection")
    clf_name = 'KNN'
    clf = KNN()
    X_train, X_messages = feature_utils.get_data(TRAINING_FOLDER)

    clf.fit(X_train)

    # If you want to see the predictions of the training data, you can use this way:
    # get the prediction labels and outlier scores of the training data
    y_train_pred = clf.labels_  # binary labels (0: inliers, 1: outliers)
    y_train_scores = clf.decision_scores_  # raw outlier scores

    X_test, X = feature_utils.get_data(TEST_FOLDER)

    # get the prediction on the test data
    y_test_pred = clf.predict(X_test)  # outlier labels (0 or 1)
    y_test_scores = clf.decision_function(X_test)  # outlier scores
    index = 0
    anomalies = 0
    for y in y_test_pred:
        if y==1:
            print(X[index])
            anomalies = anomalies+1
        index = index+1

    print ("Total number of anomalies = " + str(anomalies))


# Start program
if __name__ == "__main__":
    main()
