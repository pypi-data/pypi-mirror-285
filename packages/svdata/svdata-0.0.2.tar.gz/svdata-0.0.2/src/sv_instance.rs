use pyo3::prelude::*;
use sv_parser::{unwrap_node, RefNode, SyntaxTree};

use crate::sv_misc::{get_string, identifier};

#[derive(Debug, Clone, PartialEq)]
#[pyclass]
pub struct SvInstance {
    #[pyo3(get, set)]
    pub module_identifier: String,
    #[pyo3(get, set)]
    pub hierarchical_instance: String,
    #[pyo3(get, set)]
    pub hierarchy: Vec<String>,
    #[pyo3(get, set)]
    pub connections: Vec<Vec<String>>,
}

#[pymethods]
impl SvInstance {
    #[new]
    fn new() -> Self {
        SvInstance {
            module_identifier: String::new(),
            hierarchical_instance: String::new(),
            hierarchy: Vec::new(),
            connections: Vec::new(),
        }
    }
    fn __repr__(&self) -> String {
        format!(
            "SvInstance(module_identifier={}, hierarchical_instance={}, hierarchy={}, connections={})",
            self.module_identifier,
            self.hierarchical_instance,
            self.hierarchy.len(),
            self.connections.len()
        )
    }
}

pub fn module_instance(p: &sv_parser::ModuleInstantiation, syntax_tree: &SyntaxTree) -> SvInstance {
    SvInstance {
        module_identifier: inst_module_identifier(p, syntax_tree),
        hierarchical_instance: inst_hierarchical_instance(p, syntax_tree),
        hierarchy: inst_hierarchy(p, syntax_tree),
        connections: inst_connections(p, syntax_tree),
    }
}

// Find module identifier for the instantiation (child module)
fn inst_module_identifier(p: &sv_parser::ModuleInstantiation, syntax_tree: &SyntaxTree) -> String {
    if let Some(id) = unwrap_node!(p, ModuleIdentifier) {
        identifier(id, syntax_tree).unwrap()
    } else {
        unreachable!()
    }
}

// Find hierarchical instance for the instantiation
fn inst_hierarchical_instance(
    p: &sv_parser::ModuleInstantiation,
    syntax_tree: &SyntaxTree,
) -> String {
    if let Some(id) = unwrap_node!(p, InstanceIdentifier) {
        identifier(id, syntax_tree).unwrap()
    } else {
        unreachable!()
    }
}

// Find hierarchy for the instantiation (only finds label for the time being)
fn inst_hierarchy(p: &sv_parser::ModuleInstantiation, syntax_tree: &SyntaxTree) -> Vec<String> {
    let mut ret: Vec<String> = Vec::new();

    for node in syntax_tree {
        if let RefNode::GenerateBlock(x) = node {
            for instance in x {
                if let RefNode::ModuleInstantiation(y) = instance {
                    if y == p {
                        if let Some(label) = unwrap_node!(node.clone(), GenerateBlockIdentifier) {
                            let label = identifier(label, syntax_tree).unwrap();
                            ret.push(label);
                        } else {
                            unreachable!()
                        }
                    }
                }
            }
        }
    }

    ret
}

// Finding connections for the instantiation
fn inst_connections(
    p: &sv_parser::ModuleInstantiation,
    syntax_tree: &SyntaxTree,
) -> Vec<Vec<String>> {
    let mut ret: Vec<Vec<String>> = Vec::new();

    for node in p {
        match node {
            // Port connection by name
            RefNode::NamedPortConnection(x) => {
                // Connection in child module
                let left = unwrap_node!(node.clone(), PortIdentifier).unwrap();
                let left = identifier(left, syntax_tree).unwrap();
                // Connection in parent module
                if let Some(right_node) = unwrap_node!(node.clone(), HierarchicalIdentifier) {
                    let right_name = identifier(right_node, syntax_tree).unwrap();
                    let mut right_index = String::new();
                    for select_node in x {
                        if let RefNode::Select(y) = select_node {
                            for expression_node in y {
                                if let RefNode::HierarchicalIdentifier(_) = expression_node {
                                    if let Some(right_node) =
                                        unwrap_node!(expression_node.clone(), Identifier)
                                    {
                                        right_index = identifier(right_node, syntax_tree).unwrap();
                                    } else {
                                        unreachable!()
                                    }
                                } else if let RefNode::IntegralNumber(_) = expression_node {
                                    if let Some(right_node) =
                                        unwrap_node!(expression_node.clone(), DecimalNumber)
                                    {
                                        right_index = get_string(right_node, syntax_tree).unwrap();
                                    } else {
                                        unreachable!()
                                    }
                                }
                            }
                        }
                    }
                    // Push connection to ret
                    if right_index.is_empty() {
                        // If no indexing
                        ret.push([left, right_name].to_vec());
                    } else {
                        // If there is indexing
                        let right = format!("{right_name}[{right_index}]");
                        ret.push([left, right].to_vec());
                    }
                } else {
                    ret.push([left, String::new()].to_vec());
                }
            }
            // Port connection by order
            RefNode::OrderedPortConnection(x) => {
                if let Some(right_node) = unwrap_node!(node.clone(), HierarchicalIdentifier) {
                    let right_name = identifier(right_node, syntax_tree).unwrap();
                    // TODO: Mutating a string is a bit dodgy here.
                    let mut right_index = String::new();
                    for select_node in x {
                        if let RefNode::Select(y) = select_node {
                            for expression_node in y {
                                if let RefNode::HierarchicalIdentifier(_) = expression_node {
                                    if let Some(right_node) =
                                        unwrap_node!(expression_node.clone(), Identifier)
                                    {
                                        right_index = identifier(right_node, syntax_tree).unwrap();
                                    } else {
                                        unreachable!()
                                    }
                                } else if let RefNode::IntegralNumber(_) = expression_node {
                                    if let Some(right_node) =
                                        unwrap_node!(expression_node.clone(), DecimalNumber)
                                    {
                                        right_index = get_string(right_node, syntax_tree).unwrap();
                                    } else {
                                        unreachable!()
                                    }
                                }
                            }
                        }
                    }
                    // Push connection to ret
                    if right_index.is_empty() {
                        // If no indexing
                        ret.push([right_name].to_vec());
                    } else {
                        // If there is indexing
                        let right = format!("{right_name}[{right_index}]");
                        ret.push([right].to_vec());
                    }
                }
            }
            _ => (),
        }
    }

    ret
}
