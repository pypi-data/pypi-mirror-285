"""
Test the gradient descent method
"""
import pytest
# Local imports
from pymath_compute.solvers.opt_solver import OptSolver
from pymath_compute.model.variable import Variable
from pymath_compute.methods import OptMethods


def obj_func(variables: dict[str, float]) -> int | float:
    """Objective function that sums all the variables of the vars"""
    return sum(v for v in variables.values())


def create_solver(
    variables: list[Variable],
) -> OptSolver:
    """Create an instance of the solver"""
    # Instance the solver
    solver = OptSolver()
    # Set the variables
    solver.set_variables(variables)
    solver.set_objective_function(obj_func)
    solver.set_solver_config({
        "solver_time": 10,
        "solver_method": OptMethods.GRADIENT_DESCENT
    })
    return solver


@pytest.mark.opt_methods
def test_just_one_variable() -> None:
    """Using the Gradient Descent, obtain the minimization of
    the sum of one variable
    """
    variables = [
        Variable(name="x", lb=1, v0=10)
    ]
    # Create the solver
    solver = create_solver(variables)
    # Run the solution. This should give a RunTime error
    # since we cannot calculate the gradient of just one variable
    solver.solve()
    # Then, the status should be UNFEASIBLE
    assert solver.status == "UNFEASIBLE"


@pytest.mark.opt_methods
def test_just_two_variable() -> None:
    """Using the Gradient Descent, obtain the minimization of
    the sum of two variables
    """
    variables = [
        Variable(name="x", lb=1, v0=10),
        Variable(name="y", lb=1, v0=15)
    ]
    # Create the solver
    solver = create_solver(variables)
    # Run the solution
    solver.solve()
    # Get the results
    result = solver.vars_results()
    # Ensure that the value of the sum of variables values is 2, for both
    assert sum(v.value for v in result) == 2
