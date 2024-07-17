"""Unit test for the Variable class
"""

import pytest
from pymath_compute.model.variable import Variable
from pymath_compute.model.expression import MathExpression


# Create a variable as global
variable_to_test: Variable = Variable(name="x", lb=0, ub=10)


@pytest.mark.variable
def test_create_variable():
    """Test creation of a Variable instance.

    This test checks that a Variable instance is created correctly
    with the expected attributes.
    """
    var = Variable("x", 0, 10)
    assert var.name == "x"
    assert var.lower_bound == 0
    assert var.upper_bound == 10
    assert var.value == 0.0


@pytest.mark.variable
def test_create_variable_without_bounds():
    """Test for the creation of a Variable instance.
    
    This test evaluates that if we do not provide any bounds
    then the variable is going to have a unlimited range of values
    """
    var: Variable = Variable("x")
    assert var.name == "x"
    assert var.lower_bound == float("-inf")
    assert var.upper_bound == float("inf")
    # The value should be 0.0
    assert var.value == 0.0


@pytest.mark.variable
def test_create_variable_with_initial_value():
    """Test the creation of a variable with a v0, being the initial value
    of the var
    """
    var: Variable = Variable("x", lb=10, v0=15)
    # Since lb = 10, ub = inf, then it is valid that lb <= v0 <= ub
    assert var.value == 15


@pytest.mark.variable
def test_create_variable_with_initial_value_out_of_bounds():
    """Test the creation of a variable with a v0 that
    is out of the bounds. That means, that the rule
    lb <= v0 <= ub is violated
    """
    # Since lb = 10, ub = 15, then it is not valid that lb <= v0 <= ub
    with pytest.raises(ValueError):
        _: Variable = Variable("x", lb=10, ub=15, v0=0)

@pytest.mark.variable
def test_set_valid_value():
    """Test setting a valid value to a Variable.

    This test checks that a valid value can be set to a Variable
    instance and that it is correctly stored.
    """
    var: Variable = variable_to_test
    var.value = 5.0
    assert var.value == 5.0


@pytest.mark.variable
def test_set_invalid_value():
    """Test setting an invalid value to a Variable.

    This test checks that setting a value outside the defined
    bounds would set the closes bound as the value
    """
    var: Variable = variable_to_test
    var.value = 15.0
    # Evaluate it and confirm that it has, indeed, the upper bound as limit
    assert var.value == var.upper_bound


@pytest.mark.variable
def test_set_invalid_type():
    """Test setting an invalid type value to a Variable.

    This test checks that setting a value of an invalid type
    raises a TypeError.
    """
    var: Variable = variable_to_test
    with pytest.raises(TypeError):
        var.value = "invalid"  # type: ignore


@pytest.mark.variable
def test_add_method_variable():
    """Test the __add__ method with another Variable instance.

    This test checks that the __add__ method correctly creates
    a MathExpression when adding another Variable instance.
    """
    var1 = variable_to_test
    var2 = Variable("y", -5, 5)
    expr = var1 + var2
    assert isinstance(expr, MathExpression)


@pytest.mark.variable
def test_add_method_expression():
    """Test the __add__ method with a MathExpression.

    This test checks that the __add__ method correctly creates
    a MathExpression when adding a MathExpression.
    """
    var: Variable = variable_to_test
    expr = MathExpression({"const": 3}) + var
    assert isinstance(expr, MathExpression)


@pytest.mark.variable
def test_add_method_constant():
    """Test the __add__ method with a constant value.

    This test checks that the __add__ method correctly creates
    a MathExpression when adding a constant value.
    """
    var: Variable = variable_to_test
    expr = var + 5
    assert isinstance(expr, MathExpression)


@pytest.mark.variable
def test_add_method_invalid_type():
    """Test the __add__ method with an invalid type.

    This test checks that using an invalid type with the __add__
    method raises a TypeError.
    """
    var: Variable = variable_to_test
    with pytest.raises(TypeError):
        _ = var + "invalid"  # type: ignore


@pytest.mark.variable
def test_radd_method():
    """Test the __radd__ method.

    This test checks that the __radd__ method correctly creates
    a MathExpression when the variable is on the right-hand side.
    """
    var: Variable = variable_to_test
    expr = 5 + var
    assert isinstance(expr, MathExpression)


@pytest.mark.variable
def test_mul_method_variable():
    """Test the __mul__ method with another Variable instance.

    This test checks that the __mul__ method correctly creates
    a MathExpression when multiplying by another Variable instance.
    """
    var1 = variable_to_test
    var2 = Variable("y", -5, 5)
    expr = var1 * var2
    assert isinstance(expr, MathExpression)


