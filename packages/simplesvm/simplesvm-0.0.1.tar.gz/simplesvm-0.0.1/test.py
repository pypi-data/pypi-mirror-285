import numpy as np

from simplesvm import KernelSVM, LinearSVM

# クラス0のデータを生成
np.random.seed(0)
n = 0.75
X_class0 = np.random.randn(50, 2) + np.array([n, n])
y_class0 = np.zeros(50)

# クラス1のデータを生成
X_class1 = np.random.randn(50, 2) + np.array([-n, -n])
y_class1 = np.ones(50)

# データを結合
X = np.vstack((X_class0, X_class1))
y = np.hstack((y_class0, y_class1))

# データをシャッフル
indices = np.arange(X.shape[0])
np.random.shuffle(indices)
X = X[indices]
y = y[indices]

# 訓練とテストに分割 (80% 訓練, 20% テスト)
split_index = int(0.8 * X.shape[0])
X_train, X_test = X[:split_index], X[split_index:]
y_train, y_test = y[:split_index], y[split_index:]


for i, svm in enumerate([LinearSVM(), KernelSVM()]):
    svm.fit(X_train, y_train)
    y_pred = svm.predict(X_test)
    acc = sum(y_test == y_pred) / len(y_test)
    if i == 0:
        print(f"LinearSVM acc: {acc}")
    else:
        print(f"KernelSVM acc: {acc}")
