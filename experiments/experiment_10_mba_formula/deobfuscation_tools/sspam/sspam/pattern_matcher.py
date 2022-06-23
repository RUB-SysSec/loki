"""Pattern matching module.

This module contains classes to detect a pattern in an expression, and
eventually replace it with another expression if found.

Classes and methods included in this module are:
 - EvalPattern: replaces wildcards in a pattern with their supposed
   values.
 - PatternMatcher: returns true if pattern is matched on expression.
 - match: same as PatternMatcher, but with pre-processing applied
   first
 - PatternReplacement: takes pattern, replacement expression and target
   expression as input ; if pattern is found in target expression,
   replaces it with replacement expression
 - replace: same as PatternReplacement, but with pre-processing
   applied first.
"""


import ast
from copy import deepcopy
import itertools
import astunparse

try:
    import z3
except ImportError:
    raise Exception("z3 module is needed to use this pattern matcher")

from sspam.tools import asttools
from sspam.tools.flattening import Flattening, Unflattening
from sspam import pre_processing


# If set to true, pattern matcher will use z3 to match patterns
FLEXIBLE = True


class EvalPattern(ast.NodeTransformer):
    """
    Replace wildcards in pattern with supposed values.
    """

    def __init__(self, wildcards):
        self.wildcards = wildcards

    def visit_Name(self, node):
        'Replace wildcards with supposed value'
        if node.id in self.wildcards:
            return deepcopy(self.wildcards[node.id])
        return node


