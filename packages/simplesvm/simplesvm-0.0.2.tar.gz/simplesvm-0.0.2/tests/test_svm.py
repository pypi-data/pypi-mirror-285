import numpy as np

from simplesvm import KernelSVM, LinearSVM


def make_dataset():
    np.random.seed(0)
    X_class0 = np.random.randn(50, 2) + np.array([2, 2])
    y_class0 = np.zeros(50)

    X_class1 = np.random.randn(50, 2) + np.array([-2, -2])
    y_class1 = np.ones(50)

    X = np.vstack((X_class0, X_class1))
    y = np.hstack((y_class0, y_class1))

    indices = np.arange(X.shape[0])
    np.random.shuffle(indices)
    X = X[indices]
    y = y[indices]

    split_index = int(0.8 * X.shape[0])
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y[:split_index], y[split_index:]

    return X_train, X_test, y_train, y_test


def test_linear_svm():
    X_train, X_test, y_train, y_test = make_dataset()
    model = LinearSVM()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = (y_test == y_pred).sum() / len(y_test)
    assert acc >= 0.95


def test_kernel_svm():
    X_train, X_test, y_train, y_test = make_dataset()
    model = KernelSVM()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = (y_test == y_pred).sum() / len(y_test)
    assert acc >= 0.95
