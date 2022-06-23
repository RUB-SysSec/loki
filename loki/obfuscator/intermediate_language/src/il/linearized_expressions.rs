use crate::FastHashSet;
use il::expr_replacer::ExprReplacer;
use il::expression_evaluator::ExprEvaluator;
use symbolic_execution::symbolic_evaluator::SymbolicEvaluator;

#[derive(Serialize, Deserialize, Debug, Hash, Eq, PartialEq, Clone, Ord, PartialOrd)]
pub struct LinearExpr {
    pub size: usize,
    pub op: LinearExprOp,
}

#[derive(Serialize, Deserialize, Debug, Hash, Eq, PartialEq, Clone, Ord, PartialOrd)]
pub enum LinearExprOp {
    Assign,
    Add,
    Sub,
    Or,
    And,
    Xor,
    Nand,
    Nor,
    Not,
    Neg,
    Ashr,
    Lshr,
    Shl,
    Mul,
    Udiv,
    Sdiv,
    Urem,
    Srem,
    Ult,
    Slt,
    Ule,
    Sle,
    Equal,
    Const(u64),
    Reg(String),
    RegSlice(u8, u8),
    ConstSlice(u8, u8),
    Ite,
    Slice(u8, u8),
    Mem,
    Concat,
    ZeroExtend,
    SignExtend,
    Trunc,
    BitCast,
    E,
    Nop,
    GEP,
    Load,
    Store,
    Alloc(u64),
    Alloca,
}

impl LinearExpr {
    pub fn new(op: LinearExprOp, size: usize) -> LinearExpr {
        LinearExpr { size, op }
    }

    pub fn arity(&self) -> usize {
        match self.op {
            LinearExprOp::Assign => 2,
            LinearExprOp::Add => 2,
            LinearExprOp::Sub => 2,
            LinearExprOp::Or => 2,
            LinearExprOp::And => 2,
            LinearExprOp::Xor => 2,
            LinearExprOp::Nand => 2,
            LinearExprOp::Nor => 2,
            LinearExprOp::Not => 1,
            LinearExprOp::Neg => 1,
            LinearExprOp::Ashr => 2,
            LinearExprOp::Lshr => 2,
            LinearExprOp::Shl => 2,
            LinearExprOp::Mul => 2,
            LinearExprOp::Udiv => 2,
            LinearExprOp::Sdiv => 2,
            LinearExprOp::Urem => 2,
            LinearExprOp::Srem => 2,
            LinearExprOp::Ult => 2,
            LinearExprOp::Slt => 2,
            LinearExprOp::Ule => 2,
            LinearExprOp::Sle => 2,
            LinearExprOp::Equal => 2,
            LinearExprOp::Const(_) => 0,
            LinearExprOp::Reg(ref _x) => 0,
            LinearExprOp::RegSlice(..) => 0,
            LinearExprOp::ConstSlice(..) => 0,
            LinearExprOp::Ite => 3,
            LinearExprOp::Slice(_x, _y) => 1,
            LinearExprOp::Mem => 1,
            LinearExprOp::Concat => 2,
            LinearExprOp::ZeroExtend => 1,
            LinearExprOp::SignExtend => 1,
            LinearExprOp::Trunc => 1,
            LinearExprOp::E => 0,
            LinearExprOp::Nop => 0,
            LinearExprOp::GEP => 2,
            LinearExprOp::Load => 1,
            LinearExprOp::Store => 2,
            LinearExprOp::Alloc(_) => 0,
            LinearExprOp::Alloca => 1,
            LinearExprOp::BitCast => 1,
        }
    }

    pub fn is_constant(&self) -> bool {
        match self.op {
            LinearExprOp::Const(_) => true,
            _ => false,
        }
    }

    pub fn is_var(&self) -> bool {
        match self.op {
            LinearExprOp::Reg(_) => true,
            _ => false,
        }
    }

    pub fn is_commutative(&self) -> bool {
        match self.op {
            LinearExprOp::Add => true,
            LinearExprOp::Or => true,
            LinearExprOp::And => true,
            LinearExprOp::Xor => true,
            LinearExprOp::Nand => true,
            LinearExprOp::Nor => true,
            LinearExprOp::Mul => true,
            _ => false,
        }
    }

    pub fn is_associative(&self) -> bool {
        match self.op {
            LinearExprOp::Add => true,
            LinearExprOp::Or => true,
            LinearExprOp::And => true,
            LinearExprOp::Xor => true,
            LinearExprOp::Mul => true,
            _ => false,
        }
    }

