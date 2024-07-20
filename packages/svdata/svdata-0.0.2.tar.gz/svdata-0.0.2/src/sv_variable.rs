use pyo3::prelude::*;
use sv_parser::{unwrap_node, SyntaxTree};

use crate::sv_misc::identifier;

#[derive(Debug, Clone, PartialEq)]
#[pyclass]
pub struct SvVariable {
    #[pyo3(get, set)]
    pub identifier: String,
}

#[pymethods]
impl SvVariable {
    #[new]
    fn new() -> Self {
        SvVariable {
            identifier: String::new(),
        }
    }
    fn __repr__(&self) -> String {
        format!("SvVariable(identifier={})", self.identifier)
    }
}

pub fn variable_declaration(
    p: &sv_parser::ModuleCommonItem,
    syntax_tree: &SyntaxTree,
) -> SvVariable {
    SvVariable {
        identifier: variable_identifier(p, syntax_tree),
    }
}

fn variable_identifier(node: &sv_parser::ModuleCommonItem, syntax_tree: &SyntaxTree) -> String {
    if let Some(id) = unwrap_node!(node, VariableIdentifier) {
        identifier(id, syntax_tree).unwrap()
    } else if let Some(id) = unwrap_node!(node, NetIdentifier) {
        identifier(id, syntax_tree).unwrap()
    } else {
        unreachable!()
    }
}
