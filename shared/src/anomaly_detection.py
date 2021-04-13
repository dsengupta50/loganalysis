import feature_utils
import logutils

import numpy as np
import sys

# train kNN detector
from pyod.models.knn import KNN
from joblib import dump, load

def main():
    print("Hello anomaly detection")

def train_and_save_model(training_folder, feature_star_regex, model_filename):
    clf_name = 'KNN'
    clf = KNN()
    X_train, X_messages = feature_utils.get_data(training_folder, feature_star_regex)

    clf.fit(X_train)

    dump(clf, model_filename)

def predict(data_folder, feature_star_regex, model_filename):
    clf = load(model_filename)

    print("Detecting anomalies on " + data_folder)
    X_test, X = feature_utils.get_data(data_folder, feature_star_regex)

    # get the prediction on the test data
    y_test_pred = clf.predict(X_test)  # outlier labels (0 or 1)
    y_test_scores = clf.decision_function(X_test)  # outlier scores

    index = 0
    anomalies = 0
    for y in y_test_pred:
        if y==1:
            event = X[index]
            print(event['activity'] + '\t' + event['date']+'\t\t'+event['message'])
            anomalies = anomalies+1
        index = index+1

    print ("Total number of anomalies = " + str(anomalies))

# Start program
if __name__ == "__main__":
    main()
