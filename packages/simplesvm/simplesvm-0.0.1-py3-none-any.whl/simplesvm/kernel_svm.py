import numpy as np


def _rbf_kernel(X: np.ndarray, Y: np.ndarray, gamma: float = 1.0):
    """Compute RBF kernel (Gaussian kernel).

    Parameters
    ----------
    X : numpy.ndarray
        First feature array.
    Y : numpy.ndarray
        Second feature array.
    gamma : float, default=1.0
        Parameter of the RBF kernel.

    Returns
    -------
    K : numpy.ndarray
        The RBF kernel.
    """
    # Compute the squared Euclidean distance between each pair of points in X and Y
    # ||x-y||^2 = ||x||^2 + ||y||^2 - 2 * x^T * y
    X_norm = np.sum(X**2, axis=1).reshape(-1, 1)
    Y_norm = np.sum(Y**2, axis=1).reshape(1, -1)
    D_square = X_norm + Y_norm - 2 * np.dot(X, Y.T)

    # Apply the RBF kernel formula
    K = np.exp(-gamma * D_square)

    return K


class KernelSVM:
    def __init__(
        self,
        lam: float = 0.01,
        n_iters: int = 5000,
        learning_rate: float = 0.01,
        kernel: str = "rbf",
        gamma: float = 1.0,
        bias=True,
        verbose=False,
    ):
        """Kernel Support Vector Machine (SVM) for Binary Classification.

        Parameters
        ----------
        lam : float, default=0.01
            Regularization parameter.
        n_iters : int, default=5000
            Number of iterations for the gradient descent.
        learning_rate : float, default=0.01
            Learning rate for the gradient descent.
        kernel : str, default="rbf"
            Kernel type to be used in the algorithm. It must be one of 'linear', 'rbf'.
        gamma : float, default=1.0
            Kernel parameter for 'rbf'.
        bias : bool, default=True
            Whether to include a bias term in the input matrix.
        verbose : bool, default=False
            If True, print progress messages during the gradient descent.
        """
        self.lam = lam
        self.n_iters = n_iters
        self.learning_rate = learning_rate
        self.bias = bias
        self.kernel = kernel
        self.gamma = gamma
        self.verbose = verbose
        self._Xfit = None
        self._classes = {}
        self._a = None

    # Calculate kernel function
    def _kernelize(self, X, Y):
        if self.kernel == "linear":
            return X @ Y.T
        elif self.kernel == "rbf":
            return _rbf_kernel(X, Y, gamma=self.gamma)
        else:
            raise ValueError(f"Unexpected kernel type: {self.kernel}")

    # Calculate the empirical risk function.
    def _empirical_risk(
        self, K: np.ndarray, y: np.ndarray, a_t: np.ndarray
    ) -> np.ndarray:
        regularzation = 0.5 * self.lam * (a_t @ K @ a_t)
        loss = np.where(1 - y * (K @ a_t) >= 0, 1 - y * (K @ a_t, 0)).mean()

        return regularzation + loss

    # Calculate the gradient of the empirical risk function.
    def _empirical_risk_grad(
        self, K: np.ndarray, y: np.ndarray, a_t: np.ndarray
    ) -> np.ndarray:
        regularzation_grad = self.lam * (K @ a_t)
        loss_grad = (
            (np.where(1 - y * (K @ a_t) >= 0, 1, 0) * -y).reshape(-1, 1) * K
        ).mean(axis=0)

        return regularzation_grad + loss_grad

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fit the Kernel SVM model according to the given training data.

        Parameters
        ----------
        X : numpy.ndarray of shape (n_samples, n_features)
            Training vectors, where `n_samples` is the number of samples
            and `n_features` is the number of features.

        y : numpy.ndarray of shape (n_samples,)
            Class labels in classification.

        Returns
        -------
        self : object
            Fitted estimator.
        """
        # validate and change class labels
        classes = np.unique(y)
        if len(classes) != 2:
            raise ValueError("Class labels is not binary")
        self._classes[-1] = classes[0]
        self._classes[1] = classes[1]
        y = np.where(y == self._classes[1], 1, -1)

        if self.bias:
            X = np.c_[X, np.ones(X.shape[0])]

        self._Xfit = X
        K = self._kernelize(X, X)

        # alpha for weights
        a = np.ones((K.shape[1]))

        # gradient descent
        for i in range(self.n_iters):
            a = a - self.learning_rate * self._empirical_risk_grad(K, y, a)
            if self.verbose and (i + 1) % 1000 == 0:
                print(f"{i+1:4}: R(a) = {self._empirical_risk(K, y, a)}")
        self._a = a

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """Evaluate the decision function for the samples in X.

        Parameters
        ----------
        X : numpy.ndarray of shape (n_samples, n_features)
            The input samples.

        Returns
        -------
        y_score : ndarray of shape (n_samples, )
            Returns the decision function of the sample for each class in the model.
            The decision function is calculated based on the class labels 1 and -1.
        """
        if self.bias:
            X = np.c_[X, np.ones(X.shape[0])]

        K = self._kernelize(X, self._Xfit)
        y_score = K @ self._a

        return y_score

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Perform classification on samples in X.

        Parameters
        ----------
        X : numpy.ndarray of shape (n_samples, n_features)

        Returns
        -------
        y_pred : ndarray of shape (n_samples,)
            Class labels for samples in X.
        """
        y_score = self.decision_function(X)
        y_pred = np.where(y_score > 0, 1, -1)
        y_pred = np.where(y_pred == 1, self._classes[1], self._classes[-1])

        return y_pred