@pytest.mark.variable
def test_mul_method_expression():
    """Test the __mul__ method with a MathExpression.

    This test checks that the __mul__ method correctly creates
    a MathExpression when multiplying by a MathExpression.
    """
    var: Variable = variable_to_test
    expr = MathExpression({"const": 3}) * var
    assert isinstance(expr, MathExpression)


@pytest.mark.variable
def test_mul_method_constant():
    """Test the __mul__ method with a constant value.

    This test checks that the __mul__ method correctly creates
    a MathExpression when multiplying by a constant value.
    """
    var: Variable = variable_to_test
    expr = var * 5
    assert isinstance(expr, MathExpression)


@pytest.mark.variable
def test_mul_method_invalid_type():
    """Test the __mul__ method with an invalid type.

    This test checks that using an invalid type with the __mul__
    method raises a TypeError.
    """
    var: Variable = variable_to_test
    with pytest.raises(TypeError):
        _ = var * "invalid"  # type: ignore


@pytest.mark.variable
def test_rmul_method():
    """Test the __rmul__ method.

    This test checks that the __rmul__ method correctly creates
    a MathExpression when the variable is on the right-hand side.
    """
    var: Variable = variable_to_test
    expr = 5 * var
    assert isinstance(expr, MathExpression)


@pytest.mark.variable
def test_sub_method_variable():
    """Test the __sub__ method with another Variable instance.

    This test checks that the __sub__ method correctly creates
    a MathExpression when subtracting another Variable instance.
    """
    var1 = variable_to_test
    var2 = Variable("y", -5, 5)
    expr = var1 - var2
    assert isinstance(expr, MathExpression)


def test_sub_method_expression():
    """Test the __sub__ method with a MathExpression.

    This test checks that the __sub__ method correctly creates
    a MathExpression when subtracting a MathExpression.
    """
    var: Variable = variable_to_test
    expr = MathExpression({"const": 3}) - var
    assert isinstance(expr, MathExpression)


@pytest.mark.variable
def test_sub_method_invalid_type():
    """Test the __sub__ method with an invalid type.

    This test checks that using an invalid type with the __sub__
    method raises a TypeError.
    """
    var: Variable = variable_to_test
    with pytest.raises(TypeError):
        _ = var - "invalid"  # type: ignore


@pytest.mark.variable
def test_rsub_method():
    """Test the __rsub__ method.

    This test checks that the __rsub__ method correctly creates
    a MathExpression when the variable is on the right-hand side.
    """
    var: Variable = variable_to_test
    expr = 5 - var
    assert isinstance(expr, MathExpression)


@pytest.mark.variable
def test_neg_method():
    """Test the __neg__ method.

    This test checks that the __neg__ method correctly creates
    a MathExpression for the negation of the variable.
    """
    var: Variable = variable_to_test
    expr = -var
    assert isinstance(expr, MathExpression)


@pytest.mark.variable
def test_pow_method():
    """Test the __pow__ method.

    This test checks that the __pow__ method correctly creates
    a MathExpression for raising the variable to a power.
    """
    var: Variable = variable_to_test
    expr = var ** 2
    assert isinstance(expr, MathExpression)


@pytest.mark.variable
def test_pow_method_invalid_type():
    """Test the __pow__ method with an invalid type.

    This test checks that using an invalid type with the __pow__
    method raises a TypeError.
    """
    var: Variable = variable_to_test
    with pytest.raises(TypeError):
        _ = var ** "invalid"  # type: ignore


@pytest.mark.variable
def test_pow_method_invalid_value():
    """Test the __pow__ method with an invalid power value.

    This test checks that using an invalid power value with the
    __pow__ method raises a TypeError.
    """
    var: Variable = variable_to_test
    with pytest.raises(TypeError):
        _ = var ** -2


@pytest.mark.variable
def test_invalid_init_name_type():
    """Test initializing a Variable with an invalid name type.

    This test checks that initializing a Variable with a non-string
    name raises a TypeError.
    """
    with pytest.raises(TypeError):
        Variable(123, 0, 10)  # type: ignore


@pytest.mark.variable
def test_invalid_init_bounds_type():
    """Test initializing a Variable with invalid bounds type.

    This test checks that initializing a Variable with non-numeric
    bounds raises a TypeError.
    """
    with pytest.raises(TypeError):
        Variable("x", "0", 10)  # type: ignore


@pytest.mark.variable
def test_invalid_init_bounds_order():
    """Test initializing a Variable with bounds in wrong order.

    This test checks that initializing a Variable with lower bound
    greater than upper bound raises a ValueError.
    """
    with pytest.raises(ValueError):
        Variable("x", 10, 0)
