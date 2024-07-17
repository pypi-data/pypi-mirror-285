# Examples of the Algorithm

These are some of the examples of how you can use this package to solve different mathematical problems.

## Examples

### Example 1: Basic Optimization

This example demonstrates how to set up and solve a basic optimization problem.

```python
from pymath_compute import Variable
from pymath_compute.solvers.opt_solver import OptSolver
from pymath_compute.methods import OptMethods

# Define the objective function
def simple_objective(variables: list[Variable]) -> float:
    return sum(var.value for var in variables)

# Create variables
variables = [Variable(name=f"Var_{i}", value=i*2) for i in range(5)]

# Initialize the solver
solver = OptSolver()

# Set the variables
solver.set_variables(variables)

# Set the objective function
solver.set_objective_function(simple_objective)

# Configure the solver
solver.set_solver_config({
    "solver_time": 10,
    "solver_method": OptMethods.GRADIENT_DESCENT
})

# Solve the optimization problem
solver.solve()

# Retrieve and print the results
print(f"Solver status: {solver.status}")
for var in solver.vars_results():
    print(f"{var.name}: {var.value}")
```

### Example 2: Advanced Usage with Custom Functions

This example demonstrates a more advanced use case with a custom objective function involving the area of a revolution solid.

```python
from functools import partial
import numpy as np
from pymath_compute import Variable
from pymath_compute.solvers.opt_solver import OptSolver
from pymath_compute.methods import OptMethods

def f(x: float) -> float:
    return np.exp(-x**2)

def approx_derivate(variables: list[float], index: int, dx: float) -> float:
    if index == len(variables) - 1:
        next_var = variables[index - 1] - (4 * dx) / np.e
        prev_var = variables[index - 1]
    elif index == 0:
        next_var = variables[index + 1]
        prev_var = variables[index + 1] + (4 * dx) / np.e
    else:
        next_var = variables[index + 1]
        prev_var = variables[index - 1]
    return (next_var - prev_var) / (2 * dx)

def objective_function(variables: dict[str, float], dx: float) -> float:
    values_of_vars = list(variables.values())
    var_sum = sum(
        var_value * np.sqrt(1 + approx_derivate(values_of_vars, i, dx)**2)
        for i, var_value in enumerate(values_of_vars)
    )
    return 2 * np.pi * var_sum

# Define the array of variables
f_variables = []
X0, XF, X_STEP = -1, 1, 0.001
N_VARS = int((XF - X0) / X_STEP)
X_LINSPACE = np.linspace(X0, XF, N_VARS)

for i in range(N_VARS):
    variable = Variable(name=f"Var_{i+1}")
    variable.value = f(X_LINSPACE[i])
    f_variables.append(variable)

# Initialize the solver
solver = OptSolver()
solver.set_variables(variables=f_variables)
solver.set_objective_function(partial(objective_function, dx=X_STEP))
solver.set_solver_config({
    "solver_time": 30,
    "solver_method": OptMethods.GRADIENT_DESCENT
})

# Solve the optimization problem
solver.solve()

# Evaluate the status and print results
print(f"The status is {solver.status}")
results = solver.vars_results()
for var in results:
    print(f"{var.name}: {var.value}")
```
