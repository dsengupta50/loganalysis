import feature_utils
import numpy as np

# train kNN detector
from pyod.models.knn import KNN

def main():
    print("Hello anomaly detection")
    clf_name = 'KNN'
    clf = KNN()
    X_train = feature_utils.get_data()

    clf.fit(X_train)
    # If you want to see the predictions of the training data, you can use this way:
    y_train_scores = clf.decision_scores_
    for y in y_train_scores:
        print(y)


# Start program
if __name__ == "__main__":
    main()