    pub fn get_constant_val(&self) -> u64 {
        match self.op {
            LinearExprOp::Const(x) => x,
            _ => unreachable!(),
        }
    }

    pub fn get_var_name(&self) -> &str {
        match self.op {
            LinearExprOp::Reg(ref x) => x,
            _ => unreachable!(),
        }
    }

    pub fn placeholder(size: usize) -> LinearExpr {
        LinearExpr::new(LinearExprOp::E, size)
    }

    pub fn is_non_terminal(&self) -> bool {
        self.is_var() && self.get_var_name() == "NT"
    }
}

#[derive(Serialize, Deserialize, Debug, Hash, Eq, PartialEq, Clone, Ord, PartialOrd)]
pub struct LinearizedExpr(pub Vec<LinearExpr>);

impl LinearizedExpr {
    pub fn new(v: Vec<LinearExpr>) -> LinearizedExpr {
        LinearizedExpr(v)
    }

    pub fn gen_non_terminal(size: usize) -> LinearExpr {
        LinearExpr::new(LinearExprOp::Reg("NT".to_string()), size)
    }

    pub fn from_linear_expr(expr: LinearExpr) -> LinearizedExpr {
        LinearizedExpr::new(vec![expr])
    }

    pub fn size(&self) -> usize {
        self.0.last().unwrap().size
    }

    pub fn op(&self) -> &LinearExpr {
        &self.0.last().unwrap()
    }

    pub fn set_size(&mut self, size: usize) {
        self.0.last_mut().unwrap().size = size;
    }

    pub fn to_vec(&self) -> Vec<LinearExpr> {
        self.0.clone()
    }

    pub fn depth(&self) -> usize {
        let mut stack: Vec<usize> = Vec::with_capacity(self.0.len());

        for expr in self.0.iter() {
            let n = expr.arity();
            if n > 0 {
                let max = (0..n).map(|_| stack.pop().unwrap()).max().unwrap();
                stack.push(max + 1);
            } else if expr.op == LinearExprOp::E {
                stack.push(0);
            } else {
                stack.push(1);
            }
        }
        stack.pop().unwrap()
    }

    pub fn is_constant(&self) -> bool {
        match self.0.last().unwrap().is_constant() {
            true if self.0.len() == 1 => true,
            _ => false,
        }
    }

    pub fn is_var(&self) -> bool {
        match self.0.last().unwrap().is_var() {
            true if self.0.len() == 1 => true,
            _ => false,
        }
    }

    pub fn get_var_name(&self) -> &str {
        match self.op() {
            _ if self.is_var() => self.op().get_var_name(),
            _ => unreachable!(),
        }
    }

    pub fn get_constant_val(&self) -> u64 {
        match self.0.last().unwrap().op {
            LinearExprOp::Const(x) if self.0.len() == 1 => x,
            _ => {
                println!("{}", self.to_string());
                println!("op: {:?}", self.0.last().unwrap().op);
                unreachable!()
            }
        }
    }

    pub fn check_constant_val(&self, n: u64) -> bool {
        match self.is_constant() {
            true => {
                if self.get_constant_val() == n {
                    true
                } else {
                    false
                }
            }
            false => false,
        }
    }

    pub fn is_non_terminal(&self) -> bool {
        self.0.iter().any(|e| e.is_non_terminal())
    }

    pub fn get_sizes(&self) -> Vec<usize> {
        let mut ret = Vec::with_capacity(self.0.len());
        for index in 0..self.0.len() {
            let n = self.0[index].arity();
            match n {
                0 => ret.push(1),
                1 => {
                    let x = ret[index - 1];
                    ret.push(x + 1);
                }
                2 => {
                    let x = ret[index - 1];
                    let y = ret[index - 1 - x];
                    ret.push(x + y + 1);
                }
                3 => {
                    let x = ret[index - 1];
                    let y = ret[index - 1 - x];
                    let z = ret[index - 1 - x - y];
                    ret.push(x + y + z + 1);
                }
                _ => unreachable!(),
            }
        }
        ret
    }

    pub fn get_expression_slice(&self, start: usize, stop: usize) -> LinearizedExpr {
        LinearizedExpr::new(self.0.as_slice()[start..stop].to_vec())
    }

    pub fn no_op(size: usize) -> LinearizedExpr {
        LinearizedExpr::from_linear_expr(LinearExpr::new(LinearExprOp::Nop, size))
    }

    pub fn len(&self) -> usize {
        self.0.len()
    }

