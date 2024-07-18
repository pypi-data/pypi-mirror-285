"""Leaf Models in sklearn.

This model is based on a DecisionTreeRegressor. When you train the model, it
first uses a DecisionTreeRegressor to divide the data set into leaves, then fits
your model to each leaf.
"""

import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn import clone


class LeafModelRegressor(DecisionTreeRegressor):
    """An sklearn Leaf Model class."""

    def __init__(self, leaf_model, **kwargs):
        """Initialize a LeafModel.
        LEAF_MODEL is an sklearn estimator.
        """

        self.leaf_model = leaf_model
        super().__init__(**kwargs)

    def fit(self, X, y):
        """Fit the model.

        First we fit the decision tree. Then we fit the leaves in the tree to
        the leaf_model. Each leaf gets its own model.

        This is not an optimal fit, I assume the decision tree would make
        different splits if it was using leaf model errors instead of average
        errors. It works pretty well though.
        """
        self.xtrain = X
        self.ytrain = y
        super().fit(X, y)

        # Now train the leaf models
        leaves = self.apply(self.xtrain)
        self.leaf_models = {}

        for leaf in set(leaves):
            # get the x,y-points for this leaf, generate the features you might
            # want to store this data, in case you need it for UQ
            _X = self.xtrain[leaves == leaf]
            _y = self.ytrain[leaves == leaf]

            # This is the model for this leaf
            self.leaf_models[leaf] = clone(self.leaf_model)
            self.leaf_models[leaf].fit(_X, _y)

        return self

    def predict(self, X, return_std=False):
        """Predict values for X.

        if RETURN_STD is truthy, try to get a stderr from the leaf models.
        """

        # Get leaves for X that we are predicting
        pleaves = self.apply(X)

        predictions = np.zeros(X.shape[0])
        errors = np.zeros(X.shape[0])

        for leaf in set(pleaves):

            model = self.leaf_models[leaf]

            ind = pleaves == leaf
            try:
                py, pse = model.predict(X[ind], return_std=return_std)

            # if the model doesn't accept return_std you get TypeError
            # we just catch it here.
            except (ValueError, TypeError):
                py = model.predict(X[ind])
                pse = np.empty(py.shape) * np.nan
            predictions[ind] = py
            errors[ind] = pse

        if return_std:
            return np.array(predictions), np.array(errors)
        else:
            return np.array(predictions)
