import numpy as np
from venn_abers import VennAbers

from venn_abers import VennAbersCalibrator

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import log_loss


def predict_proba_prefitted_va(p_cal, y_cal, p_test, precision=None):
    classes = np.unique(y_cal)

    multiclass_probs = []
    multiclass_p0p1 = []
    for _, class_id in enumerate(classes):
        class_indices = (y_cal == class_id)
        binary_cal_probs = np.zeros((len(p_cal), 2))
        binary_test_probs = np.zeros((len(p_test), 2))
        binary_cal_probs[:, 1] = p_cal[:, class_id]
        binary_cal_probs[:, 0] = 1 - binary_cal_probs[:, 1]
        binary_test_probs[:, 1] = p_test[:, class_id]
        binary_test_probs[:, 0] = 1 - binary_test_probs[:, 1]
        binary_classes = class_indices

        va = VennAbers()
        va.fit(binary_cal_probs, binary_classes, precision=precision)
        p_pr, p0_p1 = va.predict_proba(binary_test_probs)
        multiclass_probs.append(p_pr)
        multiclass_p0p1.append(p0_p1)

    p_prime = np.zeros((len(p_test), len(classes)))

    for i, _ in enumerate(classes):
        p_prime[:, i] = multiclass_probs[i][:, 1]

    p_prime = p_prime / np.sum(p_prime, axis=1).reshape(-1, 1)

    return p_prime, multiclass_p0p1


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


# clf.fit(X_train, y_train)
# p_train = clf.predict_proba(X_train)
# p_test = clf.predict_proba(X_test)

X_train_proper, X_cal, y_train_proper, y_cal = train_test_split(
    X_train, y_train, test_size=0.2, shuffle=False
)


clf = RandomForestClassifier(random_state=rand_seed)
clf.fit(X_train_proper, y_train_proper)
p_cal = clf.predict_proba(X_cal)
p_test = clf.predict_proba(X_test)


va_prefit_prob, p0p1 = predict_proba_prefitted_va(p_cal=p_cal, y_cal=y_cal, p_test=p_test)

clf = RandomForestClassifier(random_state=rand_seed)
va = VennAbersCalibrator(estimator=clf, inductive=True, shuffle=False, cal_size=0.2)
va.fit(X_train, y_train)
va_prefit_prob_2 = va.predict_proba(X_test)


print(log_loss(y_test, p_test))
print(log_loss(y_test, va_prefit_prob))
print(log_loss(y_test, va_prefit_prob_2))
print()