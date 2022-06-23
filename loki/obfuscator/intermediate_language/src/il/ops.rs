use il::expression_utils;
use il::linearized_expressions::LinearizedExpr;
use std::ops::{Add, BitAnd, BitOr, BitXor, Mul, Neg, Not, Shl, Sub};

impl Add for LinearizedExpr {
    type Output = LinearizedExpr;

    fn add(self, other: LinearizedExpr) -> LinearizedExpr {
        let size = self.size();
        expression_utils::add(self, other, size)
    }
}

impl BitAnd for LinearizedExpr {
    type Output = LinearizedExpr;

    fn bitand(self, other: LinearizedExpr) -> LinearizedExpr {
        let size = self.size();
        expression_utils::and(self, other, size)
    }
}

impl BitOr for LinearizedExpr {
    type Output = LinearizedExpr;

    fn bitor(self, other: LinearizedExpr) -> LinearizedExpr {
        let size = self.size();
        expression_utils::or(self, other, size)
    }
}

impl BitXor for LinearizedExpr {
    type Output = LinearizedExpr;

    fn bitxor(self, other: LinearizedExpr) -> LinearizedExpr {
        let size = self.size();
        expression_utils::xor(self, other, size)
    }
}

impl Mul for LinearizedExpr {
    type Output = LinearizedExpr;

    fn mul(self, other: LinearizedExpr) -> LinearizedExpr {
        let size = self.size();
        expression_utils::mul(self, other, size)
    }
}

impl Neg for LinearizedExpr {
    type Output = LinearizedExpr;

    fn neg(self) -> LinearizedExpr {
        let size = self.size();
        expression_utils::neg(self, size)
    }
}

impl Not for LinearizedExpr {
    type Output = LinearizedExpr;

    fn not(self) -> LinearizedExpr {
        let size = self.size();
        expression_utils::not(self, size)
    }
}

impl Shl for LinearizedExpr {
    type Output = LinearizedExpr;

    fn shl(self, other: LinearizedExpr) -> LinearizedExpr {
        let size = self.size();
        expression_utils::shl(self, other, size)
    }
}

impl Sub for LinearizedExpr {
    type Output = LinearizedExpr;

    fn sub(self, other: LinearizedExpr) -> LinearizedExpr {
        let size = self.size();
        expression_utils::sub(self, other, size)
    }
}
