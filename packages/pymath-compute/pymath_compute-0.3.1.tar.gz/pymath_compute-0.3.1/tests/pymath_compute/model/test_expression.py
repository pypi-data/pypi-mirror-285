"""
Test the MathExpression module
"""
import pytest
# Local imports
from pymath_compute.model.expression import MathExpression
from pymath_compute.model.variable import Variable
from pymath_compute.model.function import MathFunction

# Create the dummy expression
x = Variable("x", 0, 10)
y = Variable("y", -5, 5)
expr_to_test: MathExpression = x + y


@pytest.mark.expression
def test_create_math_expression():
    """Test creation of a MathExpression instance.

    This test checks that a MathExpression instance is created correctly
    with the expected terms.
    """
    terms = {
        Variable("x", 0, 10): 1,
        Variable("y", -5, 5): 2,
        "const": 3,
        MathFunction("sin(x)", lambda x: x): 4,

    }
    expr = MathExpression(terms)
    assert expr.terms == terms


@pytest.mark.expression
def test_evaluate_expression():
    """Test evaluating a MathExpression instance.

    This test checks that a MathExpression instance can be evaluated
    correctly given a set of variable values.
    """
    expr = expr_to_test
    values = {"x": 1, "y": -2}
    result = expr.evaluate(values)
    assert result == -1


@pytest.mark.expression
def test_repr_expression():
    """Test the __repr__ method of MathExpression.

    This test checks that the __repr__ method returns a string representation
    of the MathExpression instance.
    """
    expr = expr_to_test
    expected_repr = (
        "Expression: 1*x + 1*y"
    )
    assert repr(expr) == expected_repr


@pytest.mark.expression
def test_add_method_variable():
    """Test the __add__ method with another Variable instance.

    This test checks that the __add__ method correctly creates
    a new MathExpression when adding another Variable instance.
    """
    expr = expr_to_test
    var = Variable("z", -10, 10)
    new_expr = expr + var
    assert isinstance(new_expr, MathExpression)


@pytest.mark.expression
def test_add_method_expression():
    """Test the __add__ method with another MathExpression.

    This test checks that the __add__ method correctly creates
    a new MathExpression when adding another MathExpression.
    """
    expr1 = expr_to_test
    expr2 = MathExpression({"const": 2})
    new_expr = expr1 + expr2
    assert isinstance(new_expr, MathExpression)


@pytest.mark.expression
def test_add_method_constant():
    """Test the __add__ method with a constant value.

    This test checks that the __add__ method correctly creates
    a new MathExpression when adding a constant value.
    """
    expr = expr_to_test
    new_expr = expr + 5
    assert isinstance(new_expr, MathExpression)


@pytest.mark.expression
def test_add_method_invalid_type():
    """Test the __add__ method with an invalid type.

    This test checks that using an invalid type with the __add__
    method raises a ValueError.
    """
    expr = expr_to_test
    with pytest.raises(ValueError):
        _ = expr + "invalid"  # type: ignore


@pytest.mark.expression
def test_radd_method():
    """Test the __radd__ method.

    This test checks that the __radd__ method correctly creates
    a new MathExpression when the variable is on the right-hand side.
    """
    expr = expr_to_test
    new_expr = 5 + expr
    assert isinstance(new_expr, MathExpression)


@pytest.mark.expression
def test_mul_method_variable():
    """Test the __mul__ method with another Variable instance.

    This test checks that the __mul__ method correctly creates
    a new MathExpression when multiplying by another Variable instance.
    """
    expr = expr_to_test
    var = Variable("z", -10, 10)
    new_expr = expr * var
    assert isinstance(new_expr, MathExpression)


@pytest.mark.expression
def test_mul_method_expression():
    """Test the __mul__ method with another MathExpression.

    This test checks that the __mul__ method correctly creates
    a new MathExpression when multiplying by another MathExpression.
    """
    expr1 = expr_to_test
    expr2 = MathExpression({"const": 2})
    new_expr = expr1 * expr2
    assert isinstance(new_expr, MathExpression)


