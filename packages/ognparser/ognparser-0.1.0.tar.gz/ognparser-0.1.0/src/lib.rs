mod message;
mod position_comment;
mod status_comment;
mod utils;

use crate::message::parse;
use pyo3::prelude::*;

#[pymodule]
fn ognparser(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    Ok(())
}
