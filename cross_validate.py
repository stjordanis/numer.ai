#!/usr/bin/env python

"""
Cross-validation with a few classifiers.
"""

import pandas as pd
import numpy as np
from time import clock
from itertools import product

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

clfs = []

from sklearn.ensemble import RandomForestClassifier as RF
rf1 = RF(n_estimators = 10, verbose = True)
rf2 = RF(n_estimators = 100, verbose = True)
rf3 = RF(n_estimators = 1000, verbose = True)
rf4 = RF(n_estimators = 10000, verbose = True)

from sklearn.linear_model import SGDClassifier
sgd = SGDClassifier()

from sklearn.svm import LinearSVC
lsvc = LinearSVC(tol = 0.01, C = 1)

from sklearn.ensemble import ExtraTreesClassifier
etc2 = ExtraTreesClassifier(n_estimators = 100, max_depth = None, min_samples_split = 1, random_state = 0)
etc3 = ExtraTreesClassifier(n_estimators = 1000, max_depth = None, min_samples_split = 1, random_state = 0)

# Logistic regression with preprocessor

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer, MinMaxScaler, StandardScaler
from sklearn.linear_model import LogisticRegression as LR

lr = LR()

transformers = [ MinMaxScaler(), StandardScaler(), 
                 Normalizer( norm = 'l1' ), Normalizer( norm = 'l2' ) ]

clfs += [make_pipeline(p) for p in product(transformers, [LR()])]

# Classifiers from Scikit Flow
# Optimizer choices: SGD, Adam, Adagrad

from skflow import TensorFlowLinearClassifier
tflc = TensorFlowLinearClassifier(n_classes = 1, batch_size = 256, steps = 1400, learning_rate = 0.01, optimizer = 'Adagrad')

from skflow import TensorFlowLinearRegressor
tflr = TensorFlowLinearRegressor(n_classes = 1, batch_size = 256, steps = 1400, learning_rate = 0.01, optimizer = 'Adagrad')

from skflow import TensorFlowDNNClassifier
tfdnnc = TensorFlowDNNClassifier(hidden_units = [100, 200, 200, 200, 100],
                                    n_classes = 1, batch_size = 256, steps = 1000, learning_rate = 0.01, optimizer = 'Adagrad')

clfs += [lr, lsvc, sgd, rf1, rf2, rf3, rf4, etc2, etc3]
# clfs += [tflc, tflr, tfdnnc]

### Cross validation

from sklearn.cross_validation import cross_val_score

for clf in clfs:
    print(clf)
    start = clock()
    scores = cross_val_score(clf, train, label, scoring = 'roc_auc', cv = 10, verbose = 1)
    print(
        "Performed {:d}-fold cross validation in {:.0f} seconds with ROC AUC: mean {:0.4f} std {:0.4f}.".format(
        len(scores), clock() - start, scores.mean(), scores.std() ))

"""
Results

LogisticRegression(C=1.0, class_weight=None, dual=False, fit_intercept=True,
          intercept_scaling=1, penalty=l2, random_state=None, tol=0.0001)
Performed 10-fold cross validation in 3 seconds with ROC AUC: mean 0.5254 std 0.0044.

LinearSVC(C=1, class_weight=None, dual=True, fit_intercept=True,
     intercept_scaling=1, loss=l2, multi_class=ovr, penalty=l2,
     random_state=None, tol=0.01, verbose=0)
Performed 10-fold cross validation in 116 seconds with ROC AUC: mean 0.5051 std 0.0186.

SGDClassifier(alpha=0.0001, class_weight=None, epsilon=0.1, eta0=0.0,
       fit_intercept=True, l1_ratio=0.15, learning_rate=optimal,
       loss=hinge, n_iter=5, n_jobs=1, penalty=l2, power_t=0.5,
       random_state=None, rho=None, shuffle=False, verbose=0,
       warm_start=False)
Performed 10-fold cross validation in 1 seconds with ROC AUC: mean 0.5002 std 0.0135.

RandomForestClassifier(bootstrap=True, compute_importances=None,
            criterion=gini, max_depth=None, max_features=auto,
            min_density=None, min_samples_leaf=1, min_samples_split=2,
            n_estimators=10, n_jobs=1, oob_score=False, random_state=None,
            verbose=True)
Performed 10-fold cross validation in 35 seconds with ROC AUC: mean 0.5057 std 0.0058.

RandomForestClassifier(bootstrap=True, compute_importances=None,
            criterion=gini, max_depth=None, max_features=auto,
            min_density=None, min_samples_leaf=1, min_samples_split=2,
            n_estimators=100, n_jobs=1, oob_score=False, random_state=None,
            verbose=True)
Performed 10-fold cross validation in 351 seconds with ROC AUC: mean 0.5213 std 0.0082.

RandomForestClassifier(bootstrap=True, compute_importances=None,
            criterion=gini, max_depth=None, max_features=auto,
            min_density=None, min_samples_leaf=1, min_samples_split=2,
            n_estimators=1000, n_jobs=1, oob_score=False,
            random_state=None, verbose=True)
Performed 10-fold cross validation in 3307 seconds with ROC AUC: mean 0.5279 std 0.0054.

ExtraTreesClassifier(bootstrap=False, compute_importances=None,
           criterion=gini, max_depth=None, max_features=auto,
           min_density=None, min_samples_leaf=1, min_samples_split=1,
           n_estimators=100, n_jobs=1, oob_score=False, random_state=0,
           verbose=0)
Performed 10-fold cross validation in 143 seconds with ROC AUC: mean 0.5228 std 0.0077.

ExtraTreesClassifier(bootstrap=False, compute_importances=None,
           criterion=gini, max_depth=None, max_features=auto,
           min_density=None, min_samples_leaf=1, min_samples_split=1,
           n_estimators=1000, n_jobs=1, oob_score=False, random_state=0,
           verbose=0)
Performed 10-fold cross validation in 1433 seconds with ROC AUC: mean 0.5255 std 0.0067.

LogisticRegression(C=1.0, class_weight=None, dual=False, fit_intercept=True,
          intercept_scaling=1, penalty=l2, random_state=None, tol=0.0001)
Performed 10-fold cross validation in 3 seconds with ROC AUC: mean 0.5254 std 0.0044.

MinMaxScaler(copy=True, feature_range=(0, 1))
Performed 10-fold cross validation in 4 seconds with ROC AUC: mean 0.5354 std 0.0062.

StandardScaler(copy=True, with_mean=True, with_std=True)
Performed 10-fold cross validation in 5 seconds with ROC AUC: mean 0.5354 std 0.0062.

Normalizer(copy=True, norm=l1)
Performed 10-fold cross validation in 3 seconds with ROC AUC: mean 0.5254 std 0.0049.

Normalizer(copy=True, norm=l2)
Performed 10-fold cross validation in 3 seconds with ROC AUC: mean 0.5261 std 0.0051.
"""
