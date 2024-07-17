//! Trainable methods for Optimization
//!
//! Provides different methods that include training, such as:
//!     - Gradient Descendent
//!
use pyo3::prelude::*;
use pyo3::types::PyDict;
// Module imports //
use crate::math_utilities::derivate::compute_gradient;

/// Gradient Descent implementation
///
/// This is a normal gradient descent implementation for a Python code.
/// The values of the variables are updated in each iteration of the
/// method, only if the old cost is better than the new cost.
///
/// Args:
///     - variables (Vec<&PyAny>): Variables given by the PyMath Module
///     - cost_method (PyObject): Method to calculate the cost.
///     - var_step (float): Finite step to calculate the gradient
///     - learning_rate (float): The learning rate for the variables
///     - iterations (int): How many iterations are you going to run as max
///     - tol (float): The tolerance to know if you got an optimal
///
/// Returns:
///     - The status of the method
#[pyfunction]
pub fn gradient_descent(
    py: Python,
    variables: Vec<&PyAny>,
    cost_method: PyObject,
    var_step: f64,
    learning_rate: f64,
    iterations: i64,
    tol: f64,
) -> PyResult<&'static str> {
    // Get the initial var values and the best cost so far
    let var_values = PyDict::new(py);
    for variable in &variables {
        let name: String = variable.getattr("name")?.extract()?;
        let value: f64 = variable.getattr("value")?.extract()?;
        var_values.set_item(name, value)?;
    }
    let mut best_cost: f64 = cost_method.call1(py, (var_values,))?.extract(py)?;
    // Calculate the initial cost for the variables
    // Begin creating the iter_exec, that is going to count the iterations executed
    let mut iter_exec: i64 = 0;
    let mut status: &str = "UNFEASIBLE";
    while iter_exec <= iterations {
        // Get a vector of the values
        let var_vec: Vec<f64> = var_values
            .values()
            .iter()
            .map(|v| v.extract::<f64>().unwrap())
            .collect();
        // Get the gradient
        let gradient = compute_gradient(var_vec.clone(), var_step)?;
        // Iterate over each value, and get the new optimized value
        let mut var_index = 0;
        for (var_name, var_value) in var_values.items().extract::<Vec<(String, f64)>>().unwrap() {
            var_values.set_item::<&str, f64>(
                &var_name,
                var_value - learning_rate * gradient[var_index],
            )?;
            // Add one value to the var index
            if var_index < gradient.len() - 1 {
                var_index += 1;
            }
        }
        // Calculate the new cost
        let cost: f64 = cost_method.call1(py, (var_values,))?.extract(py)?;
        // Compare the new and the best cost. If the new diff is lower than the
        // tolerance, then we'll break this since we've found the optimal.
        // In the other hand, if still we don't break the tolerance, but we have
        // have a new cost that is lower than the current best cost, then it's
        // time to update the best cost
        if (best_cost - cost).abs() < tol {
            status = "OPTIMAL";
            break;
        } else if cost < best_cost {
            let mut recalculate_cost: bool = false;
            for variable in &variables {
                let name: &str = variable.getattr("name")?.extract()?;
                let new_value: f64 = var_values.get_item(name).unwrap().extract()?;
                // Use the setter method to set the new value
                variable.setattr("value", new_value)?;
                // Get the value
                let var_value: f64 = variable.getattr("value")?.extract()?;
                if var_value != new_value {
                    var_values
                        .set_item::<&str, f64>(name, variable.getattr("value")?.extract()?)?;
                    // Ask to recalculate the cost
                    recalculate_cost = true
                }
            }
            if recalculate_cost {
                // Recalculate the cost, in case that we have changed the variables
                best_cost = cost_method.call1(py, (var_values,))?.extract(py)?;
            } else {
                best_cost = cost;
            }
            // Change the status to FEASIBLE
            status = "FEASIBLE";
        }
        // Add one iteration at the end
        iter_exec += 1;
    }
    // Return the variables at the end
    Ok(status)
}
