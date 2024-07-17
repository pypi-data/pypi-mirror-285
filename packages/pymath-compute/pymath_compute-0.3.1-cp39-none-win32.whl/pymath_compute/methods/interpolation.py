"""
Implement Interpolation methods with compatibility
for the Variables and MathExpression
"""
import numpy as np
# Local imports
from pymath_compute import MathExpression, Variable


def quadratic_interpolation(
    expression: MathExpression,
    var: Variable,
    _tol: float,
    _solver_time: float | int
) -> tuple[float, int]:
    """..."""
    # Get the values of a and b
    a = var.lower_bound
    b = var.upper_bound
    # Get the middle point between them
    c = (a + b) / 2
    # Get the mean x
    x_mean = (a + b + c) / 3
    # Get the initial three points of
    f0 = expression.evaluate({var.name: a})
    f1 = expression.evaluate({var.name: c})
    f2 = expression.evaluate({var.name: b})
    # Then, get an array for a matrix A to solve this using matrix
    matrix_a = np.array([
        [1, a, a**2],
        [1, c, c**2],
        [1, b, b**2]
    ])
    matrix_b = np.array([f0, f1, f2])
    # Get the coefficients
    coeffs = np.linalg.solve(matrix_a, matrix_b)
    a0, a1, a2 = coeffs
    return a0 + a1 * x_mean + a2 * x_mean**2, 1


def cubic_interpolation(
    expression: MathExpression,
    var: Variable,
    _tol: float,
    _solver_time: float | int
) -> tuple[float, int]:
    """..."""
    # Get the values of a and b
    a = var.lower_bound
    b = var.upper_bound
    # Get the middle point between them
    middle_point = (a + b) / 4
    c = (a + b) / 2 - middle_point
    d = (a + b) / 2 + middle_point
    # Get the mean x
    x_mean = (a + b + c + d) / 4
    # Get the initial three points of
    f0 = expression.evaluate({var.name: a})
    f1 = expression.evaluate({var.name: c})
    f2 = expression.evaluate({var.name: d})
    f3 = expression.evaluate({var.name: b})
    # Then, get an array for a matrix A to solve this using matrix
    matrix_a = np.array([
        [1, a, a**2,  a**3],
        [1, c, c**2, c**3],
        [1, d, d**2, d**3],
        [1, b, b**2, b**3],
    ])
    matrix_b = np.array([f0, f1, f2, f3])
    # Get the coefficients
    coeffs = np.linalg.solve(matrix_a, matrix_b)
    a0, a1, a2, a3 = coeffs
    return a0 + a1 * x_mean + a2 * x_mean**2 + a3 * x_mean**3, 1
