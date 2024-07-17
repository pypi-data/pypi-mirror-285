# Basic Usage
---

This is a simple example of how to use the math variables, how they produce a mathematical expression and how we can evaluate the expression with pre-defined values.
from pymath_compute import Variable

## Defining Variables and Mathematical Expressions

```python
from pymath_compute import Variable

# Create a variable
x = Variable(name="x", lower_bound=0, upper_bound=10)

# Create a mathematical expression
expr = x + 2 * x - 5

# Evaluate the expression
values = {"x": 5}
result = expr.evaluate(values)
print(f"Result of the expression: {result}")
```

## Mathematical Operations

PyMathCompute allows various mathematical operations with variables and expressions:

```python
from pymath_compute import Variable

# Create variables
x = Variable(name="x", lower_bound=0, upper_bound=10)
y = Variable(name="y", lower_bound=0, upper_bound=10)

# Create expressions
expr1 = x + y
expr2 = x * 2 + y ** 2

# Evaluate expressions
values = {"x": 3, "y": 4}
result1 = expr1.evaluate(values)
result2 = expr2.evaluate(values)

print(f"Result of expr1: {result1}")
print(f"Result of expr2: {result2}")
```

## Mathematical Operators

PyMathCompute also allow connection with operators, as using `sin`, `cos`, `e`, and others. For this, we use the `MathFunction` parameter

```python
from numpy import np
from pymath_compute import Variable, MathFunction

# Create the variables
x = Variable(name="x", lower_bound=0, upper_bound=np.pi)

# Add a function to calculate the sin of x
sin = MathFunction(np.sin, x)
```