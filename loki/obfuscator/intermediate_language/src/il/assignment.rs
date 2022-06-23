use il::expression_utils::assignment;
use il::linearized_expressions::LinearizedExpr;

#[derive(Serialize, Deserialize, Debug, Hash, Eq, PartialEq, Clone, Ord, PartialOrd)]
pub struct Assignment {
    pub lhs: LinearizedExpr,
    pub rhs: LinearizedExpr,
    pub size: usize,
}

impl Assignment {
    pub fn new(lhs: LinearizedExpr, rhs: LinearizedExpr) -> Assignment {
        assert_eq!(lhs.size(), rhs.size());
        let size = lhs.size();
        Assignment { lhs, rhs, size }
    }

    pub fn to_string(&self) -> String {
        format!("{} = {}", self.lhs.to_infix(), self.rhs.to_infix())
    }

    pub fn to_expr(&self) -> LinearizedExpr {
        assignment(self.lhs.clone(), self.rhs.clone())
    }

    pub fn no_op(size: usize) -> Assignment {
        Assignment::new(LinearizedExpr::no_op(size), LinearizedExpr::no_op(size))
    }

    pub fn is_nop(&self) -> bool {
        self.lhs.is_nop() & self.rhs.is_nop()
    }
}
