"""
Implement Regularity methods with compatibility
for the Variables and MathExpression
"""
from time import time
from functools import partial
from scipy.misc import derivative
# Local imports
from pymath_compute import MathExpression, Variable

def newton_method(
    expression: MathExpression,
    var: Variable,
    tol: float,
    solver_time: float | int
) -> tuple[float, int]:
    """..."""
    # Get the values of a and b
    a = var.lower_bound
    # Get the initial value of x
    x = a
    # Initialize the timing
    start_method_time = time()
    # Initialize the number of iterations
    num_iterations = 0
    # Add the flag for the solution
    solution_found: bool = False
    # Generate the df function
    df = partial(derivate, expression, var)
    while solution_found is False:
        if time() - start_method_time > solver_time:
            solution_found = True
        # Get the df value
        df_value = derivative(df, x, dx=1e-6)
        if abs(df_value) < tol:
            solution_found = True
        # Get the approximated value of x
        x_new = x - (expression.evaluate({var.name: x}) / df_value)
        # Evaluate to see if the break is here
        if abs(x_new - x) < tol:
            solution_found = True
        x = x_new
        # Add one more iteration
        num_iterations += 1
    # Return x
    return x, num_iterations


def bisection_method(
    expression: MathExpression,
    var: Variable,
    tol: float,
    solver_time: float | int
) -> tuple[float, int]:
    """..."""
    # Get the values of a and b
    a = var.lower_bound
    b = var.upper_bound
    # Initialize the timing
    start_method_time = time()
    # Initialize the number of iterations
    num_iterations = 0
    # Add the flag for the solution
    solution_found: bool = False
    while solution_found is False:
        # First, evaluate the tolerance
        if (b - a) / 2 > tol:
            solution_found = True
        if time() - start_method_time > solver_time:
            solution_found = True
        # First, get the middle point
        c = (a + b) / 2
        # Then, evaluate the solution on f(a), f(b) and f(c)
        fa = expression.evaluate({var.name: a})
        fc = expression.evaluate({var.name: c})
        # Now, evaluate the founded solution
        if fc == 0:
            # Break the solution if fc == 0
            solution_found = True
        elif fa * fc < 0:
            b = c
        else:
            # We do not have to make the other operation
            # since we can already know that if it is not
            # one of these cases, then fb * fc < 0
            a = c
        # Add one more iteration
        num_iterations += 1
    # Return the obtained value
    return (a + b) / 2, num_iterations

def derivate(expression: MathExpression, var: Variable, x: float) -> float:
    """..."""
    return expression.evaluate({var.name: x})
