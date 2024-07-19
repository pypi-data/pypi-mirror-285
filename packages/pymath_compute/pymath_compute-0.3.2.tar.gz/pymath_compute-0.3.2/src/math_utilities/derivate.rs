/// Derivatives numerical methods
///
/// This also includes methods such as methods
/// to calculate derivatives or methods to calculate the
/// gradient of an array of numbers
///
use pyo3::prelude::*;

/// Function to compute the gradient of an array of numbers
///
/// Args:
///     - array (Vec<i32>): Vector of floats
///     - var_step (f64): Finite step to calculate the gradient
///
/// Returns:
///     - An PyResult of Vector of floats
#[pyfunction]
pub fn compute_gradient(array: Vec<f64>, var_step: f64) -> PyResult<Vec<f64>> {
    if array.len() < 2 {
        return Ok(vec![]);
    }

    let mut gradient = Vec::with_capacity(array.len() - 1);
    // Calculate the gradient for each method using a forward
    // method
    for i in 1..array.len() {
        gradient.push((array[i] - array[i - 1]) / var_step);
    }
    // Return the gradient
    Ok(gradient)
}