class PatternMatcher(asttools.Comparator):
    """
    Try to match desired pattern with given ast.
    Wildcards are indicated with upper letters : A, B, ...
    Example : A + B will match (x | 34) + (y*67)
    """

    def __init__(self, root, nbits=0):
        'Init different components of pattern matcher'

        super(PatternMatcher, self).__init__()

        # wildcards used in the pattern with their possible values
        self.wildcards = {}
        # wildcards <-> values that are known not to work
        self.no_solution = []

        # root node of expression
        if isinstance(root, ast.Module):
            self.root = root.body[0].value
        elif isinstance(root, ast.Expression):
            self.root = root.body
        else:
            self.root = root
        if not nbits:
            self.nbits = asttools.get_default_nbits(self.root)
        else:
            self.nbits = nbits

        # identifiers for z3 evaluation
        getid = asttools.GetIdentifiers()
        getid.visit(self.root)
        self.variables = getid.variables
        self.functions = getid.functions

    @staticmethod
    def is_wildcard(node):
        'Check if node is wildcard'
        return isinstance(node, ast.Name) and node.id.isupper()

    def check_eq_z3(self, target, pattern):
        'Check equivalence with z3'
        # pylint: disable=exec-used
        getid = asttools.GetIdentifiers()
        getid.visit(target)
        if getid.functions:
            # not checking exprs with functions for now, because Z3
            # does not seem to support function declaration with
            # arbitrary number of arguments
            return False
        for var in self.variables:
            exec("%s = z3.BitVec('%s', %d)" % (var, var, self.nbits))
        target_ast = deepcopy(target)
        target_ast = Unflattening().visit(target_ast)
        ast.fix_missing_locations(target_ast)
        code1 = compile(ast.Expression(target_ast), '<string>', mode='eval')
        eval_pattern = deepcopy(pattern)
        EvalPattern(self.wildcards).visit(eval_pattern)
        eval_pattern = Unflattening().visit(eval_pattern)
        ast.fix_missing_locations(eval_pattern)
        getid.reset()
        getid.visit(eval_pattern)
        if getid.functions:
            # same reason as before, not using Z3 if there are
            # functions
            return False
        gvar = asttools.GetIdentifiers()
        gvar.visit(eval_pattern)
        if any(var.isupper() for var in gvar.variables):
            # do not check if all patterns have not been replaced
            return False
        code2 = compile(ast.Expression(eval_pattern), '<string>', mode='eval')
        sol = z3.Solver()
        if isinstance(eval(code1), int) and eval(code1) == 0:
            # cases where target == 0 are too permissive
            return False
        sol.add(eval(code1) != eval(code2))
        return sol.check().r == -1

    def check_wildcard(self, target, pattern):
        'Check wildcard value or affect it'
        if pattern.id in self.wildcards:
            wild_value = self.wildcards[pattern.id]
            exact_comp = asttools.Comparator().visit(wild_value, target)
            if exact_comp:
                return True
            if FLEXIBLE:
                return self.check_eq_z3(target, self.wildcards[pattern.id])
            else:
                return False
        else:
            self.wildcards[pattern.id] = target
            return True

    def get_model(self, target, pattern):
        'When target is constant and wildcards have no value yet'
        # pylint: disable=exec-used
        if target.n == 0:
            # zero is too permissive
            return False
        getwild = asttools.GetIdentifiers()
        getwild.visit(pattern)
        if getwild.functions:
            # not getting model for expr with functions
            return False
        wilds = getwild.variables
        # let's reduce the model to one wildcard for now
        # otherwise it adds a lot of checks...
        if len(wilds) > 1:
            return False

        wil = wilds.pop()
        if wil in self.wildcards:
            if not isinstance(self.wildcards[wil], ast.Num):
                return False
            folded = deepcopy(pattern)
            folded = Unflattening().visit(folded)
            EvalPattern(self.wildcards).visit(folded)
            folded = asttools.ConstFolding(folded, self.nbits).visit(folded)
            return folded.n == target.n
        else:
            exec("%s = z3.BitVec('%s', %d)" % (wil, wil, self.nbits))
        eval_pattern = deepcopy(pattern)
        eval_pattern = Unflattening().visit(eval_pattern)
        ast.fix_missing_locations(eval_pattern)
        code = compile(ast.Expression(eval_pattern), '<string>', mode='eval')
        sol = z3.Solver()
        sol.add(target.n == eval(code))
        if sol.check().r == 1:
            model = sol.model()
            for inst in model.decls():
                self.wildcards[str(inst)] = ast.Num(int(model[inst].as_long()))
            return True
        return False

    def check_not(self, target, pattern):
        'Check NOT pattern node that could be in another form'
        if self.is_wildcard(pattern.operand):
            wkey = pattern.operand.id
            if isinstance(target, ast.Num):
                if wkey not in self.wildcards:
                    mod = 2**self.nbits
                    self.wildcards[wkey] = ast.Num((~target.n) % mod)
                    return True
                else:
                    wilds2 = self.wildcards[pattern.operand.id]
                    num = ast.Num((~target.n) % 2**self.nbits)
                    return asttools.Comparator().visit(wilds2, num)
            else:
                if wkey not in self.wildcards:
                    self.wildcards[wkey] = ast.UnaryOp(ast.Invert(),
                                                       target)
                    return True
            return self.check_eq_z3(target, pattern)
        else:
            subpattern = pattern.operand
            newtarget = ast.UnaryOp(ast.Invert(), target)
            return self.check_eq_z3(newtarget, subpattern)

    def check_neg(self, target, pattern):
        'Check (-1)*... pattern that could be in another form'
        if self.is_wildcard(pattern.right):
            wkey = pattern.right.id
            if isinstance(target, ast.Num):
                if wkey not in self.wildcards:
                    mod = 2**self.nbits
                    self.wildcards[wkey] = ast.Num((-target.n) % mod)
                    return True
                else:
                    wilds2 = self.wildcards[pattern.right.id]
                    num = ast.Num((-target.n) % 2**self.nbits)
                    return asttools.Comparator().visit(wilds2, num)
            else:
                if wkey not in self.wildcards:
                    self.wildcards[wkey] = ast.BinOp(ast.Num(-1),
                                                     ast.Mult(), target)
                    return True
        return self.check_eq_z3(target, pattern)

    def check_twomult(self, target, pattern):
        'Check 2*... pattern that could be in another form'
        if isinstance(pattern.left, ast.Num) and pattern.left.n == 2:
            operand = pattern.right
        elif isinstance(pattern.right, ast.Num) and pattern.right.n == 2:
            operand = pattern.left
        else:
            return False

        # deal with case where wildcard operand and target are const values
        if isinstance(target, ast.Num) and isinstance(operand, ast.Name):
            conds = (operand.id in self.wildcards and
                     isinstance(self.wildcards[operand.id], ast.Num))
            if conds:
                eva = (self.wildcards[operand.id].n)*2 % 2**(self.nbits)
                if eva == target.n:
                    return True
            else:
                if target.n % 2 == 0:
                    self.wildcards[operand.id] = ast.Num(target.n / 2)
                    return True
                return False

        # get all wildcards in operand and check if they have value
        getwild = asttools.GetIdentifiers()
        getwild.visit(operand)
        wilds = getwild.variables
        for wil in wilds:
            if wil not in self.wildcards:
                return False
        return self.check_eq_z3(target, pattern)

    def general_check(self, target, pattern):
        'General check, very time-consuming, not used at the moment'
        getwild = asttools.GetIdentifiers()
        getwild.visit(pattern)
        wilds = list(getwild.variables)
        if all(wil in self.wildcards for wil in wilds):
            eval_pattern = deepcopy(pattern)
            eval_pattern = EvalPattern(self.wildcards).visit(eval_pattern)
            return self.check_eq_z3(target, eval_pattern)
        return False

    def check_pattern(self, target, pattern):
        'Try to match pattern written in different ways'

        if asttools.CheckConstExpr().visit(pattern):
            if isinstance(target, ast.Num):
                # if pattern is only a constant, evaluate and compare
                # to target
                pattcopy = deepcopy(pattern)
                eval_pat = asttools.ConstFolding(pattcopy,
                                                 self.nbits).visit(pattcopy)
                return self.visit(target, eval_pat)

        if isinstance(target, ast.Num):
            # check that wildcards in pattern have not been affected
            return self.get_model(target, pattern)

        # deal with NOT that could have been evaluated before
        notnode = (isinstance(pattern, ast.UnaryOp) and
                   isinstance(pattern.op, ast.Invert))
        if notnode:
            return self.check_not(target, pattern)

        # deal with (-1)*B that could have been evaluated
        negnode = (isinstance(pattern, ast.BinOp)
                   and isinstance(pattern.op, ast.Mult)
                   and isinstance(pattern.left, ast.Num)
                   and pattern.left.n == -1)
        if negnode:
            return self.check_neg(target, pattern)

        # deal with 2*B
        multnode = (isinstance(pattern, ast.BinOp) and
                    isinstance(pattern.op, ast.Mult))
        if multnode:
            return self.check_twomult(target, pattern)

        # return self.general_check(target, pattern)
        return False

    def visit(self, target, pattern):
        'Deal with corner cases before using classic comparison'

        # if pattern contains is a wildcard, check value against target
        # or affect it
        if self.is_wildcard(pattern):
            return self.check_wildcard(target, pattern)

        # if types are different, we might be facing the same pattern
        # written differently
        if type(target) != type(pattern):
            if FLEXIBLE:
                return self.check_pattern(target, pattern)
            else:
                return False

        # get type of node to call the right visit_ method
        nodetype = target.__class__.__name__
        comp = getattr(self, "visit_%s" % nodetype, None)

        if not comp:
            raise Exception("no comparison function for %s" % nodetype)
        return comp(target, pattern)

    def visit_Num(self, target, pattern):
        'Check if num values are equal modulo 2**nbits'
        mod = 2**self.nbits
        return (target.n % mod) == (pattern.n % mod)

    def visit_BinOp(self, target, pattern):
        'Check type of operation and operands'
        # pylint: disable=too-many-branches

        if type(target.op) != type(pattern.op):
            if FLEXIBLE:
                return self.check_pattern(target, pattern)
            else:
                return False

        # if operation is commutative, left and right operands are
        # interchangeable
        previous_state = deepcopy(self.wildcards)
        cond1 = (self.visit(target.left, pattern.left) and
                 self.visit(target.right, pattern.right))
        state = asttools.apply_hooks()
        nos = self.wildcards in self.no_solution
        asttools.restore_hooks(state)
        if cond1 and not nos:
            return True
        if nos:
            self.wildcards = deepcopy(previous_state)
        if not cond1 and not nos:
            # different visiting order might give different results
            wildsbackup = deepcopy(self.wildcards)
            self.wildcards = deepcopy(previous_state)
            cond1_prime = (self.visit(target.right, pattern.right) and
                           self.visit(target.left, pattern.left))
            if cond1_prime:
                return True
            else:
                self.wildcards = deepcopy(wildsbackup)

        # commutative operators
        if isinstance(target.op, (ast.Add, ast.Mult,
                                  ast.BitAnd, ast.BitOr, ast.BitXor)):
            cond2 = (self.visit(target.left, pattern.right) and
                     self.visit(target.right, pattern.left))
            if cond2:
                return True
            wildsbackup = deepcopy(self.wildcards)
            self.wildcards = deepcopy(previous_state)
            cond2_prime = (self.visit(target.right, pattern.left) and
                           self.visit(target.left, pattern.right))
            if cond2_prime:
                return True
            else:
                self.wildcards = deepcopy(wildsbackup)

            # if those affectations don't work, try with another order
            if target == self.root:
                self.no_solution.append(self.wildcards)
                self.wildcards = deepcopy(previous_state)
                cond1 = (self.visit(target.left, pattern.left) and
                         self.visit(target.right, pattern.right))
                if cond1:
                    return True
                cond2 = (self.visit(target.left, pattern.right)
                         and self.visit(target.right, pattern.left))
                return cond1 or cond2
        self.wildcards = deepcopy(previous_state)
        return False

    def visit_BoolOp(self, target, pattern):
        'Match pattern on flattened operators of same length and same type'
        conds = (type(target.op) == type(pattern.op) and
                 len(target.values) == len(pattern.values))
        if not conds:
            return False
        # try every combination wildcard <=> value
        old_context = deepcopy(self.wildcards)
        for perm in itertools.permutations(target.values):
            self.wildcards = deepcopy(old_context)
            res = True
            i = 0
            for i in range(len(pattern.values)):
                res &= self.visit(perm[i], pattern.values[i])
            if res:
                return res
        return False

    def visit_UnaryOp(self, target, pattern):
        'Match type of UnaryOp and operands'
        if type(target.op) != type(pattern.op):
            return False
        return self.visit(target.operand, pattern.operand)

    def visit_Call(self, target, pattern):
        'Match name of Call and arguments'
        if (not self.visit(target.func, pattern.func)
           or len(target.args) != len(pattern.args)):
            return False
        if (not all([self.visit(t_arg, p_arg) for t_arg, p_arg in
                    zip(target.args, pattern.args)])
            or not all([self.visit(t_key, p_key) for t_key, p_key in
                        zip(target.keywords, pattern.keywords)])):
            return False
        # only dealing with None starags and kwards for the moment
        if (not (target.starargs is None and pattern.starargs is None)
           or not (target.kwargs is None and pattern.kwargs is None)):
            return False

        return True


