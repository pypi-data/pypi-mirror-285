use std::collections::HashMap;

use pyo3::prelude::*;
use sv_parser::{unwrap_node, NodeEvent, RefNode, SyntaxTree};
use tinytemplate::TinyTemplate;

use crate::{
    sv_instance::{module_instance, SvInstance},
    sv_misc::identifier,
    sv_port::{port_declaration_ansi, SvPort},
    sv_variable::{variable_declaration, SvVariable},
};

#[derive(Debug, Clone, PartialEq)]
#[pyclass]
pub struct SvModule {
    #[pyo3(get, set)]
    pub identifier: String,
    #[pyo3(get, set)]
    pub filepath: String,
    #[pyo3(get, set)]
    pub ports: Vec<SvPort>,
    #[pyo3(get, set)]
    pub variables: Vec<SvVariable>,
    #[pyo3(get, set)]
    pub instances: Vec<SvInstance>,
}

#[pymethods]
impl SvModule {
    #[new]
    fn new() -> Self {
        SvModule {
            identifier: String::new(),
            filepath: String::new(),
            ports: Vec::new(),
            variables: Vec::new(),
            instances: Vec::new(),
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "SvModule(identifier={}, filepath={}, ports={}, variables={}, instances={})",
            self.identifier,
            self.filepath,
            self.ports.len(),
            self.variables.len(),
            self.instances.len()
        )
    }
    fn render_ports(&self) -> PyResult<String> {
        if self.ports.is_empty() {
            return Ok("();".to_string());
        }
        let mut ret = "(\n".to_string();
        for port in &self.ports[..self.ports.len() - 1] {
            ret.push_str(&format!(
                "  {} logic {}, \n",
                port.direction, port.identifier
            ));
        }
        ret.push_str(&format!(
            "  {} logic {}\n);",
            self.ports.last().unwrap().direction,
            self.ports.last().unwrap().identifier
        ));

        Ok(ret)
    }
    fn render_module_variables(&self) -> PyResult<String> {
        if self.variables.is_empty() {
            return Ok("".to_string());
        }
        let mut ret = "".to_string();
        for variable in &self.variables {
            ret.push_str(&format!("  logic {};\n", variable.identifier));
        }
        Ok(ret)
    }
    fn render_instances(&self) -> PyResult<String> {
        if self.instances.is_empty() {
            return Ok("".to_string());
        }
        let mut ret = "".to_string();
        for instance in &self.instances {
            ret.push_str(&format!(
                "  {} {}",
                instance.module_identifier, instance.hierarchical_instance
            ));

            if instance.connections.is_empty() {
                ret.push_str("();\n");
            } else {
                ret.push_str("(\n");
                for connection in &instance.connections[..instance.connections.len() - 1] {
                    ret.push_str(&format!("    .{}({}),\n", connection[0], connection[1]));
                }
                ret.push_str(&format!(
                    "    .{}({})\n",
                    instance.connections.last().unwrap()[0],
                    instance.connections.last().unwrap()[1]
                ));
                ret.push_str("  );\n");
            }
        }
        Ok(ret)
    }

    pub fn render(&self) -> PyResult<String> {
        let mut tt = TinyTemplate::new();
        tt.add_template(
            "svmodule",
            "module {module_identifier} {module_ports}

{variables}
{instances}
endmodule
",
        )
        .unwrap();

        let mut context = HashMap::new();
        context.insert("module_identifier".to_string(), self.identifier.clone());
        context.insert("filepath".to_string(), self.filepath.clone());
        context.insert("module_ports".to_string(), self.render_ports()?);
        context.insert("variables".to_string(), self.render_module_variables()?);
        context.insert("instances".to_string(), self.render_instances()?);

        match tt.render("svmodule", &context) {
            Ok(rendered) => Ok(rendered),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyException, _>(format!(
                "Rendering error: {}",
                e
            ))),
        }
    }
}

pub fn module_declaration_ansi(m: RefNode, syntax_tree: &SyntaxTree, filepath: &str) -> SvModule {
    let mut ret = SvModule {
        identifier: module_identifier(m.clone(), syntax_tree).unwrap(),
        filepath: filepath.to_string(),
        ports: Vec::new(),
        variables: Vec::new(),
        instances: Vec::new(),
    };
    let mut entering: bool;

    for event in m.into_iter().event() {
        let node = match event {
            NodeEvent::Enter(x) => {
                entering = true;
                x
            }
            NodeEvent::Leave(x) => {
                entering = false;
                x
            }
        };
        if entering {
            match node {
                RefNode::AnsiPortDeclaration(p) => {
                    let port = port_declaration_ansi(p, syntax_tree);
                    ret.ports.push(port);
                }
                RefNode::ModuleCommonItem(p) => {
                    let variable = variable_declaration(p, syntax_tree);
                    ret.variables.push(variable);
                }
                RefNode::ModuleInstantiation(p) => {
                    ret.instances.push(module_instance(p, syntax_tree));
                }

                _ => (),
            }
        }
    }
    ret
}

fn module_identifier(node: RefNode, syntax_tree: &SyntaxTree) -> Option<String> {
    if let Some(id) = unwrap_node!(node, ModuleIdentifier) {
        identifier(id, syntax_tree)
    } else {
        unreachable!()
    }
}