@pytest.mark.expression
def test_mul_method_constant():
    """Test the __mul__ method with a constant value.

    This test checks that the __mul__ method correctly creates
    a new MathExpression when multiplying by a constant value.
    """
    expr = expr_to_test
    new_expr = expr * 5
    assert isinstance(new_expr, MathExpression)


@pytest.mark.expression
def test_mul_method_invalid_type():
    """Test the __mul__ method with an invalid type.

    This test checks that using an invalid type with the __mul__
    method raises a ValueError.
    """
    expr = expr_to_test
    with pytest.raises(ValueError):
        _ = expr * "invalid"  # type: ignore


@pytest.mark.expression
def test_rmul_method():
    """Test the __rmul__ method.

    This test checks that the __rmul__ method correctly creates
    a new MathExpression when the variable is on the right-hand side.
    """
    expr = expr_to_test
    new_expr = 5 * expr
    assert isinstance(new_expr, MathExpression)


@pytest.mark.expression
def test_sub_method_variable():
    """Test the __sub__ method with another Variable instance.

    This test checks that the __sub__ method correctly creates
    a new MathExpression when subtracting another Variable instance.
    """
    expr = expr_to_test
    var = Variable("z", -10, 10)
    new_expr = expr - var
    assert isinstance(new_expr, MathExpression)


@pytest.mark.expression
def test_sub_method_expression():
    """Test the __sub__ method with another MathExpression.

    This test checks that the __sub__ method correctly creates
    a new MathExpression when subtracting another MathExpression.
    """
    expr1 = expr_to_test
    expr2 = MathExpression({"const": 2})
    new_expr = expr1 - expr2
    assert isinstance(new_expr, MathExpression)


@pytest.mark.expression
def test_sub_method_invalid_type():
    """Test the __sub__ method with an invalid type.

    This test checks that using an invalid type with the __sub__
    method raises a ValueError.
    """
    expr = expr_to_test
    with pytest.raises(ValueError):
        _ = expr - "invalid"  # type: ignore


@pytest.mark.expression
def test_rsub_method():
    """Test the __rsub__ method.

    This test checks that the __rsub__ method correctly creates
    a new MathExpression when the variable is on the right-hand side.
    """
    expr = expr_to_test
    new_expr = 5 - expr
    assert isinstance(new_expr, MathExpression)


@pytest.mark.expression
def test_neg_method():
    """Test the __neg__ method.

    This test checks that the __neg__ method correctly creates
    a new MathExpression for the negation of the expression.
    """
    expr = expr_to_test
    neg_expr = -expr
    assert isinstance(neg_expr, MathExpression)


@pytest.mark.expression
def test_invalid_add_method():
    """Test adding an invalid type with __add__ method.

    This test checks that adding an invalid type with the __add__
    method raises a ValueError.
    """
    expr = expr_to_test
    with pytest.raises(ValueError):
        _ = expr + "invalid"  # type: ignore


@pytest.mark.expression
def test_pow_method():
    """Test the __pow__ method.

    This test checks that the __pow__ method correctly creates
    a new MathExpression for raising the expression to a power.
    """
    expr = expr_to_test
    new_expr = expr ** 2
    assert isinstance(new_expr, MathExpression)


@pytest.mark.expression
def test_pow_method_with_zero():
    """Test the __pow__ method with an invalid power value.

    This test checks that using an invalid power value with the
    __pow__ method raises a ValueError.
    """
    expr = expr_to_test
    # Evaluate it using 0
    new_expr = expr ** 0
    assert new_expr.evaluate({}) == 1


@pytest.mark.expression
def test_pow_method_invalid_type():
    """Test the __pow__ method with an invalid type.

    This test checks that using an invalid type with the __pow__
    method raises a ValueError.
    """
    expr = expr_to_test
    with pytest.raises(ValueError):
        _ = expr ** "invalid"  # type: ignore


@pytest.mark.expression
def test_pow_method_invalid_value():
    """Test the __pow__ method with an invalid power value.

    This test checks that using an invalid power value with the
    __pow__ method raises a ValueError.
    """
    expr = expr_to_test
    with pytest.raises(ValueError):
        _ = expr ** -2  # type: ignore
