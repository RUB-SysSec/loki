use il::assignment::Assignment;

#[derive(Serialize, Deserialize, Debug, Hash, Eq, PartialEq, Clone, Ord, PartialOrd)]
pub struct SemanticFormula(pub Vec<Assignment>);

impl SemanticFormula {
    pub fn new(v: Vec<Assignment>) -> SemanticFormula {
        SemanticFormula(v)
    }

    pub fn to_string(&self) -> String {
        let mut ret = String::new();
        ret.push_str("{ ");
        ret.push_str(&format!("{}", self.0.first().unwrap().to_string()));

        if self.0.len() == 1 {
            ret.push_str(" }");
        }

        for i in 1..self.0.len() {
            if i < (self.0.len() - 1) {
                ret.push_str(&format!(" ; {}", self.0.get(i).unwrap().to_string()));
            } else {
                ret.push_str(&format!(" ; {}", self.0.get(i).unwrap().to_string()));
                ret.push_str(" }");
            }
        }
        ret
    }
}
