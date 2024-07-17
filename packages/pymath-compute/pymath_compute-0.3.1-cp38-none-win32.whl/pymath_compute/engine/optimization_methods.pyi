"""
Mathematical engine for all heavy mathematical computations
made it in Rust. This engine allow us to implement and use
different functions or optimization methods in Python code,
allowing us to have an increase in the execution time and
in the convergence.
 
The modules now includes in this engine are:
    - methods: Include different set of methods
"""
from typing import Callable, Literal
# Local imports
from pymath_compute.model import Variable

STATUS = Literal["OPTIMAL", "FEASIBLE", "UNFEASIBLE", "NOT_EXECUTED"]


def gradient_descent(
    variables: list[Variable],
    cost_method: Callable[[dict[str, float]], float | int],
    var_step: float,
    learning_rate: float,
    iterations: int,
    tol: float,
) -> STATUS:
    """Gradient Descent implementation
    
    This is a normal gradient descent implementation for a Python code.
    The values of the variables are updated in each iteration of the
    method, only if the old cost is better than the new cost.
    
    Args:
        - variables (list[Variable]): Variables given by the PyMath Module
        - cost_method (Callable): Method to calculate the cost.
        - var_step (float): Finite step to calculate the gradient
        - learning_rate (float): The learning rate for the variables
        - iterations (int): How many iterations are you going to run as max
        - tol (float): The tolerance to know if you got an optimal
    
    Returns:
        - The status of the method
    """
