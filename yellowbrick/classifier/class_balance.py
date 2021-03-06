
from .base import ClassificationScoreVisualizer
from ..style.palettes import color_palette

import numpy as np
import matplotlib.pyplot as plt

from sklearn.cross_validation import train_test_split
from sklearn.metrics import precision_recall_fscore_support


##########################################################################
## Class Balance Chart
##########################################################################

class ClassBalance(ClassificationScoreVisualizer):
    """
    Class balance chart that shows the support for each class in the
    fitted classification model displayed as a bar plot. It is initialized
    with a fitted model and generates a class balance chart on draw.

    Parameters
    ----------

    ax: axes
        the axis to plot the figure on.

    model: estimator
        Scikit-Learn estimator object. Should be an instance of a classifier,
        else ``__init__()`` will raise an exception.

    classes: list
        A list of class names for the legend. If classes is None and a y value
        is passed to fit then the classes are selected from the target vector.

    kwargs: dict
        Keyword arguments passed to the super class. Here, used
        to colorize the bars in the histogram.

    These parameters can be influenced later on in the visualization
    process, but can and should be set as early as possible.
    """
    def __init__(self, model, ax=None, classes=None, **kwargs):

        super(ClassBalance, self).__init__(model, ax=ax, **kwargs)

        self.colors    = color_palette(kwargs.pop('colors', None))
        self.classes_  = classes

    def fit(self, X, y=None, **kwargs):
        """
        Parameters
        ----------

        X : ndarray or DataFrame of shape n x m
            A matrix of n instances with m features

        y : ndarray or Series of length n
            An array or series of target or class values

        kwargs: keyword arguments passed to Scikit-Learn API.

        Returns
        -------
        self : instance
            Returns the instance of the classification score visualizer

        """
        super(ClassBalance, self).fit(X, y, **kwargs)
        if self.classes_ is None:
            self.classes_ = self.estimator.classes_
        return self

    def score(self, X, y=None, **kwargs):
        """
        Generates the Scikit-Learn precision_recall_fscore_support

        Parameters
        ----------

        X : ndarray or DataFrame of shape n x m
            A matrix of n instances with m features

        y : ndarray or Series of length n
            An array or series of target or class values

        Returns
        -------

        ax : the axis with the plotted figure
        """
        y_pred = self.predict(X)
        self.scores  = precision_recall_fscore_support(y, y_pred)
        self.support = dict(zip(self.classes_, self.scores[-1]))
        return self.draw()

    def draw(self):
        """
        Renders the class balance chart across the axis.

        Returns
        -------

        ax : the axis with the plotted figure

        """
        # Create the axis if it doesn't exist
        if self.ax is None:
            self.ax = plt.gca()

        #TODO: Would rather not have to set the colors with this method.
        # Refactor to make better use of yb_palettes module?

        colors = self.colors[0:len(self.classes_)]
        plt.bar(np.arange(len(self.support)), self.support.values(), color=colors, align='center', width=0.5)

        return self.ax

    def finalize(self, **kwargs):
        """
        Finalize executes any subclass-specific axes finalization steps.
        The user calls poof and poof calls finalize.

        Parameters
        ----------
        kwargs: generic keyword arguments.

        """

        # Set the title
        self.set_title('Class Balance for {}'.format(self.name))

        # Set the x ticks with the class names
        # TODO: change to the self.ax method rather than plt.xticks
        plt.xticks(np.arange(len(self.support)), self.support.keys())

        # Compute the ceiling for the y limit
        cmax, cmin = max(self.support.values()), min(self.support.values())
        self.ax.set_ylim(0, cmax + cmax* 0.1)

def class_balance(model, X, y=None, ax=None, classes=None, **kwargs):
    """Quick method:

    Displays the support for each class in the
    fitted classification model displayed as a bar plot.

    This helper function is a quick wrapper to utilize the ClassBalance
    ScoreVisualizer for one-off analysis.

    Parameters
    ----------
    X  : ndarray or DataFrame of shape n x m
        A matrix of n instances with m features.

    y  : ndarray or Series of length n
        An array or series of target or class values.

    ax : matplotlib axes
        The axes to plot the figure on.

    model : the Scikit-Learn estimator (should be a classifier)

    classes : list of strings
        The names of the classes in the target

    Returns
    -------
    ax : matplotlib axes
        Returns the axes that the class balance plot was drawn on.
    """
    # Instantiate the visualizer
    visualizer = ClassBalance(model, ax, classes, **kwargs)

    # Create the train and test splits
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Fit and transform the visualizer (calls draw)
    visualizer.fit(X_train, y_train, **kwargs)
    visualizer.score(X_test, y_test)

    # Return the axes object on the visualizer
    return visualizer.ax
