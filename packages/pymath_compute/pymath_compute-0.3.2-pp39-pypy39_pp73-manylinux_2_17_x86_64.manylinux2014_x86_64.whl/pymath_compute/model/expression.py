"""
MathExpression implementation module.

This module provides the implementation of the `MathExpression` class, which allows
the creation and manipulation of mathematical expressions involving variables, constants,
and functions. The expressions can be evaluated given a set of variable values.
"""
from typing import Sequence, Optional
# Local import
from pymath_compute.model.types import Operators, MathematicalTerms
from pymath_compute.utils.graph import plot_math_expression


def _generate_terms(
    items: Sequence,
    visited_ids: Optional[list[int]] = None
) -> tuple[list[str], list[int]]:
    """Generate the terms from a list of items"""
    terms = []
    visited_ids = visited_ids if visited_ids else []
    for item in items:
        if id(item) in visited_ids:
            continue
        if isinstance(item, str):
            terms.append(item)
        if type(item).__name__ == "Variable":
            terms.append(item.name)  # type: ignore
        if type(item).__name__ == "MathFunction":
            terms.append(f"{item}")
        if isinstance(item, tuple):
            new_terms, visited_ids = _generate_terms(item, visited_ids)
            terms += new_terms
    # Return the terms
    return terms, visited_ids


def _evaluate(
    items: Sequence,
    values: dict[str, int | float]
) -> float:
    """Evaluate elements in a iterative way"""
    # Define the term
    term = 1
    # Iterate over the items
    for item in items:
        if type(item).__name__ == "Variable":
            term *= values[item.name]
        elif type(item).__name__ == "MathFunction":
            term *= item.evaluate(values)  # type: ignore
        elif isinstance(item, MathExpression):
            term *= item.evaluate(values)
        else:
            term *= _evaluate(item, values)
    return term

