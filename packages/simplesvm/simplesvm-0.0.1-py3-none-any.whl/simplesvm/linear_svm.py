import numpy as np
import numpy.linalg as LA


class LinearSVM:
    def __init__(
        self,
        lam: float = 0.01,
        n_iters: int = 5000,
        learning_rate: float = 0.01,
        bias=True,
        verbose=False,
    ):
        """Linear Support Vector Machine (SVM) for Binary Classification.

        Parameters
        ----------
        lam : float, default=0.01
            Regularization parameter.
        n_iters : int, default=5000
            Number of iterations for the gradient descent.
        learning_rate : float, default=0.01
            Learning rate for the gradient descent.
        bias : bool, default=True
            Whether to include a bias term in the input matrix.
        verbose : bool, default=False
            If True, print progress messages during the gradient descent.
        """
        self.lam = lam
        self.n_iters = n_iters
        self.learning_rate = learning_rate
        self.bias = bias
        self.verbose = verbose
        self._classes = {}
        self._w = None

    # Calculate the empirical risk function.
    def _empirical_risk(
        self, X: np.ndarray, y: np.ndarray, w_t: np.ndarray
    ) -> np.ndarray:
        regularzation = 0.5 * self.lam * LA.norm(w_t, ord=2) ** 2
        loss = np.where(1 - y * (X @ w_t) >= 0, 1 - y * (X @ w_t), 0).mean()

        return regularzation + loss

    # Calculate the gradient of the empirical risk function.
    def _empirical_risk_grad(
        self, X: np.ndarray, y: np.ndarray, w_t: np.ndarray
    ) -> np.ndarray:
        regularzation_grad = self.lam * w_t
        loss_grad = (
            (np.where(1 - y * (X @ w_t) >= 0, 1, 0) * -y).reshape(-1, 1) * X
        ).mean(axis=0)

        return regularzation_grad + loss_grad

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fit the Linear SVM model according to the given training data.

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

        # weights
        w = np.ones((X.shape[1]))

        # gradient descent
        for i in range(self.n_iters):
            w = w - self.learning_rate * self._empirical_risk_grad(X, y, w)
            if self.verbose and (i + 1) % 1000 == 0:
                print(f"{i+1:4}: R(w) = {self._empirical_risk(X, y, w)}")
        self._w = w

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """Evaluate the decision function for the samples in X.

        Parameters
        ----------
        X : numpy.ndarray of shape (n_samples, n_features)
            The input samples.

        Returns
        -------
        y_score : ndarray of shape (n_samples,)
            Returns the decision function of the sample for each class in the model.
            The decision function is calculated based on the class labels 1 and -1.
        """
        if self.bias:
            X = np.c_[X, np.ones(X.shape[0])]
        y_score = X @ self._w

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
