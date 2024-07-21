
import numpy as np
from venn_abers import VennAbersCalibrator, VennAbers

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

n_features = 10
rand_seed = 0
n_samples = 10000

X, y = make_classification(
    n_classes=4,
    n_samples=n_samples,
    n_clusters_per_class=2,
    n_features=n_features,
    n_informative=int(n_features / 2),
    n_redundant=int(n_features / 4),
    random_state=rand_seed)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=rand_seed)

clf = RandomForestClassifier(random_state=0)

X_train_proper, X_cal, y_train_proper, y_cal = train_test_split(
    X_train, y_train, test_size=0.2, shuffle=False
)

clf.fit(X_train_proper, y_train_proper)
p_cal = clf.predict_proba(X_cal)
p_test = clf.predict_proba(X_test)



classes = np.unique(y_train_proper)
class_pairs = []
for i in range(len(classes) - 1):
    for j in range(i + 1, len(classes)):
        class_pairs.append([i, j])

multiclass_probs = []
for i, class_pair in enumerate(class_pairs):
    pairwise_indices = (y_cal == class_pair[0]) + (y_cal == class_pair[1])
    binary_cal_probs = p_cal[:, class_pair][pairwise_indices] / np.sum(p_cal[:, class_pair][pairwise_indices], axis=1).reshape(-1, 1)
    binary_test_probs = p_test[:, class_pair] / np.sum(p_test[:, class_pair], axis=1).reshape(-1, 1)
    binary_classes = y_cal[pairwise_indices] == class_pair[1]

    va = VennAbers()
    va.fit(binary_cal_probs, binary_classes)
    p_prime, p0_p1 = va.predict_proba(binary_test_probs)
    multiclass_probs.append(p_prime)


p_prime = np.zeros((len(p_test), len(classes)))

for i, cl_id, in enumerate(classes):
    stack_i = [
        p[:, 0].reshape(-1, 1) for i, p in enumerate(multiclass_probs) if class_pairs[i][0] == cl_id]
    stack_j = [
        p[:, 1].reshape(-1, 1) for i, p in enumerate(multiclass_probs) if class_pairs[i][1] == cl_id]
    p_stack = stack_i + stack_j

    p_prime[:, i] = 1/(np.sum(np.hstack([(1/p) for p in p_stack]), axis=1) - (len(classes) - 2))

p_prime = p_prime/np.sum(p_prime, axis=1).reshape(-1, 1)

def predict_proba_prefitted_va(p_cal, y_cal, p_test, precision=None):
    classes = np.unique(y_train_proper)
    class_pairs = []
    for i in range(len(classes) - 1):
        for j in range(i + 1, len(classes)):
            class_pairs.append([i, j])

    multiclass_probs = []
    for i, class_pair in enumerate(class_pairs):
        pairwise_indices = (y_cal == class_pair[0]) + (y_cal == class_pair[1])
        binary_cal_probs = p_cal[:, class_pair][pairwise_indices] / np.sum(p_cal[:, class_pair][pairwise_indices],
                                                                           axis=1).reshape(-1, 1)
        binary_test_probs = p_test[:, class_pair] / np.sum(p_test[:, class_pair], axis=1).reshape(-1, 1)
        binary_classes = y_cal[pairwise_indices] == class_pair[1]

        va = VennAbers()
        va.fit(binary_cal_probs, binary_classes, precision=precision)
        p_pr, p0_p1 = va.predict_proba(binary_test_probs)
        multiclass_probs.append(p_pr)

    p_prime = np.zeros((len(p_test), len(classes)))

    for i, cl_id, in enumerate(classes):
        stack_i = [
            p[:, 0].reshape(-1, 1) for i, p in enumerate(multiclass_probs) if class_pairs[i][0] == cl_id]
        stack_j = [
            p[:, 1].reshape(-1, 1) for i, p in enumerate(multiclass_probs) if class_pairs[i][1] == cl_id]
        p_stack = stack_i + stack_j

        p_prime[:, i] = 1 / (np.sum(np.hstack([(1 / p) for p in p_stack]), axis=1) - (len(classes) - 2))

    p_prime = p_prime / np.sum(p_prime, axis=1).reshape(-1, 1)

    return p_prime


print()