def match(target_str, pattern_str):
    'Apply all pre-processing, then pattern matcher'
    target_ast = ast.parse(target_str, mode="eval").body
    target_ast = pre_processing.all_preprocessings(target_ast)
    target_ast = Flattening(ast.Add).visit(target_ast)
    pattern_ast = ast.parse(pattern_str, mode="eval").body
    pattern_ast = pre_processing.all_preprocessings(pattern_ast)
    pattern_ast = Flattening(ast.Add).visit(pattern_ast)
    return PatternMatcher(target_ast).visit(target_ast, pattern_ast)


class PatternReplacement(ast.NodeTransformer):
    """
    Test if a pattern is included in an expression,
    and replace it if found.
    """

    def __init__(self, patt_ast, target_ast, rep_ast, nbits=0):
        'Pattern ast should have as root: BinOp, BoolOp, UnaryOp or Call'
        if isinstance(patt_ast, ast.Module):
            self.patt_ast = patt_ast.body[0].value
        elif isinstance(patt_ast, ast.Expression):
            self.patt_ast = patt_ast.body
        else:
            self.patt_ast = patt_ast
        if isinstance(rep_ast, ast.Module):
            self.rep_ast = deepcopy(rep_ast.body[0].value)
        elif isinstance(rep_ast, ast.Expression):
            self.rep_ast = deepcopy(rep_ast.body)
        else:
            self.rep_ast = deepcopy(rep_ast)

        if not nbits:
            getsize = asttools.GetSize()
            getsize.visit(target_ast)
            if getsize.result:
                self.nbits = getsize.result
            # default bitsize is 8
            else:
                self.nbits = 8
        else:
            self.nbits = nbits

    def basic_visit(self, node):
        'Check if node is matching the pattern, if not, visit children'
        pat = PatternMatcher(node, self.nbits)
        matched = pat.visit(node, self.patt_ast)
        if matched:
            repc = deepcopy(self.rep_ast)
            new_node = EvalPattern(pat.wildcards).visit(repc)
            return new_node
        else:
            return self.generic_visit(node)

    def visit_Call(self, node):
        'No particular case for Call replacement'
        return self.basic_visit(node)

    def visit_BinOp(self, node):
        'No particular case for BinOp replacement'
        return self.basic_visit(node)

    def visit_UnaryOp(self, node):
        'No particular case for UnaryOp replacement'
        return self.basic_visit(node)

    def visit_BoolOp(self, node):
        'Check if BoolOp is exaclty matching or contain pattern'

        if isinstance(self.patt_ast, ast.BoolOp):
            if len(node.values) == len(self.patt_ast.values):
                return self.basic_visit(node)
            elif len(node.values) > len(self.patt_ast.values):
                # associativity n to m
                for combi in itertools.combinations(node.values,
                                                    len(self.patt_ast.values)):
                    rest = [elem for elem in node.values if elem not in combi]
                    testnode = ast.BoolOp(node.op, list(combi))
                    pat = PatternMatcher(testnode, self.nbits)
                    matched = pat.visit(testnode, self.patt_ast)
                    if matched:
                        new = EvalPattern(pat.wildcards).visit(self.rep_ast)
                        new = ast.BoolOp(node.op, [new] + rest)
                        new = Unflattening().visit(new)
                        return new
            return self.generic_visit(node)

        if isinstance(self.patt_ast, ast.BinOp):
            if type(node.op) != type(self.patt_ast.op):
                return self.generic_visit(node)
            op = node.op
            for combi in itertools.combinations(node.values, 2):
                rest = [elem for elem in node.values if elem not in combi]
                testnode = ast.BinOp(combi[0], op, combi[1])
                pat = PatternMatcher(testnode, self.nbits)
                matched = pat.visit(testnode, self.patt_ast)
                if matched:
                    new_node = EvalPattern(pat.wildcards).visit(self.rep_ast)
                    new_node = ast.BoolOp(op, [new_node] + rest)
                    new_node = Unflattening().visit(new_node)
                    return new_node
        return self.generic_visit(node)


def replace(target_str, pattern_str, replacement_str):
    'Apply pre-processing and replace'
    target_ast = ast.parse(target_str, mode="eval").body
    target_ast = pre_processing.all_preprocessings(target_ast)
    target_ast = Flattening(ast.Add).visit(target_ast)
    patt_ast = ast.parse(pattern_str, mode="eval").body
    patt_ast = pre_processing.all_preprocessings(patt_ast)
    patt_ast = Flattening(ast.Add).visit(patt_ast)
    rep_ast = ast.parse(replacement_str)
    rep = PatternReplacement(patt_ast, target_ast, rep_ast)
    return rep.visit(target_ast)


# Used for debug purposes:
if __name__ == '__main__':
    # pylint: disable=invalid-name
    patt_string = "A + B - (A | B)"
    test = "f(g(x + x) + 3 + 4)"
    repl = "A & B"

    print(match(test, patt_string))
    print("-"*80)
    out = replace(test, patt_string, repl)
    print(ast.dump(out))
    out = Unflattening().visit(out)
    print(astunparse.unparse(out))
