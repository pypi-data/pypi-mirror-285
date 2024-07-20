use pyo3::prelude::*;

use sv_module::module_declaration_ansi;
use sv_parser::{NodeEvent, RefNode};

pub mod sv_data;
pub mod sv_instance;
pub mod sv_misc;
pub mod sv_module;
pub mod sv_port;
pub mod sv_variable;
#[pyfunction]
pub fn read_sv_file(file_path: &str) -> PyResult<sv_data::SvData> {
    let defines = std::collections::HashMap::new();
    let includes: Vec<std::path::PathBuf> = Vec::new();

    let mut svdata = sv_data::SvData {
        modules: Vec::new(),
    };

    if let Ok((syntax_tree, _)) = sv_parser::parse_sv(file_path, &defines, &includes, true, false) {
        sv_to_structure(&syntax_tree, file_path, &mut svdata);
    } else {
        Err(pyo3::exceptions::PyValueError::new_err(format!(
            "Could not parse {file_path}."
        )))?;
    }

    Ok(svdata)
}

fn sv_to_structure(
    syntax_tree: &sv_parser::SyntaxTree,
    filepath: &str,
    svdata: &mut sv_data::SvData,
) {
    for event in syntax_tree.into_iter().event() {
        let enter_not_leave = match event {
            NodeEvent::Enter(_) => true,
            NodeEvent::Leave(_) => false,
        };
        let node = match event {
            NodeEvent::Leave(x) | NodeEvent::Enter(x) => x,
        };

        if enter_not_leave {
            if let RefNode::ModuleDeclarationAnsi(_) = node {
                svdata
                    .modules
                    .push(module_declaration_ansi(node, syntax_tree, filepath).clone());
            }
        }
    }
}

/// This module is implemented in Rust.
#[pymodule(name = "svdata")]
fn my_extension(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(read_sv_file, m)?)?;
    m.add_class::<sv_data::SvData>()?;
    m.add_class::<sv_port::SvPort>()?;
    m.add_class::<sv_port::SvPortDirection>()?;
    m.add_class::<sv_module::SvModule>()?;
    m.add_class::<sv_variable::SvVariable>()?;
    Ok(())
}
