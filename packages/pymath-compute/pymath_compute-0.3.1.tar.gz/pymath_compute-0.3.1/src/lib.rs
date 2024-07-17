//! Library export for Python modules
//!
// Import the methods module here
mod math_utilities;
mod methods;
// Import methods
use math_utilities::*;
use methods::*;
use pyo3::prelude::*;

/// Mathematical engine for all heavy mathematical computations
/// made it in Rust. This engine allow us to implement and use
/// different functions or optimization methods in Python code,
/// allowing us to have an increase in the execution time and
/// in the convergence.
///  
/// The modules now includes in this engine are:
///     - methods: Include different set of methods
#[pymodule]
fn engine(py: Python, m: &PyModule) -> PyResult<()> {
    // Call all the modules and append those modules to the main module //
    // MODULE METHODS.
    let optimization = build_optimization_module(py)?;
    let utils = build_utils_module(py)?;
    // ================================================================= //
    // Add all the PyModules to the main m module                        //
    // ================================================================= //
    m.add_submodule(optimization)?;
    m.add_submodule(utils)?;
    // Add the modules to sys
    py.import("sys")?
        .getattr("modules")?
        .set_item("pymath_compute.engine.optimization_methods", optimization)?;
    py.import("sys")?
        .getattr("modules")?
        .set_item("pymath_compute.engine.utils", utils)?;
    // Return the result of the module at the very end                   //
    Ok(())
}

/// Include several optimization methods to handle the optimization
/// of different functions
fn build_optimization_module(py: Python) -> Result<&PyModule, PyErr> {
    // Let's add a new submodule for the methods
    let methods_module = PyModule::new(py, "optimization_methods")?;
    // Add the methods inside here
    methods_module.add_function(wrap_pyfunction!(
        training::gradient_descent,
        methods_module
    )?)?;
    // Return the methods module
    Ok(methods_module)
}

/// Include several utilities for mathematics, such as the derivate methods
/// of different functions
fn build_utils_module(py: Python) -> Result<&PyModule, PyErr> {
    // Let's add a new submodule for the methods
    let utils_module = PyModule::new(py, "utils")?;
    // ======================================== //
    // Add the submodule of derivate here       //
    // ======================================== //
    let sub_derivate_module = PyModule::new(py, "derivate")?;
    sub_derivate_module.add_function(wrap_pyfunction!(
        derivate::compute_gradient,
        sub_derivate_module
    )?)?;

    // Add the methods inside here
    utils_module.add_submodule(sub_derivate_module)?;
    py.import("sys")?
        .getattr("modules")?
        .set_item("pymath_compute.engine.utils.derivate", sub_derivate_module)?;
    // Return the methods module
    Ok(utils_module)
}
