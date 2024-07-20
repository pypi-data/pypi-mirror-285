use sv_parser::{unwrap_node, NodeEvent, RefNode, SyntaxTree};

pub fn identifier(parent: RefNode, syntax_tree: &SyntaxTree) -> Option<String> {
    let id = match unwrap_node!(parent, SimpleIdentifier, EscapedIdentifier) {
        Some(RefNode::SimpleIdentifier(x)) => Some(x.nodes.0),
        Some(RefNode::EscapedIdentifier(x)) => Some(x.nodes.0),
        _ => None,
    };

    id.map(|x| syntax_tree.get_str(&x).unwrap().to_string())
}

pub fn get_string(parent: RefNode, syntax_tree: &SyntaxTree) -> Option<String> {
    let mut ret: String = String::new();
    let mut skip_whitespace: bool = false;

    for node in parent.into_iter().event() {
        match node {
            NodeEvent::Enter(RefNode::WhiteSpace(_)) => skip_whitespace = true,
            NodeEvent::Leave(RefNode::WhiteSpace(_)) => skip_whitespace = false,
            NodeEvent::Enter(RefNode::Locate(x)) => {
                if !skip_whitespace {
                    ret.push_str(syntax_tree.get_str(x).unwrap());
                }
            }

            _ => (),
        }
    }

    if ret.is_empty() {
        None
    } else {
        Some(ret)
    }
}
