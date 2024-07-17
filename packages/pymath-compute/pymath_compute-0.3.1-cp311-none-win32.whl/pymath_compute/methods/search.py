"""
Implement Search methods with compatibility
for the Variables and MathExpression
"""
from typing import Optional
from time import time
# Local imports
from pymath_compute import MathExpression, Variable


def binary_search(
    expression: MathExpression,
    var: Variable,
    tol: float,
    solver_time: float | int
) -> tuple[float, int]:
    """..."""
    # Get the epsilon method
    epsilon: float = 1e-5
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
        # Try to get the tolerance and the timing
        if (b - a) <= tol:
            solution_found = True
        if time() - start_method_time > solver_time:
            solution_found = True
        # For this method, we'll get the middle point a and b
        middle_point = (a + b) / 2
        # With this, get the new x1 and x2
        x1 = middle_point - epsilon
        x2 = middle_point + epsilon
        # Evaluate the expression using this two values
        f1 = expression.evaluate({var.name: x1})
        f2 = expression.evaluate({var.name: x2})
        if f1 < f2:
            b = x1
            # Leaving the mark as
            # [a, x1]
        else:
            a = x2
            # Leaving the new mark as
            # [x2, b]
        # Increase the number of iterations
        num_iterations += 1
    # Return the last middle point
    return (a + b) / 2, num_iterations


def fibonacci_search(
    expression: MathExpression,
    var: Variable,
    tol: float,
    solver_time: float | int
) -> tuple[float, int]:
    """..."""
    # Number of iterations
    N = 100
    # Calculate the Fibonacci values
    fib = _fibonacci(n=N)
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
        # Try to get the tolerance and the timing
        if (b - a) <= tol:
            solution_found = True
        if time() - start_method_time > solver_time:
            solution_found = True
        # For this method, we'll get the middle point a and b
        middle_point = b - a
        # With this, get the new x1 and x2
        x1 = a + fib[N-2] / fib[N] * middle_point
        x2 = a + fib[N-1] / fib[N] * middle_point
        # Evaluate the expression using this two values
        f1 = expression.evaluate({var.name: x1})
        f2 = expression.evaluate({var.name: x2})
        if f1 < f2:
            b = x1
            # Leaving the mark as
            # [a, x1]
        else:
            a = x2
            # Leaving the new mark as
            # [x2, b]
        # Reduce the N value -1
        N -= 1
        # Increase the number of iterations
        num_iterations += 1
    # Return the last middle point
    return (a + b) / 2, num_iterations


def _fibonacci(
    n: int,
    values: Optional[dict[int, int]] = None
) -> dict[int, int]:
    # Instance the dictionary
    if values is None:
        values = {0: 0, 1: 1, 2: 1}
    # Get fibonacci for n-1
    if n-1 not in values:
        values = _fibonacci(n-1, values)
    # Do the same with n-2
    if n-2 not in values:
        values = _fibonacci(n-2, values)
    fib_1 = values[n-1]
    fib_2 = values[n-2]
    # Get the value for n
    n_value = fib_2 + fib_1
    values[n] = n_value
    return values
