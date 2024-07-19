"""
Implement a generic code that allows us to graph a mathematical expression and a given value.

This module provides functions to obtain variables from a mathematical expression and to plot 
a mathematical expression with specified limits for the variables.

Classes:
    VarsLimit: Represents the upper and lower limits to plot an expression.

Functions:
    plot_math_expression:
        Plots a mathematical expression with specified limits for the variables and optional 
        parameters for customization.
"""
from typing import TypedDict, Optional, TYPE_CHECKING
import random
# Required Math imports
import numpy as np
import matplotlib.pyplot as plt
# Local imports
if TYPE_CHECKING:
    from pymath_compute.model.expression import MathExpression
    from pymath_compute.model.variable import Variable

# Add this to allow us to import everything in a LaTex manner
font = {
    'family': 'serif',
    'size': 12,
    'serif':  'Computer Modern'
}


class VarsLimit(TypedDict):
    """Upper and Lower limit to plot an expression"""
    lower_limit: Optional[float]
    upper_limit: Optional[float]


def _get_vars(expression: "MathExpression") -> set["Variable"]:
    """
    Retrieves all variables involved in a mathematical expression.

    Args:
        expression (MathExpression): The mathematical expression from which to extract variables.

    Returns:
        set[Variable]: A set of variables involved in the expression.
    """
    variables: set["Variable"] = set()
    for term in expression.terms.keys():
        if not isinstance(term, tuple):
            term = (term, )  # type: ignore
        for t in term:  # type: ignore
            if type(t).__name__ == "Variable":
                variables.add(t)  # type: ignore
            if type(t).__name__ == "MathFunction":
                if type(t.variable).__name__ == "Variable":  # type: ignore
                    variables.add(t.variable)  # type: ignore
                else:
                    variables = variables | _get_vars(
                        t.variable)  # type: ignore
    # Return the variables obtained
    return variables


def plot_math_expression(  # pylint: disable=R0913
    expr: "MathExpression",
    *,
    plot_color: str = "black",
    store_as_pdf: bool = False,
    figsize: tuple[int, int] = (10, 6),
    title: str = "",
    xlabel: str = "Variables",
    ylabel: str = "Variable values"
) -> None:
    """Plots a mathematical expression with specified limits for
    the variables and optional parameters for customization.

    Args:
        expr (MathExpression): The mathematical expression to plot.
        store_as_pdf (bool, optional): Whether to store the plot as a PDF file. Defaults to False.
        vars_limit (Optional[dict[Variable, VarsLimit]], optional): A dictionary specifying the
            limits for each variable. Defaults to None.
        figsize (tuple[int, int], optional): The size of the figure. Defaults to (10, 6).
        xlabel (str, optional): The label for the x-axis. Defaults to "Variable values".
        ylabel (str, optional): The label for the y-axis. Defaults to "Expression values".
    """
    # From the expression, get the terms inside it
    variables: set["Variable"] = set(  # type: ignore
        var for var in expr.terms.keys()
        if type(var).__name__ == "Variable"
    )

    variables: set["Variable"] = _get_vars(expression=expr)
    # From each of the variable, get a linspace
    expr_values: list[int | float] = []
    for var in variables:
        expr_values.append(var.value)
    # Then, start to plot the figure
    plt.figure(figsize=figsize)
    # Plot the values of each variable
    plt.scatter(
        list(range(1, len(expr_values) + 1)),
        expr_values,
        color=plot_color
    )
    # Add the labels
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title if title else f'Graph of ${expr}$.')
    # Show grid
    plt.grid(True)
    # Decide if you want to store this graph or to show it
    if store_as_pdf is False:
        plt.show()
    else:
        plt.savefig(f'expr_plot_{random.randint(0, 100)}.pdf', format='pdf')
