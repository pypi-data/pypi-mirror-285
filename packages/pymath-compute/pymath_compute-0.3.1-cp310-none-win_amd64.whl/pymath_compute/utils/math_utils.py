"""
Different utilities, such as a Gradient calculator
and other minor extra methods
"""
import math
# External imports
import numpy as np
# Local imports
from pymath_compute.model import MathExpression, MathFunction, Variable

available_methods_to_derivative = {
    np.sin: np.cos,
    np.cos: lambda x: -np.sin(x),
    np.exp: np.exp,
    np.log: lambda x: 1/x,
    # Math methods
    math.sin: np.cos,
    math.cos: lambda x: -np.sin(x),
    math.exp: np.exp,
    math.log: lambda x: 1/x
}


def get_gradient(expr: MathExpression, var: Variable) -> MathExpression:
    """Calculate the gradient of the expression with respect
    to the given expression. It is likely a derivative.
    
    This gradient is going to be obtained only for one Variable in the expression

    Args:
        - expr (MathExpression): Expression to get the gradient
        - var (Variable): This is the gradient for which variable.

    Returns:
        - Return a MathExpression
    """
    # Get a dictionary of the new terms
    new_terms = {}
    # And then, iterate over the terms of this expression
    for term, coef in expr.terms.items():
        if term == "const":
            # Ignore the constant
            continue

        if isinstance(term, Variable):
            # If this variable is the same as the one we want to
            # get the gradient...
            if term == var:
                new_terms["const"] = coef
        elif isinstance(term, MathFunction):
            # Get the function of the MathFunction
            func = term.function
            if func not in available_methods_to_derivative:
                raise NotImplementedError(
                    f"The function {func} is not implemented to derivate at this moment."
                )
            # Get the new Math function
            new_math_func = MathFunction(
                available_methods_to_derivative[func],
                var
            )
            # Get the new term for this derivate
            new_terms[new_math_func] = coef
        else:
            term_vars = list(term)  # type: ignore
            if var in term_vars:
                term_vars.remove(var)
                new_terms[tuple(term_vars)] = coef * term_vars.count(var)
    # At the end, return a new math expression with their terms.
    # If they exist, return an expression with those terms
    if new_terms:
        return MathExpression(new_terms)
    # If we do not have any new terms, then return None
    return MathExpression({"const": 0})