class MathExpression:
    """Represents a mathematical expression, that can be a sum of two variables,
    a multiplication, a subtraction and other expressions.

    Attributes:
        terms (MathematicalTerms): The terms of the mathematical expression.
    """
    terms: MathematicalTerms
    __slots__ = ["terms"]

    def __init__(self, terms: MathematicalTerms) -> None:
        self.terms = terms

    def evaluate(self, values: dict[str, int | float]) -> float:
        """From a passed dictionary of values, we'll evaluate the current terms
        expression with that value.

        Example:
            ```
            x = Variable(name="x", lower_bound: 0, upper_bound: 10)
            expr = x + 2
            expr.evaluate({"x": 1}) <- We're setting the value for the name variable defined
            ```

        Args:
            values: dict[str, int | float]: A dict of values using the variable name as key
                and the value to set as the corresponding item for that key
        """
        if not isinstance(values, dict):
            raise TypeError("We're expecting a dict as {VAR_NAME: MATH_VALUE}," +
                            f" but instead we got {type(values)}.")
        # Initialize the result variable
        result: float = 0.0
        for var, coef in self.terms.items():
            # If the var is a constant, don't do
            # anything but adding them to the result
            if var == "const" and isinstance(var, str):
                result += coef
            elif type(var).__name__ == "Variable":
                if var.name not in values:  # type: ignore
                    raise ValueError(
                        "In the given values, we're missing the" +
                        f" following variable '{var.name}'."  # type: ignore
                    )
                result += coef*values[var.name]  # type: ignore
            elif type(var).__name__ == "MathFunction":
                result += coef * var.evaluate(values)  # type: ignore
            else:
                # Define a sub term for this
                result += coef * _evaluate(var, values)  # type: ignore
        # In the end, return the result
        return result

    def plot(  # pylint: disable=R0913
        self,
        *,
        plot_color: str = "black",
        store_as_pdf: bool = False,
        figsize: tuple[int, int] = (10, 6),
        title: str = "",
        xlabel: str = "Variables",
        ylabel: str = "Variable values"
    ) -> None:
        """Plot the Mathematical expression with the corresponding terms"""
        plot_math_expression(self, plot_color=plot_color,
                             store_as_pdf=store_as_pdf, figsize=figsize,
                             xlabel=xlabel, ylabel=ylabel, title=title
                             )

    def __repr__(self) -> str:
        expression: str = "Expression: "
        # Add the terms to print in the representation
        printable_terms: list[str] = []
        for var, coef in self.terms.items():
            if var == "const":
                printable_terms.append(str(coef))
            elif type(var).__name__ == "Variable":
                printable_terms.append(f"{coef}*{var.name}")  # type: ignore
            elif type(var).__name__ == "MathFunction":
                printable_terms.append(f"{coef}*{var}")
            else:
                terms, _ = _generate_terms(var)  # type: ignore
                # Define the str of the term
                term_str = '*'.join(terms)
                # Define the printable terms here
                printable_terms.append(f"{coef}*{term_str}")
        # Return the expression with a join
        return expression + " + ".join(printable_terms)

    # ============================================= #
    #      MATH OPERATIONS REPLACING SECTION        #
    # ============================================= #

    # ////////////////////////// #
    #         ADD METHODS        #
    # ////////////////////////// #
    def __add__(self, other: Operators) -> 'MathExpression':  # pylint: disable=R0912
        # Obtain the new terms
        new_terms = self.terms.copy()
        if type(other).__name__ == "Variable":
            if other in new_terms:
                new_terms[other] += 1  # type: ignore
            else:
                new_terms[other] = 1  # type: ignore
        elif isinstance(other, MathExpression):
            for var, coef in other.terms.items():
                if var in new_terms:
                    new_terms[var] += coef  # type: ignore
                else:
                    new_terms[var] = coef  # type: ignore
        elif type(other).__name__ == "MathFunction":
            if other in new_terms:
                new_terms[other] += 1  # type: ignore
            else:
                new_terms[other] = 1  # type: ignore
        elif isinstance(other, (int, float)):
            if 'const' in new_terms:
                new_terms['const'] += other
            else:
                new_terms['const'] = other
        # If add is not on the expected params
        else:
            raise ValueError(
                f"The param {other} of type {type(other)} is not supported.")
        # Return the new MathExpression
        return MathExpression(new_terms)


    def __radd__(self, other: Operators) -> 'MathExpression':
        return self.__add__(other)

    # ////////////////////////// #
    #   MULTIPLICATION METHODS   #
    # ////////////////////////// #

    def __mul__(self, other: Operators) -> 'MathExpression':
        # Evaluate if the thing to evaluate is a int or a float
        if isinstance(other, (int, float)):
            # Get a new terms expression by multiplying everything that we have
            # for the new other term
            new_terms = {
                var: coef * other
                for var, coef in self.terms.items()
            }
            return MathExpression(new_terms)  # type: ignore
        if type(other).__name__ == "Variable":
            new_terms = {}
            for term, coef in self.terms.items():
                if isinstance(term, tuple):
                    new_terms[term + (other,)] = coef  # type: ignore
                else:
                    new_terms[(term, other)] = coef
            return MathExpression(new_terms)
        if type(other).__name__ == "MathFunction":
            new_terms = self.terms.copy()
            if other in new_terms:
                new_terms[other] += 1  # type: ignore
            else:
                new_terms[other] = 1  # type: ignore
            return MathExpression(new_terms)
        if isinstance(other, MathExpression):
            # Get the new terms
            new_terms = {}
            # Iterate over the terms of this expression
            for o_term, o_coef in other.terms.items():
                for term, coef in self.terms.items():
                    new_terms[(term, o_term)] = coef*o_coef
            return MathExpression(new_terms)
        # If add is not on the expected params
        raise ValueError(
            f"The param {other} of type {type(other)} is not supported.")

    def __rmul__(self, other: Operators) -> 'MathExpression':
        return self.__mul__(other)

    # ////////////////////////// #
    #     SUBTRACT METHODS       #
    # ////////////////////////// #

    def __sub__(self, other: Operators) -> 'MathExpression':
        print(
            type(other).__name__,
            type(other).__name__ in ["Variable", "MathFunction"],
            type(other).__name__ == "Variable"
        )
        # Evaluate that the other parameter is a valid expression
        if not isinstance(other, (int, float, MathExpression)) \
                and not type(other).__name__ in ["Variable", "MathFunction"]:
            raise ValueError(
                f"The param {other} of type {type(other)} is not supported.")

        return self.__add__(-other)  # type: ignore

    def __rsub__(self, other: Operators) -> 'MathExpression':
        # The (-self) invoques the __neg__ method and returns which value
        # we'll expect from it. Since we define the __neg__ method here, we already
        # know that we're going to get a new MathExpression with the negative values.
        return (-self).__add__(other)

    # ////////////////////////// #
    #      NEGATIVE METHODS      #
    # ////////////////////////// #

    def __neg__(self) -> 'MathExpression':
        # Obtain the new negative terms
        new_terms = {var: -coef for var, coef in self.terms.items()}
        return MathExpression(new_terms)  # type: ignore

    # ////////////////////////// #
    #         POW METHODS        #
    # ////////////////////////// #
    def __pow__(self, other: int) -> 'MathExpression':
        if not isinstance(other, int):
            raise ValueError(
                f"The param {other} of type {type(other)} is not supported.")
        if other < 0:
            raise ValueError("The power has to be greater or equal to zero.")
        if other == 0:
            # Make everything 1
            self.terms = {"const": 1}
            return self
        # Multiply the self instance n times
        new_expr: MathExpression = self
        for _ in range(other):
            new_expr = self * self
        # Return it
        return new_expr
