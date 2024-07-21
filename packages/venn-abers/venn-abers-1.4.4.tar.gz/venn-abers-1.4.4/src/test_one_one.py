import numpy as np
from venn_abers import VennAbersCalibrator, VennAbers

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from sklearn.naive_bayes import GaussianNB

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from sklearn.metrics import log_loss

from sklearn.utils.estimator_checks import check_estimator


n_features = 10
rand_seed = 272
n_samples = 10000

X, y = make_classification(
    n_classes=3,
    n_samples=n_samples,
    n_clusters_per_class=2,
    n_features=n_features,
    n_informative=int(n_features / 2),
    n_redundant=int(n_features / 4),
    random_state=rand_seed)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=rand_seed)

clf = RandomForestClassifier(random_state=rand_seed)
clf.fit(X_train, y_train)
p_train = clf.predict_proba(X_train)
p_test = clf.predict_proba(X_test)


clf = RandomForestClassifier(random_state=rand_seed)
va = VennAbersCalibrator(estimator=clf, inductive=True, shuffle=False, cal_size=0.2)
va.fit(X_train, y_train)
va_prefit_prob = va.predict_proba(X_test)


print(log_loss(y_test, p_test))
print(log_loss(y_test, va_prefit_prob))
print()
# class CustomOneVsOneClassifer:
#
#     def __init__(self):
#         self.classes = None
#         self.n_classes = None
#         self.pairwise_id = []
#         self.estimators_ = []
#
#     def fit(self, p_cal, y_cal):
#
#         self.classes = np.unique(y_cal)
#         self.n_classes = len(self.classes)
#
#         for i in range(self.n_classes):
#             for j in range(i + 1, self.n_classes):
#                 self.pairwise_id.append([self.classes[i], self.classes[j]])
#
#     def predict_proba(self, p_test):
#         p_prime = np.zeros((len(p_test), 2))
#         p_prime[:, 0] = p_test[:, self.pairwise_id[0][0]]
#         p_prime[:, 1] = p_test[:, self.pairwise_id[0][1]]
#         p_prime = p_prime / np.sum(p_prime, axis=1).reshape(-1, 1)
#
#         return p_prime


# test = CustomOneVsOneClassifer()
# test.fit(p_train, y_train)
# opa = test.predict_proba(p_test)
# papa = 0

# clf = GaussianNB()
# va = VennAbersCalibrator(estimator=clf, inductive=False, n_splits = 3, random_state=27)
# va.fit(X_train, y_train)
# opa = 0
#
#
# class SpecialClassifier(ClassifierMixin, BaseEstimator):
#     def __init__(self):
#         pass
#
#     def fit(self, X, y, **kwargs):
#         if y is None:
#             raise ValueError('requires y to be passed, but the target y is None')
#
#         X, y = check_X_y(X, y)
#
#         self.n_features_in_ = X.shape[1]
#         self.classes_ = unique_labels(y)
#         self.is_fitted_ = True
#
#         self.X_ = X
#         self.y_ = y
#
#         return self
#
#     def predict_proba(self, X):
#
#         check_is_fitted(self, ['is_fitted_', 'X_', 'y_'])
#         X = check_array(X)
#
#         p_prime = np.zeros((len(X), 2))
#         p_prime[:, 0] = X[:, self.classes_[0]]
#         p_prime[:, 1] = X[:, self.classes_[1]]
#         p_prime = p_prime / np.sum(p_prime, axis=1).reshape(-1, 1)
#
#         return p_prime
#
#     def predict(self, X, one_hot=False):
#         p_prime = self.predict_proba(X)
#
#         idx = np.argmax(p_prime, axis=-1)
#         if one_hot:
#             y_pred = np.zeros(p_prime.shape)
#             y_pred[np.arange(y_pred.shape[0]), idx] = 1
#         else:
#             y_pred = np.array([self.classes_[i] for i in idx])
#         return y_pred
#
# # check_estimator(SpecialClassifier())
#
# clf = RandomForestClassifier()
# clf.fit(X_train, y_train)
# p_train = clf.predict_proba(X_train)
# p_test = clf.predict_proba(X_test)
#
# clf_special = SpecialClassifier()
#
# va = VennAbersCalibrator(clf_special, cal_size=0.5)
# va.fit(p_train, y_train)
# opa = va.predict_proba(p_test)
#
#
# clf_special.fit(p_train, y_train)
# p_prime = clf_special.predict_proba(p_test)
# y_pred = clf_special.predict(p_test)
# opa = 0
#
# precision = 5
# va = VennAbers()
# va.fit(p_cal, y_cal, precision)
# p_prime, p0_p1 = va.predict_proba(p_test)
#


