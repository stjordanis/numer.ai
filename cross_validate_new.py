#!/usr/bin/env python

"cross-validation"

import pandas as pd
from time import clock

### Load and prepare data

train_file = 'dataset/numerai_training_data.csv'

start = clock()
train_frame = pd.read_csv(train_file)
print('Loaded {:d} train entries in {:.0f} seconds.'.format( 
    len(train_frame), clock() - start))

# Remove validation column, not used here
train_frame.drop('validation', axis = 1 , inplace = True)

# Separate train data and label
label = train_frame['target']
train_frame.drop('target', axis = 1, inplace = True)

# One-hot encode of categorical variable
# Encode column in train, then drop original column
train_dummies = pd.get_dummies(train_frame['c1'])
train = pd.concat((train_frame.drop('c1', axis = 1), train_dummies.astype(int)), axis = 1)

### Select classifiers

from sklearn.ensemble import RandomForestClassifier as RF
rf1 = RF(n_estimators = 10, verbose = True)
rf2 = RF(n_estimators = 100, verbose = True)
rf3 = RF(n_estimators = 1000, verbose = True)

from sklearn.linear_model import LogisticRegression as LR
lr = LR()

from sklearn.linear_model import SGDClassifier
sgd = SGDClassifier()

from sklearn.svm import LinearSVC
lsvc = LinearSVC(tol = 0.01, C = 1)

# from sklearn.svm import SVC
# svc = SVC()

clf_list = [lr, lsvc, sgd, rf1, rf2, rf3]

### Cross validation

from sklearn.cross_validation import cross_val_score

for clf in clf_list:
    print clf
    start = clock()
    scores = cross_val_score(clf, train, label, scoring = 'roc_auc', cv = 10, verbose = 1)
    print(
        "Performed {:d}-fold cross validation in {:.0f} seconds with ROC AUC: mean {:0.4f} std {:0.4f}.".format(
        len(scores), clock() - start, scores.mean(), scores.std() ))

"""
Results

LR()
Performed 10-fold cross validation in 3 seconds with ROC AUC: mean 0.5254 std 0.0044.

RF(n_estimators = 10, verbose = True)
mean 0.5092 std 0.0043

LinearSVC(tol = 0.01, C = 1)
Performed 10-fold cross validation in 111 seconds with ROC AUC: mean 0.5085 std 0.0116.

SGDClassifier()
Performed 10-fold cross validation in 3 seconds with ROC AUC: mean 0.5002 std 0.0135.

RF(n_estimators = 100, verbose = True)
Performed 10-fold cross validation in 35 seconds with ROC AUC: mean 0.5125 std 0.0101.

RF(n_estimators = 1000, verbose = True)
Performed 10-fold cross validation in 348 seconds with ROC AUC: mean 0.5227 std 0.0092.
"""
