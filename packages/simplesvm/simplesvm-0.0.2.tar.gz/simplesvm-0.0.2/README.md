# simplesvm

[![PyPI - Version](https://img.shields.io/pypi/v/simplesvm.svg)](https://pypi.org/project/simplesvm)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/simplesvm.svg)](https://pypi.org/project/simplesvm)

-----

A simple Support Vector Machine for binary classification with scikit-learn like API.

- Repository: https://github.com/obizip/simplesvm
- About this SVM (ja)
    - LinearSVM: https://zenn.dev/obizip/articles/2024-07-04-linear_svm
    - KernelSVM:

## Installation

```console
pip install simplesvm
```

## How to use
### LienearSVM
```python
from simplesvm import LinearSVM
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_moons
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt


np.random.seed(42)

X, y = make_blobs(random_state=8,
                  n_samples=500,
                  n_features=2,
                  cluster_std=3,
                  centers=2)

X_train, X_test, y_train, y_test = train_test_split(X, y)

model = LinearSVM()
model.fit(X_train, y_train)
preds = model.predict(X_test)

print(f"ACC: {accuracy_score(y_test, preds)}")
# ACC: 0.936

plt.figure(figsize=(8, 7))
plt.scatter(X[:, 0], X[:, 1], marker='o', c=y, s=25, edgecolor='k')
w = model._w
# w0*x + w1*y + w2 = 0
# y = - (w0*x + w2) / w1
plt.plot(X[:, 0], - (w[0] * X[:, 0] + w[2]) / w[1])
```

### KernelSVM
```python
from simplesvm import KernelSVM
import numpy as np
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

np.random.seed(42)

X, y = make_moons(n_samples=500, noise=0.1, random_state=1)
X_train, X_test, y_train, y_test = train_test_split(X, y)

model = KernelSVM()
model.fit(X_train, y_train)
preds = model.predict(X_test)

print(f"ACC: {accuracy_score(y_test, preds)}")

# Plot a decision boundary
x_min=X[:, 0].min()
x_max=X[:, 0].max()
y_min=X[:, 1].min()
y_max=X[:, 1].max()

xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.01), np.arange(y_min, y_max, 0.01))
XY = np.array([xx.ravel(), yy.ravel()]).T
z = model.predict(XY)
plt.contourf(xx, yy, z.reshape(xx.shape), alpha=0.2, cmap=plt.cm.coolwarm)
plt.scatter(X[:, 0], X[:, 1], c=y, s=10, cmap=plt.cm.coolwarm)
plt.show()
```

## License

`simplesvm` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

