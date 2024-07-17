extern crate nalgebra as na;
extern crate numpy;
extern crate pointpca2_rs;

use na::DMatrix;
use numpy::PyArray1;
use numpy::PyReadonlyArray2;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

fn as_dmatrix<'a, T>(x: &'a PyReadonlyArray2<T>) -> DMatrix<T>
where
    T: numpy::Element + na::Scalar,
{
    let data: Vec<T> = x.as_array().iter().cloned().collect();
    DMatrix::from_row_slice(x.shape()[0], x.shape()[1], &data)
}

#[pyfunction]
fn compute_pointpca2<'py>(
    _py: Python<'py>,
    points_a: PyReadonlyArray2<'py, f64>,
    colors_a: PyReadonlyArray2<'py, u8>,
    points_b: PyReadonlyArray2<'py, f64>,
    colors_b: PyReadonlyArray2<'py, u8>,
    search_size: usize,
    verbose: bool,
) -> &'py PyArray1<f64> {
    let (points_a, colors_a, points_b, colors_b) = {
        (
            as_dmatrix(&points_a),
            as_dmatrix(&colors_a),
            as_dmatrix(&points_b),
            as_dmatrix(&colors_b),
        )
    };
    let pooled_predictors = pointpca2_rs::compute_pointpca2(
        points_a,
        colors_a,
        points_b,
        colors_b,
        search_size,
        verbose,
    );
    let py_array = PyArray1::from_iter(_py, pooled_predictors.iter().cloned());
    py_array
}

#[pymodule]
fn pointpca2(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute_pointpca2, m)?)?;
    Ok(())
}