    pub fn is_nop(&self) -> bool {
        self.0.last().unwrap().op == LinearExprOp::Nop
    }

    pub fn extend(&mut self, expr: LinearizedExpr) {
        self.0.extend(expr.0);
    }

    pub fn push(&mut self, expr: LinearExpr) {
        self.0.push(expr);
    }

    pub fn to_infix(&self) -> String {
        <dyn ExprEvaluator<String>>::eval(self, &self)
    }

    pub fn to_string(&self) -> String {
        self.to_infix()
    }

    pub fn replace_at_pos(&mut self, pos: usize, new_expr: &LinearizedExpr) {
        self.0.remove(pos);
        for index in (pos..pos + new_expr.0.len()).rev() {
            self.0
                .insert(pos, new_expr.0.get(index - pos).unwrap().clone())
        }
    }

    pub fn replace_subexpr(&mut self, sub_expr: &LinearizedExpr, replacement: &LinearizedExpr) {
        *self = ExprReplacer::replace(self.clone(), sub_expr, replacement);
    }

    pub fn num_unique_vars(&self) -> usize {
        self.0
            .iter()
            .filter(|e| e.is_var())
            .collect::<FastHashSet<_>>()
            .len()
    }

    pub fn num_unique_constants(&self) -> usize {
        self.0
            .iter()
            .filter(|e| e.is_constant())
            .collect::<FastHashSet<_>>()
            .len()
    }

    pub fn replace_var(&mut self, v_old: &LinearizedExpr, v_new: &LinearizedExpr) {
        assert_eq!(v_old.size(), v_new.size());
        for v in self.0.iter_mut().filter(|e| e.is_var()) {
            if v.get_var_name() == v_old.get_var_name() {
                *v = LinearExpr::new(
                    LinearExprOp::Reg(v_new.get_var_name().to_string()),
                    v_new.size(),
                );
            }
        }
    }

    pub fn replace_var_with_constant(&mut self, v_old: &LinearizedExpr, v_new: &LinearizedExpr) {
        assert_eq!(v_old.size(), v_new.size());
        for v in self.0.iter_mut().filter(|e| e.is_var()) {
            if v.get_var_name() == v_old.get_var_name() {
                *v = LinearExpr::new(LinearExprOp::Const(v_new.get_constant_val()), v_new.size());
            }
        }
    }

    pub fn contains_var_name(&self, var_name: &str) -> bool {
        self.0
            .iter()
            .any(|x| x.is_var() && x.get_var_name() == var_name)
    }

    pub fn is_memory_op(&self) -> bool {
        match self.op().op {
            LinearExprOp::Load
            | LinearExprOp::Store
            | LinearExprOp::Alloc(_)
            | LinearExprOp::Mem => true,
            _ => false,
        }
    }

    pub fn iter_mut(&mut self) -> impl Iterator<Item = &mut LinearExpr> {
        self.0.iter_mut()
    }

    pub fn gen_se_symbols(&self) -> Vec<LinearExpr> {
        self.0
            .iter()
            .filter(|e| e.is_var())
            .map(|e| LinearExpr::new(LinearExprOp::Reg(e.get_var_name().to_string()), e.size))
            .collect()
    }

    fn symbolical_execute(expr: &LinearizedExpr, se_symbols: Vec<LinearExpr>) -> LinearizedExpr {
        let evaluator = SymbolicEvaluator::new(se_symbols);
        evaluator.evaluate(expr)
    }

    pub fn simplify(&self) -> LinearizedExpr {
        let se_symbols = self.gen_se_symbols();
        let mut before = self.clone();
        let mut current = LinearizedExpr::symbolical_execute(self, se_symbols.clone());
        while before != current {
            before = current.clone();
            current = LinearizedExpr::symbolical_execute(&current, se_symbols.clone());
        }
        current
    }

    pub fn get_vars(&self) -> Vec<LinearizedExpr> {
        self.0
            .iter()
            .filter(|x| x.is_var())
            .map(|x| LinearizedExpr::from_linear_expr(x.clone()))
            .collect()
    }

    pub fn get_unique_vars(&self) -> Vec<LinearizedExpr> {
        let mut seen = FastHashSet::default();
        let mut ret = vec![];

        for v in self
            .0
            .iter()
            .filter(|x| x.is_var())
            .map(|x| LinearizedExpr::from_linear_expr(x.clone()))
            .into_iter()
        {
            if !seen.contains(&v) {
                ret.push(v.clone());
            }
            seen.insert(v);
        }
        ret
    }

