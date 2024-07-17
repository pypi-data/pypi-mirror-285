"""
Include different training methods from the Engine
"""
import time
from typing import Callable
from copy import copy
# Extra imports
from scipy.misc import derivative
import numpy as np
# Engine imports
# from pymath_compute_engine import gradient_descent as __gradient_descent
# Local imports
from pymath_compute.model import Variable


def __derivate(
    x: float,
    variable: Variable,
    variables: list[Variable],
    objective_func: Callable[[list[Variable]], int | float],
) -> float:
    """..."""
    new_variables = []
    # Get the variable from the list
    for _v in variables:
        new_var = copy(_v)
        if _v == variable:
            if x <= variable.lower_bound:
                new_var.lower_bound = x
            if x >= variable.upper_bound:
                new_var.upper_bound = x
            new_var.value = x
        new_variables.append(new_var)
    return objective_func(new_variables)


def __finite_difference(
    func: Callable[[list[Variable]], int | float],
    variables: list[Variable]
) -> dict[Variable, float]:
    """..."""
    derivate = {}
    # Calculate the derivate for each func
    for variable in variables:
        derivate[variable] = __derivate(
            variable.value, variable, variables, func
        )
    return derivate


def gradient_descent(
    variables: list[Variable],
    objective_func: Callable[[list[Variable]], int | float],
    solver_time: int,
    learning_rate: float = 0.0001,
    tol: float = 1e-5
) -> tuple[float, list[Variable]]:
    """..."""
    # Use the Gradient descent method here
    exc_time = time.time()
    # Get the values for the best cost
    best_values = {}
    # For each variable, get the lower value of their limits
    for variable in variables:
        variable.value = variable.lower_bound
        best_values[variable] = variable.value
    # Then, get the initial solution using this parameter
    best_cost = objective_func(variables)
    # Use the solutions to print how many solutions you've got
    solution = 0
    # Then, try to solve the problem
    optimal_found = False
    no_more_solutions = False
    while all([
        time.time() - exc_time < solver_time,
        optimal_found is False,
        no_more_solutions is False
    ]) is True:
        # Iterate over the values of the current variables, getting the
        # gradient for each variable and obtaining the new variable value
        gradient = __finite_difference(objective_func, variables)
        for variable in variables:
            new_var_value = variable.value + \
                learning_rate * gradient[variable]
            if new_var_value > variable.upper_bound:
                no_more_solutions = True
            # If the value is l
            else:
                variable.value = new_var_value
        # With this, obtain the new cost
        new_cost = objective_func(variables)
        # And compare it.
        if abs(new_cost - best_cost) < tol:
            optimal_found = True
        # If the new cost is lower than the best cost, then
        # add that as the new general cost
        if new_cost < best_cost:
            best_cost = new_cost
            best_values.update({
                variable: variable.value
                for variable in variables
            })
            solution += 1
            print(
                f"Solution {solution} found in" +
                f" {round(time.time() - exc_time,4)}s" +
                f" with cost {best_cost}"
            )

    # Be sure to return the best values
    for variable, best_value in best_values.items():
        variable.value = best_value
    # At the very end, return the variables
    return best_cost, variables
