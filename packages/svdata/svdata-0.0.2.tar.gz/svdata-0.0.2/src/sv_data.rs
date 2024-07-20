use pyo3::prelude::*;

use crate::sv_module::SvModule;

#[derive(Debug, Clone, PartialEq)]
#[pyclass]
pub struct SvData {
    #[pyo3(get, set)]
    pub modules: Vec<SvModule>,
}

#[pymethods]
impl SvData {
    #[new]
    fn new() -> Self {
        SvData {
            modules: Vec::new(),
        }
    }
    fn __repr__(&self) -> String {
        format!("SvData(modules={})", self.modules.len())
    }
}
