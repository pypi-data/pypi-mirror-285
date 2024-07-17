"""
Tests for the MathFunction class
"""
import pytest
import numpy as np
# Local imports
from pymath_compute.model.function import MathFunction
from pymath_compute.model.variable import Variable
from pymath_compute.model.expression import MathExpression

# Generate a global math function
x = Variable(name="x", lb=0, ub=10)
func_to_test = MathFunction(np.sin, x)


@pytest.mark.function
def test_create_math_function():
    """Test creation of a MathFunction instance.

    This test checks that a MathFunction instance is created correctly
    with the expected function and variable.
    """
    variable = Variable(name="x", lb=0, ub=10)
    math_func = MathFunction(np.sin, variable)
    assert math_func.function == np.sin
    assert math_func.variable == variable


@pytest.mark.function
def test_evaluate_math_function():
    """Test evaluating a MathFunction instance.

    This test checks that a MathFunction instance can be evaluated
    correctly given a set of variable values.
    """
    math_func = func_to_test
    values = {"x": np.pi / 2}
    result = math_func.evaluate(values)
    assert result == np.sin(np.pi / 2)


@pytest.mark.function
def test_repr_math_function():
    """Test the __repr__ method of MathFunction.

    This test checks that the __repr__ method returns a string representation
    of the MathFunction instance.
    """
    math_func = func_to_test
    expected_repr = "sin(x: 0)"
    assert repr(math_func) == expected_repr


@pytest.mark.function
def test_add_method_math_function():
    """Test the __add__ method with another MathFunction.

    This test checks that the __add__ method correctly creates
    a new MathExpression when adding another MathFunction.
    """
    math_func1 = func_to_test
    variable = Variable(name="y", lb=-5, ub=5)
    math_func2 = MathFunction(np.cos, variable)
    new_expr = math_func1 + math_func2
    assert isinstance(new_expr, MathExpression)


@pytest.mark.function
def test_add_method_constant():
    """Test the __add__ method with a constant value.

    This test checks that the __add__ method correctly creates
    a new MathExpression when adding a constant value.
    """
    math_func = func_to_test
    new_expr = math_func + 5
    assert isinstance(new_expr, MathExpression)


@pytest.mark.function
def test_add_method_variable():
    """Test the __add__ method with a Variable instance.

    This test checks that the __add__ method correctly creates
    a new MathExpression when adding a Variable instance.
    """
    math_func = func_to_test
    variable = Variable(name="y", lb=-5, ub=5)
    new_expr = math_func + variable
    assert isinstance(new_expr, MathExpression)


@pytest.mark.function
def test_add_method_invalid_type():
    """Test the __add__ method with an invalid type.

    This test checks that using an invalid type with the __add__
    method raises a ValueError.
    """
    math_func = func_to_test
    with pytest.raises(ValueError):
        _ = math_func + "invalid"  # type: ignore


@pytest.mark.function
def test_radd_method():
    """Test the __radd__ method.

    This test checks that the __radd__ method correctly creates
    a new MathExpression when the variable is on the right-hand side.
    """
    math_func = func_to_test
    new_expr = 5 + math_func
    assert isinstance(new_expr, MathExpression)
