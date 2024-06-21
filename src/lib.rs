use pyo3::prelude::*;

/// Formats the sum of two numbers as string.

#[pyfunction]
fn rs_time() -> PyResult<f64> {
    Ok(std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs_f64())
}

/// A Python module implemented in Rust.
#[pymodule]
fn wave_craze(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(rs_time, m)?)?;
    Ok(())
}