    pub fn get_constants(&self) -> Vec<LinearizedExpr> {
        self.0
            .iter()
            .filter(|x| x.is_constant())
            .map(|x| LinearizedExpr::from_linear_expr(x.clone()))
            .collect()
    }

    pub fn get_unique_constants(&self) -> Vec<LinearizedExpr> {
        let mut seen = FastHashSet::default();
        let mut ret = vec![];

        for v in self
            .0
            .iter()
            .filter(|x| x.is_constant())
            .map(|x| LinearizedExpr::from_linear_expr(x.clone()))
            .into_iter()
        {
            if !seen.contains(&v) {
                ret.push(v.clone());
            }
            seen.insert(v);
        }
        ret
    }
}

impl ExprEvaluator<String> for LinearizedExpr {
    fn eval_op_0(&self, expr: &LinearExpr) -> String {
        match expr.op {
            LinearExprOp::Const(x) => format!("0x{:x}", x),
            LinearExprOp::ConstSlice(x, y) => format!("Const[{}:{}]", x, y),
            LinearExprOp::Reg(ref x) => format!("{}", x),
            LinearExprOp::RegSlice(x, y) => format!("Reg[{}:{}]", x, y),
            LinearExprOp::E => format!("E"),
            LinearExprOp::Nop => format!("NOP"),
            LinearExprOp::Alloc(c) => format!("Alloc({})", c),
            _ => unreachable!(),
        }
    }

    fn eval_op_1(&self, x: &String, expr: &LinearExpr) -> String {
        match expr.op {
            LinearExprOp::ZeroExtend => format!("ZeroExtend({}, {})", x, expr.size),
            LinearExprOp::SignExtend => format!("SignExtend({}, {})", x, expr.size),
            LinearExprOp::Trunc => format!("Trunc({}, {})", x, expr.size),
            LinearExprOp::Not => format!("(~ {})", x),
            LinearExprOp::Neg => format!("(- {})", x),
            LinearExprOp::Mem => format!("@{}[{}]", expr.size, x),
            LinearExprOp::Slice(start, end) => format!("Slice({}, {}, {})", x, start, end),
            LinearExprOp::Load => format!("Load({}, {})", x, expr.size),
            LinearExprOp::BitCast => format!("BitCast({}, {})", x, expr.size),
            LinearExprOp::Alloca => format!("Alloca({})", x),
            _ => unreachable!(),
        }
    }

    fn eval_op_2(&self, y: &String, x: &String, expr: &LinearExpr) -> String {
        match expr.op {
            LinearExprOp::Assign => format!("({} = {})", x, y),
            LinearExprOp::Add => format!("({} + {})", x, y),
            LinearExprOp::Sub => format!("({} - {})", x, y),
            LinearExprOp::And => format!("({} & {})", x, y),
            LinearExprOp::Or => format!("({} | {})", x, y),
            LinearExprOp::Xor => format!("({} ^ {})", x, y),
            LinearExprOp::Nand => format!("({} NAND {})", x, y),
            LinearExprOp::Nor => format!("({} NOR {})", x, y),
            LinearExprOp::Mul => format!("({} * {})", x, y),
            LinearExprOp::Udiv => format!("({} / {})", x, y),
            LinearExprOp::Sdiv => format!("({} /s {})", x, y),
            LinearExprOp::Urem => format!("({} % {})", x, y),
            LinearExprOp::Srem => format!("({} %s {})", x, y),
            LinearExprOp::Ult => format!("({} < {})", x, y),
            LinearExprOp::Slt => format!("({} <s {})", x, y),
            LinearExprOp::Ule => format!("({} <= {})", x, y),
            LinearExprOp::Sle => format!("({} <=s {})", x, y),
            LinearExprOp::Equal => format!("({} == {})", x, y),
            LinearExprOp::Ashr => format!("({} a>> {})", x, y),
            LinearExprOp::Lshr => format!("({} >> {})", x, y),
            LinearExprOp::Shl => format!("({} << {})", x, y),
            LinearExprOp::Concat => format!("({} ++ {})", x, y),
            LinearExprOp::GEP => format!("GEP({}, {})", x, y),
            LinearExprOp::Store => format!("Store({}, {}, {})", x, y, expr.size),
            _ => unreachable!(),
        }
    }
    fn eval_op_3(&self, z: &String, y: &String, x: &String, expr: &LinearExpr) -> String {
        match expr.op {
            LinearExprOp::Ite => format!("({} ? {} : {})", x, y, z),
            _ => unreachable!(),
        }
    }
}
