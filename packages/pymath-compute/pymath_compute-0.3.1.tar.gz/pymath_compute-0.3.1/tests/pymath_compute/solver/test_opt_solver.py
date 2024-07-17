"""
Tests for the Optimization Solver.

This solver is the one that allow to the users to easily
implement different optimization methods
"""
import pytest
# Local imports
from pymath_compute.solvers.opt_solver import OptSolver
from pymath_compute.model.variable import Variable


@pytest.mark.opt_solver
def test_try_to_solve_without_params() -> None:
    """Test the execution of the OptSolver when you're
    trying to initialize it and using it without the
    needed parameters, such as the variables, the objective
    or the configuration
    """
    solver = OptSolver()
    # Try to solve it and receive the RunTime Error
    with pytest.raises(RuntimeError):
        solver.solve()
    # Then, add the variables and try to run it without objective
    solver._vars = ["TEST"]  # type: ignore # pylint: disable=W0212
    with pytest.raises(RuntimeError):
        solver.solve()
    # Set a objective
    solver._objective = lambda x: 10 * x  # type: ignore # pylint: disable=W0212
    with pytest.raises(RuntimeError):
        solver.solve()


@pytest.mark.opt_solver
def test_setting_bad_variables() -> None:
    """Test the behaviour of the class when you're setting
    bad variables to the optimizer
    """
    solver = OptSolver()
    # Try to set something that is not a Variable
    # or that is not a list of variables
    with pytest.raises(TypeError):
        solver.set_variables(variables="Test")  # type: ignore
    # Do the same but using a list of Test
    with pytest.raises(TypeError):
        solver.set_variables(variables=["Test"])  # type: ignore


@pytest.mark.opt_solver
def test_bad_objective_function() -> None:
    """Test that happens when you set a function that is not a callable"""
    solver = OptSolver()
    # Using a "Test", we'll have a type error
    with pytest.raises(TypeError):
        solver.set_objective_function("Test")  # type: ignore


@pytest.mark.opt_solver
def test_bad_config() -> None:
    """Test what happens if you did not put correctly the configuration
    of the solver
    """
    solver = OptSolver()
    # First, set something that is not a dict
    with pytest.raises(TypeError):
        solver.set_solver_config("Test")  # type: ignore
    # Then, set something that doesn't have the "solver_method"
    # included
    with pytest.raises(TypeError):
        solver.set_solver_config({"Test": "test"})  # type: ignore
    # Then, add a test where you're setting a solver method
    # that is not of OptMethod type
    with pytest.raises(TypeError):
        solver.set_solver_config({"solver_method": "test"})  # type: ignore


@pytest.mark.opt_solver
def test_status_not_executed() -> None:
    """Test that the status of the solver is NOT_EXECUTED
    if we did not run anything
    """
    solver = OptSolver()
    assert solver.status == "NOT_EXECUTED"


@pytest.mark.opt_solver
def test_set_variables() -> None:
    """Test that we can set variables at different
    moments of time in the solver, and that we'll
    have all those variables at the end
    """
    solver = OptSolver()
    # First, set one variable
    variable = Variable(name="V1")
    solver.set_variables(variable)
    # Assert and ensure that you have only one variable
    assert len(solver._vars) == 1  # pylint: disable=W0212
    # Then, append two vars as a list and ensure that now
    # the length is 3
    variables = [Variable(name="V2"), Variable(name="V3")]
    solver.set_variables(variables)
    assert len(solver._vars) == 3  # pylint: disable=W0212
