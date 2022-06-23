#!/usr/bin/python3
"""
simplify the MBA expression by the truth table searching:
    step1: get the entire truth table, then transform it into the linear combination of basis.
    step2: split the MBA expression, replace every bitwise expression with the related basis.
    step3: simplify the MBA expression into the conbination of basis.
    trick: replace the basis with variable, simplify the MBA expression by the sympy library.
"""
import io
import numpy as np
import re
import sympy
import sys
sys.path.append("../tools")
import z3
from argparse import ArgumentParser
from typing import Any, List, Optional, Tuple, Union

# FIX: imported by me
import logging
def setup_logging() -> logging.Logger:
    logger = logging.getLogger("MBA-Blast")
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('debug.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s | %(processName)-17s - "
        "%(levelname)-8s: %(message)s"))
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter(
        "%(levelname)-8s: %(message)s"))
    #    "%(name)s | %(processName)-17s - %(levelname)-8s: %(message)s"))
    # logger.addHandler(file_handler)
    # logger.addHandler(console_handler)
    return logger
logger = setup_logging()
### end fix


def postfix(itemString: str) -> str:
    """transform infixExpre into postfixExpre
    Algorithm:
        step1: if operator, stack in;
        step2: if "(", stack in.
        step3: if variable, pop out the all continued unary operator until other operator or "("
        step4: if ")", pop out all operators until "(", then pop all continued unary operator.
        step5: goto step1.
    Arg:
        itemString: bitwise expression string persented in infix.
    Return:
        itemStr: expression string persented in postfix.
    """
    logger.debug(f"postfix(itemString={itemString} (type={type(itemString)}))")
    itemStr = ""
    boperatorList = ["&", "|", "^"]
    uoperator = "~"
    opeList = []

    for (idx, char) in enumerate(itemString):
         #open parenthesis, stack it
        if char == "(":
            opeList.append(char)
        #binary operatork, stack it
        elif char in boperatorList:
            opeList.append(char)
        #unary operator
        elif uoperator in char:
            opeList.append(char)
        #closed parenthesis, pop out the operator to string
        elif char == ")":
            while(opeList and opeList[-1] != "("):
                itemStr += opeList[-1]
                opeList.pop()
            if opeList and opeList[-1] != "(":
                raise RuntimeError("expected (")
            #open parenthesis found
            opeList.pop()
            #unary operator found before open parenthesis
            while(opeList and opeList[-1] == "~"):
                itemStr += opeList[-1]
                opeList.pop()
        #variable name found
        else:
            itemStr += char
            #top of stack is unary operator
            while(opeList and opeList[-1] in uoperator):
                itemStr += opeList[-1]
                opeList.pop()

    if len(opeList) > 1:
        raise RuntimeError("error in function postfix!")
    #have one operator without parenthesis
    elif len(opeList):
        itemStr += opeList[0]

    print(f"  -> postfix={itemStr}")
    return itemStr


def postfix_cal(itemString: str, vnumber: int = 0) -> List[int]:
    """calculate the result of the expression string.
    Args:
        itemString: bitwise expression string persented in postfix.
        vnumber: the number of variables.
    Returns:
        result: the result list of the expression string.
    Raises:
        through out SystemExit exception.
    """
    logger.debug(f"postfix_cal(itemString={itemString}(type={type(itemString)}), vnumber={vnumber}(type={type(vnumber)})")
    if vnumber == 1:
        x = [0,1]
    elif vnumber == 2:
        y = [0, 1, 0, 1]
        x = [0, 0, 1, 1] 
    elif vnumber == 3:
        y = [0, 1, 0, 1, 0, 1, 0, 1]
        x = [0, 0, 1, 1, 0, 0, 1, 1]
        z = [0, 0, 0, 0, 1, 1, 1, 1]
    elif vnumber == 4:
        y = [0, 1] * 8
        x = [0, 0, 1, 1] * 4
        z = [0] * 4 + [1] * 4 + [0] * 4 + [1] * 4
        t = [0] * 8 + [1] * 8
    else:
        raise NotImplementedError(f"Currently only 1 - 4 variables are supported")
    variableList = ["x", "y", "z", "t"]
    binaryOperator = ["&", "|", "^"]
    unaryOperator = ["~"]

    stack: List[List[int]] = []
    for c in itemString:
        # logger.debug(f"  c={c}")
        if c in variableList:
            # logger.debug(f"  insert={eval(c)}(type={type(eval(c))})")
            stack.insert(0, eval(c))
        elif c in unaryOperator:
            operation = stack.pop(0)
            res = np.invert(operation)
            res = res % 2
            # logger.debug(f"  insert={res}(type={type(res)})")
            stack.insert(0, res)
        elif c in binaryOperator:
            operation1 = stack.pop(0)
            operation2 = stack.pop(0)
            if c == "&":
                res = np.bitwise_and(operation1, operation2)
                # logger.debug(f"  insert={res}(type={type(res)})")
                stack.insert(0, res)
            elif c == "|":
                res = np.bitwise_or(operation1, operation2)
                # logger.debug(f"  insert={res}(type={type(res)})")
                stack.insert(0, res)
            elif c == "^":
                res = np.bitwise_xor(operation1, operation2)
                # logger.debug(f"  insert={res}(type={type(res)})")
                stack.insert(0, res)
        else: # FIX: added by me
            logger.debug(f"FIX: c was neither in variableList, unaryOperator, nor binaryOperator: {c}")

    if len(stack) > 1:
        raise RuntimeError("postfix_cal: stack > 1")
    result: Union[List[int], "np.ndarray"] = stack[0]
    # logger.debug(f"  result={result}(type={type(result)})")
    if isinstance(result, list):
        pass
    else:
        assert isinstance(result, np.ndarray), f"FIX: expected np.array, found type {type(result)}"
        result = result.tolist()
        # logger.debug(f"  result.tolist()={result}(type={type(result)})")

    assert isinstance(result, list)
    print(f"  -> postfix_cal={result}")
    return result



def verify_mba_unsat(leftExpre: str, rightExpre: str, bitnumber: int = 2) -> bool:
    """check the relaion whether the left expression is euqal to the right expression.
    Args:
        leftExpre: left expression.
        rightExpre: right expression.
        bitnumber: the number of the bits of the variable.
    Returns:
        True: equation.
        False: unequal.
    Raises:
        None.
    """
    logger.debug(f"verify_mba_unsat(...)")
    x,y,z,t,a,b,c,d,e,f = z3.BitVecs("x y z t a b c d e f", bitnumber)

    leftEval = eval(leftExpre)
    rightEval = eval(rightExpre)

    solver = z3.Solver()
    solver.add(leftEval != rightEval)
    result = solver.check()

    if str(result) != "unsat":
        return False
    else:
        return True



def truthtable_term_list(termList: List[str], vnumber: int = 0) -> List[int]:
    """obtain the result vector based on the term list on mba expression.
    Args:
        termList: mba expression string splited by the + or - operator.
        vnumber: the number of variable.
    Returns:
        result: the result vector presenting by np.array format of the mba expression.
    Raises:
        through out SystemExit exception.
    """
    logger.debug(f"truthtable_term_list(termList={termList} (type={type(termList)}), vnumber={vnumber} = 0 (type={type(vnumber)}))")
    #function call error
    if not vnumber:
        raise RuntimeError(f"vnumber must be [1-4] - is {vnumber}")
    #empty expression
    if not termList:
        return [0] * 2**vnumber
    result = np.zeros((2**vnumber,), dtype=int) # replaced dtype=np.int by int (deprecationwarning)
    for item in termList:
        itemList = re.split("\*", item)
        #only bitwise expression or constant
        if len(itemList) == 1:
            bitwiseExpre = itemList[0]
            if bool(re.search("\d", bitwiseExpre)):
                #constant
                result += np.array([int(bitwiseExpre) * -1] * 2**vnumber)
            else:
                #only bitwise expression
                if bitwiseExpre[0] == "+":
                    result += np.array(truthtable_bitwise(bitwiseExpre[1:], vnumber))
                elif bitwiseExpre[0] == "-":
                    result -= np.array(truthtable_bitwise(bitwiseExpre[1:], vnumber))
                else:
                    result += np.array(truthtable_bitwise(bitwiseExpre, vnumber))
        #coefficient and bitwise
        elif len(itemList) == 2:
            coefficient = int(itemList[0])
            bitwiseExpre = itemList[1]
            result += coefficient * np.array(truthtable_bitwise(bitwiseExpre, vnumber))

    fix_result: List[int] = result.tolist()
    return fix_result


def truthtable_bitwise(bitExpre: str, vnumber: int) -> List[int]:
    """generate the truth table of a bitwise expression.
    Args:
        bitExpre: a bitwise expression.
        vnumber: the number of variables in a expression.
    Returns:
        truthList: a truth table on a format of list.
    """
    logger.debug(f"truthtable_bitwise(bitExpre={bitExpre} (type={type(bitExpre)}), vnumber={vnumber} (type={type(vnumber)}))")
    truthList = postfix_cal(postfix(bitExpre), vnumber)
    print(f"{bitExpre} -> {truthList}")

    return truthList



def truthtable_expression(expreStr: str, vnumber: int) -> List[int]:
    """generate the truth table on a linear MBA expression.
    Args:
        expreStr: a linear MBA expression.
        vnumber: the number of variables in a expression.
    Returns:
        truthtalbeList: a truth table on a format of list.
    """
    logger.debug(f"truthtable_expression(expreStr={expreStr} (type={type(expreStr)}), vnumber={vnumber} (type={type(vnumber)}))")
    termList = expression_2_term(expreStr)

    #truth table of bitwise expression 
    truthtableList = truthtable_term_list(termList, vnumber)

    return truthtableList


def expression_2_term(expreStr: str) -> List[str]:
    """generate the truth table on a linear MBA expression.
    Args:
        expreStr: a linear MBA expression.
    Returns:
        termList: a list of terms on bitwise expression.
        constantList: a list of constant term of the linear MBA expression.
    """
    logger.debug(f"expression_2_term(expreStr={expreStr} (type={type(expreStr)}))")
    itemList = re.split("([\+-])", expreStr)
    print(f"  itemList={itemList}")
    item0 = itemList[0]
    print(f"  item0='{item0}'")
    termList = []
    constantList = []
    if item0 != "":
        itemList.insert(0, "")
        print(f"  itemList={itemList} (inserted \"\")")
    for (idx, item) in enumerate(itemList):
        print(f"  idx={idx}, item='{item}'")
        if item == "+" or item == "-" or item == "":
            print(f"    skip (is '', '+', '-')")
            continue
        #bitwise term
        elif re.search("\w+", item):
            term = itemList[idx - 1] + itemList[idx]
            print(f"    term={term}")
            termList.append(term)
        #constant term
        elif re.search("\d+", item):
            term = itemList[idx - 1] + itemList[idx]
            print(f"    constant={term}")
            constantList.append(term)
        else:
            raise RuntimeError(f"expression_2_term failed: This is something wrong in mba expression: idx={idx}, item={item}")

    return termList +  constantList


def generate_coe_bit(mbatermList: List[str]) -> List[List[str]]:
    """split the one term into pair, [coe, bit]
    Arg:
        mbatermList: one list of terms.
    Return:
        coeBitList: one list of pair [coe, bit]
    """
    logger.debug(f"generate_coe_bit(mbatermList={mbatermList} (type={type(mbatermList)}))")
    coeBitList = []
    for term in mbatermList:
        itemList = re.split("\*", term)
        maycoe= itemList[0]
        #not coefficient
        if not bool(re.search("\d", maycoe)):
            bit = itemList[0]
            bit = bit.replace("+", "")
            if "-" not in term:
                coe = 1
            else:
                coe = -1
                bit = bit.replace("-", "")
            coeBitList.append([str(coe), bit]) # FIX: added str(), original code would mix int and str
        #multi bitwise expression
        elif len(itemList) >= 2:
            #1 is for the first time synbol
            bit = term[len(maycoe)+1:]
            coeBitList.append([maycoe, bit])
        #only constant
        elif len(itemList) == 1 and bool(re.search("\d", maycoe)):
            coeValue = int(maycoe) * -1
            coeBitList.append([str(coeValue), "~(x&~x)"])
            
        else:
            print("error in function of generate_coe_bit")
            exit(0)

    return coeBitList 


def combine_term(mbaExpre: str) -> str:
    """combining like terms of the mba expression
    Args:
        mbaExpre: the mba expression.
    Return:
        newmbaExpre: new mba expression have combined like terms.
    """
    logger.debug(f"combine_term(mbaExpre={mbaExpre} (type={type(mbaExpre)}))")
    #get pair of coefficient and bitwise on the mba expression
    termList = expression_2_term(mbaExpre)
    coeBitList = generate_coe_bit(termList)

    #firstly sort the list
    coeBitList = sorted(coeBitList, key=lambda x: x[1])
    #walk the list and combine like terms
    newcoeBitList = []
    itemList = coeBitList[0]
    for item in coeBitList[1:]:
        if item[1] != itemList[1]:
            #delete 0 term
            if itemList[0] != "0":
                newcoeBitList.append(itemList)
            itemList = item
        else:
            coe1 = itemList[0]
            coe2 = item[0]
            coe = eval(coe1) + eval(coe2)
            itemList[0] = str(coe)
    #handle the last one term
    if newcoeBitList[-1][1] != itemList[1]:
        newcoeBitList.append(itemList)
    #coefficent and bitwise expression to terms
    newtermList = []
    for item in newcoeBitList:
        coe = item[0]
        bit = item[1]
        if coe[0] == "+" or coe[0] == "-":
            term = "{coe}*{bit}".format(coe=coe, bit=bit)
        else:
            coe = "+" + coe
            term = "{coe}*{bit}".format(coe=coe, bit=bit)
        newtermList.append(term)
    #terms to expression
    newmbaExpre = "".join(newtermList) 
    if newmbaExpre[0] == "+":
        newmbaExpre = newmbaExpre[1:]
    #verification
    z3res = verify_mba_unsat(mbaExpre, newmbaExpre)
    if not z3res:
        raise RuntimeError("error in merge_bitwise!")
    return newmbaExpre




def addMBA(mbaExpre1: str, mbaExpre2: str) -> str:
    """two mba expression addition.
    Args:
        mbaExpre1: one MBA expression.
        mbaExpre2: another one MBA expression.
    Return:
        mbaExpre: the mba expression by addition of mbaExpre1 and mbaExpre2
    """
    logger.debug(f"addMBA(mbaExpre1={mbaExpre1} (type={type(mbaExpre1)}), mbaExpre2={mbaExpre2} (type={type(mbaExpre2)}))")
    #get the coefficient and related bitwise 
    mbaterm1List = expression_2_term(mbaExpre1)
    coeBitList1 = generate_coe_bit(mbaterm1List)
    coeBitDict1 = {}
    for item in coeBitList1:
        coeBitDict1[item[1]] = item[0]
    mbaterm2List = expression_2_term(mbaExpre2)
    coeBitList2 = generate_coe_bit(mbaterm2List)
    coeBitDict2 = {}
    for item in coeBitList2:
        coeBitDict2[item[1]] = item[0]

    commonKey = set(coeBitDict1.keys()) & set(coeBitDict2.keys())
    for key in commonKey:
        coe1 = coeBitDict1[key]
        coe2 = coeBitDict2[key]
        res = eval(coe1) + eval(coe2)
        if not res:
            coeBitDict1.pop(key)
        else:
            coeBitDict1[key] = str(res)
        coeBitDict2.pop(key)
    #the last pair of coefficient and bitwise
    coeBitDict = coeBitDict1
    coeBitDict.update(coeBitDict2)
    termList = []
    for item_tup in coeBitDict.items():
        term = item_tup[1] + "*" + item_tup[0]
        if term[0] == "-" or term[0] == "+":
            termList.append(term)
        else:
            term = "+" + term
            termList.append(term)
    #construct the mba expression
    mbaExpre = "".join(termList)
    if mbaExpre[0] == "+":
        mbaExpre = mbaExpre[1:]

    #verification
    oriExpre = ""
    if mbaExpre2[0] == "+" or mbaExpre2[0] == "-":
        oriExpre = mbaExpre1 + mbaExpre2
    else:
        oriExpre = mbaExpre1 + "+" + mbaExpre2
    z3res = verify_mba_unsat(oriExpre, mbaExpre)
    if not z3res:
        raise RuntimeError("error in addMBA: simplification != original expression")

    return mbaExpre


def variable_list(expreStr: str) -> List[str]:
    """get the set of variable of expression.
    Args:
        expreStr: the mba expression string.
    Return:
        variableList: the list of variables.
    """
    logger.debug(f"variable_list(expreStr={expreStr} (type={type(expreStr)}))")
    varSet = set(expreStr)
    variableList = []
    for i in varSet:
        #the variable name
        if i in ["x", "y", "z", "t", "a", "b", "c", "d", "e", "f"]:
            variableList.append(i)

    return variableList

def get_entire_bitwise(vnumber: int) -> List[str]:
    """get the entire bitwise expression of 2/3/4-variable.
    Args:
        vnumber: the number of the variables.
    Return:
        bitList: the entire bitwise expression.
    """
    logger.debug(f"get_entire_bitwise(vnumber={vnumber} (type={type(vnumber)}))")
    if not vnumber in [1, 2,3,4]:
        raise RuntimeError(f"vnumber must be [1-4], is - {vnumber}")
    truthfile = "./dataset/{vnumber}variable_truthtable.txt".format(vnumber=vnumber)
    bitList = []
    with open(truthfile, "r") as fr:
        for line in fr:
            if "#" not in line:
                line = line.strip()
                itemList = re.split(",", line)
                bit = itemList[1]
                bitList.append(bit)

    return bitList

class MBASimplify(object):
    """
    Attributes:
        vnumber: the number of variable in one expression.
        basisList: the basis vector.
        truthBasisList: the related truth of the basis vector.
        bitTruthList: transform every one truth into the linear combination of the basis.
        middleNameList: in order to simplify the expression by  the temp variable.
    """

    def __init__(self, vnumber: int, basisList: List[str]) -> None:
        logger.debug(f"MBASimplify.__init__(vnumber={vnumber} (type={type(vnumber)}), basisList={basisList} (type={type(basisList)}))")
        self.vnumber = vnumber
        self.basisList = basisList
        self.truthBasisList = []
        for bit in self.basisList:
            print(f"  bit={bit}")
            self.truthBasisList.append(truthtable_bitwise(bit, vnumber))
        print(f"truthBasisList={self.truthBasisList}")
        #transform bitwise to the combination of basis
        logger.info("transform bitwise to the combination of basis")
        self.bitTruthList = self.bit_2_basis()
        #temp variable
        self.middleNameList = []
        for i in range(2 ** self.vnumber):
            vname = "X{num}".format(num=i)
            self.middleNameList.append(vname)
        print(f"middleNameList={self.middleNameList}")
        print("-----------------------------------INIT DONE--------------------------------------")
        return None


    def bit_2_basis(self) -> List[List[int]]:
        """get entire truth table, create the linear combination of every bitwise expression, just store the coefficient of every term.
        Args:
            None
        Returns:
            bitTruthList: the list of basis on every one bitwise expression.
        """
        logger.debug(f"MBASimplify.bit_2_basis() -- get entire truth table, create the linear combination of every bitwise expression, just store the coefficient of every term.")
        bitList = get_entire_bitwise(self.vnumber)
        print(f"bitList={bitList}")
        bitTruthList: List[List[int]] = []

        print(f"  self.truthBasisList={self.truthBasisList}")
        A = np.mat(self.truthBasisList).T
        print(f"  A={A}")
        for bit in bitList:
            print(f"  bit={bit}")
            truth = truthtable_bitwise(bit, self.vnumber)
            print(f"  truth={truth}")
            b = np.mat(truth).T
            print(f"  b={b}")
            resMatrix = np.linalg.solve(A, b)
            print(f"  resMatrix={resMatrix}")
            resList = np.array(resMatrix).reshape(-1,).tolist()
            resList = [int(i) for i in resList]
            print(f"  resList={resList}")
            bitTruthList.append(resList)

        return bitTruthList


    def process_term(self, term: str) -> Optional[str]:
        """
            step2: for every term, split the term into coeffcient and bitwise expression.
            step3: for the bitwise, transform it into linear combination of temp variable name.
            step4: construct every term into the multiplication of temp variable name.
            step5: goto step2, until loop end.
        """
        print(f"  " + "-"*16)
        print(f"  term={term}")
        #split the term
        itemList: List[str] = re.split("\*", term)
        print(f"    itemList={itemList}")
        assert len(itemList), f"FIX: len(itemList) == 0 in MBASimplify.simplify"
        #the term is constant
        if len(itemList) == 1:
            if not re.search("[a-z]", itemList[0]):
                coe_int = int(itemList[0])
                if coe_int < 0:
                    coeStr = "+{coe}".format(coe=abs(coe_int))
                    itemList = [coeStr, "~(x&~x)"]
                elif coe_int > 0:
                    coeStr = "-{coe}".format(coe=coe_int)
                    itemList = [coeStr, "~(x&~x)"]
                print(f"    -> itemList={itemList}")
            else:
                print(f"    item contains variable (is not constant)")
        #get the coefficient
        coe: str = itemList[0]
        if not re.search("\d", coe):
            itemList.insert(0, "")
            if coe[0] == "-":
                coe = "-1"
            else:
                coe = "+1"
            print(f"    coe set to '{coe}'")
        else:
            print(f"    coe already set")
        bitTransList = []
        #transform every bitwise expression into linear combination of basis
        logger.debug("transform every bitwise expression into linear combination of basis")
        for bit in itemList[1:]:
            print(f"      bit={bit}")
            truth = truthtable_bitwise(bit, self.vnumber)
            print(f"      truth={truth}")
            #get the index of truth table
            index = 0
            for (idx, value) in enumerate(truth):
                index += value *  2**idx
            print(f"      index={index}")
            #transform the truth table to the related basis
            print(f"      self.bitTruthList={self.bitTruthList}")
            basisVec = self.bitTruthList[index]
            print(f"      basisVec={basisVec}")
            basisStrList = []
            for (idx, value) in enumerate(basisVec):
                if value < 0:
                    basisStrList.append(str(value) + "*" + self.middleNameList[idx]) 
                elif value > 0:
                    basisStrList.append("+" + str(value) + "*" + self.middleNameList[idx]) 
            #construct one bitwise transformation 
            basisStr = "".join(basisStrList)
            print(f"      basisStrList={basisStrList}")
            if basisStr:
                if basisStr[0] == "+":
                    basisStr = basisStr[1:]
                #one bitwise transformation
                bitTransList.append("({basis})".format(basis=basisStr))
                print(f"      bitTransList={bitTransList}")
        #not zero 
        if bitTransList:
            #construct the entire term.
            bitTrans = "*".join(bitTransList)
            #contain coefficient
            bitTrans = coe + "*" + bitTrans
            print(f"      bitTrans={bitTrans}")
            return bitTrans
        return None


    def parse_subexpression(self, expr: str, depth: int = 0) -> Tuple[int, str, bool]:
        new_expr = ""
        print("-"*64)
        print(f"parse_subexpression({expr}, depth={depth})")
        if depth > 100:
            raise RuntimeError(f"Recursion error")
        num_skip = 0
        has_arith = False
        inner_stack: List[Tuple[str, bool]] = []
        # inner_expr = ""
        # inner_has_arith = False # in case we have no inner, set this to False
        for (i, c) in enumerate(expr):
            if num_skip:
                # print("skipped!")
                num_skip -= 1
                continue
            print(f"i={i}, c={c}, depth={depth}, new_expr={new_expr} -- {expr}")
            print(" "*(2+len(str(i))+5+8+len(str(depth))+11+len(new_expr)+4) + " "*i + "^")
            if c == "(":
                # recursively call this function again to resolve inner term
                # we return both how many chars were processed in the inner term and the term itself
                num_skip, inner_expr, inner_has_arith = self.parse_subexpression(expr[i+1:], depth=depth + 1)
                inner_stack.append((inner_expr, inner_has_arith))
                num_skip += 1 # we need to account for ")" as well
                new_expr += "(" + inner_expr + ")"
            elif c == ")":
                # if none of the inner expressions contain arithmetic, we can simplify the whole
                if not any(map(lambda inner: inner[1], inner_stack)):
                    print("="*32)
                    print(f"can simplify: {new_expr}")
                    old = new_expr
                    try:
                        simplified_expr = self.simplify(new_expr)
                        if "+" in simplified_expr or "-" in simplified_expr:
                            print(f"refusing simplification: {old} -> {new_expr} <" + "~"*70)
                        else:
                            new_expr = simplified_expr
                        print("="*16 + "DONE" + "="*16)
                        print(f"simplified: {old} -> {new_expr} <" + "~"*70)
                    except Exception as e:
                        logger.error(f"Skipping simplification -- raised: {str(e)}\ntried: {new_expr}")
                ret_has_arith = has_arith or any(map(lambda inner: inner[1], inner_stack))
                print(f"return len={i}, {new_expr}, has_arith={ret_has_arith}")
                print("-"*16)
                return i, new_expr, ret_has_arith
            else:
                new_expr += c
                if c in ("+", "-"):
                    has_arith = True
        # if none of the inner expressions contain arithmetic, we can simplify the whole
        if not any(map(lambda inner: inner[1], inner_stack)):
            if "+" in new_expr or "-" in new_expr:
                print(f"can simplify: {new_expr}")
                old = new_expr
                try:
                    new_expr = self.simplify(new_expr)
                    print(f"simplified: {old} -> {new_expr} <" + "~"*70)
                except Exception as e:
                    logger.error(f"Skipping simplification -- raised: {str(e)}\ntried: {new_expr}")
            else:
                print(f"Only boolean arithmetic here.. not simplifying {new_expr}")
        ret_has_arith = has_arith or any(map(lambda inner: inner[1], inner_stack))
        print(f"return {len(expr) - 1}, {new_expr}, {ret_has_arith} -- string done")
        return len(expr) - 1, new_expr, ret_has_arith


    def simplify_non_normalized(self, mbaexpre: str) -> str:
        # parse all subexpressions
        print(f"initial mba_expr={mbaexpre}")
        if len(mbaexpre) > 1:
            while mbaexpre[0] == "(" and mbaexpre[-1] == ")":
                mbaexpre = mbaexpre[1:-1]
        res = self.parse_subexpression(mbaexpre)
        return res[1]


    def simplify(self, mbaExpre: str) -> str:
        """simplify the MBA expression.
        Algorithm:
            step1: split the expression into list of terms.
            step2: for every term, split the term into coeffcient and bitwise expression.
            step3: for the bitwise, transform it into linear combination of temp variable name.
            step4: construct every term into the multiplication of temp variable name.
            step5: goto step2, until loop end.
            step6: apply sympy to simplify the transformation.
            step7: replace the temp variable name with bitwise expression in the simplified expression.
        Arg:
            mbaExpre: MBA expression.
        Return:
            resExpre: the related simplified MBA expression.
        """
        logger.debug(f"MBASimplify.simplify(mbaExpre={mbaExpre} (type={type(mbaExpre)}))")
        #split the expression into terms
        logger.info("Stage 1: convert expression into terms")
        termList = expression_2_term(mbaExpre)
        logger.debug(f"Term parsing done -- found {len(termList)} terms")
        print(f"termList from expression_2_term: termList={termList}")
        print("+"*32 + "Stage 1 done" + "+"*32)
        newtermList = []
        logger.info("Stage 2: apply magic onto terms")
        print(f"process all terms in list:")
        for term in termList:
            bitTrans = self.process_term(term)
            if bitTrans:
                newtermList.append(bitTrans)
        # TODO: hacky catch to avoid nasty situation with empty newtermList
        if not newtermList:
            logger.warning(f"Failed to find new terms -> returning original expression")
            return mbaExpre # no simplification possible
        print("-"*12 + "terms processed" + "-"*12)
        print(f"  newtermList={newtermList}")
        #construct the transformation temp result
        midExpre = "".join(newtermList)
        print(f"  midExpre={midExpre}")
        print("+"*32 + "Stage 2 done" + "+"*32)
        logger.info("Stage 3: Pass transformed formula to sympy")
        #simplify the temp result, but must process the power operator
        resExpre = self.sympy_simplify(midExpre)
        print(f"  resExpre={resExpre}")
        resExpre = resExpre.strip()
        resExpre = resExpre.replace(" ", "")
        resExpre = self.power_expand(resExpre)
        #replace the temp variable name with real bitwise expression
        #for (idx, var) in enumerate(self.middleNameList):
        for idx in range(len(self.middleNameList)-1, -1, -1):
            var = self.middleNameList[idx]
            basis = self.basisList[idx]
            resExpre = resExpre.replace(var, basis)
        print(f"  -> resExpre={resExpre}")

        #verification
        z3res = verify_mba_unsat(mbaExpre, resExpre)
        if not z3res:
            logger.error(f"z3 proved: {mbaExpre} != {resExpre}")
            raise RuntimeError("error in simplify MBA expression: mbaExpre != resExpre")

        return resExpre


    def sympy_simplify(self, mbaExpre: str) -> str:
        """simplify the mba expression by the sympy library.
        Args:
            mbaExpre: the mba expression.
        Returns:
            newmbaExpre: the simplified mba expression.
        """
        logger.debug(f"MBASimplify.sympy_simplify(mbaExpre={mbaExpre} (type={type(mbaExpre)}))")
        #variable symbols
        if self.vnumber in [1, 2, 3, 4]:
            X0 = sympy.symbols("X0")
            X1 = sympy.symbols("X1")
            X2 = sympy.symbols("X2")
            X3 = sympy.symbols("X3")
            X4 = sympy.symbols("X4")
            X5 = sympy.symbols("X5")
            X6 = sympy.symbols("X6")
            X7 = sympy.symbols("X7")
            X8 = sympy.symbols("X8")
            X9 = sympy.symbols("X9")
            X10 = sympy.symbols("X10")
            X11 = sympy.symbols("X11")
            X12 = sympy.symbols("X12")
            X13 = sympy.symbols("X13")
            X14 = sympy.symbols("X14")
            X15 = sympy.symbols("X15")
        else:
            raise RuntimeError("error in sympy_simplify: wrong vnumber")
        #simplify it
        resExpre = sympy.simplify(eval(mbaExpre))
        return str(resExpre) # FIX: rather than hijacking stdout, we just return a string
        print(f"resExpre={resExpre} (type={type(resExpre)})")
        print(f"resExpre={str(resExpre)} (type={type(str(resExpre))})")
        #output the result to a variable
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        print(resExpre, end="")
        newmbaExpre = new_stdout.getvalue()
        sys.stdout = old_stdout

        print(f"newmbaExpre={newmbaExpre} (type={type(newmbaExpre)})")

        return newmbaExpre


    def power_expand(self, mbaExpre: str) -> str:
        """since the sympy simplification expression contains power operator, which is unaccepted by solver,we expand the power operator.
        Args:
            mbaExpre: mba expression.
        Returns:
            newmbaExpre: the expanded mba expression.
        """
        logger.debug(f"MBASimplify.power_expand(mbaExpre={mbaExpre} (type={type(mbaExpre)}))")
        #split the expression by power operator.
        itemList = re.split("(\*\*)", mbaExpre)

        breakFlag = False
        for (idx, item) in enumerate(itemList):
            if r"**" in item:
                #pre/post-item of the power operator
                preStr = itemList[idx - 1]
                postStr = itemList[idx + 1]
                #get the one operand of power operator -- variable name
                splitList = re.split("\*", preStr)
                splitList = re.split("[\+-]", splitList[-1])
                varName = splitList[-1]
                #get the one operand of power operator -- value
                count_str = ""
                for (i, c) in enumerate(postStr):
                    #the beginning character must be a number
                    if re.search("\d", c):
                        count_str += c
                    else:
                        breakFlag = True
                        break
                count = int(count_str)
                #remove the value from the postStr
                if breakFlag:
                    itemList[idx + 1] = itemList[idx + 1][i:]
                    breakFlag = False
                else:
                    itemList[idx + 1] = itemList[idx + 1][i+1:]
                    breakFlag = False
                #expand the power operator
                #the number of 1 is because the preStr have one variable name
                powerList = [varName] * (count - 1)
                powerStr = "*" + "*".join(powerList)
                #replace the power operator with proper expression
                itemList[idx] = powerStr
            else:
                continue

        newmbaExpre = "".join(itemList)

        return newmbaExpre


def refine_simplification(resultVector: List[int], vnumber: int) -> Tuple[bool, str]:
    """after get the result vector, refine the result expression.
    Args:
        resultVector: the result vector of the mba expression.
        vnumber: the number of variables in the expression.
    Return:
        (True, simExpre): sucessfully refine the result expression.
        (False,): the result expression can't be refined.
    Raise:
        None.
    """
    logger.debug(f"refine_simplification(resultVector={resultVector} (type={type(resultVector)}), vnumber={vnumber} (type={type(vnumber)}))")
    truthtableList = get_entire_bitwise(vnumber)

    #refine the simplification result
    resultSet = set(resultVector)
    if len(resultSet) == 1:
        coefficient = resultSet.pop()
        if coefficient == 0:
            raise RuntimeError("refine_simplification: vector calculation error! coefficient == 0")
        else:
            simExpre = str(-1 * coefficient)
            return (True, simExpre)
    elif len(resultSet) == 2 and (0 in resultSet):
        coefficient = resultSet.pop()
        if coefficient == 0:
            coefficient = resultSet.pop()
            if coefficient == 0:
                raise RuntimeError("refine_simplification: vector calculation error! coefficient == 0")
        index = 0
        for i in range(len(resultVector)):
            if resultVector[i]:
                index += 2**i
        simExpre = str(coefficient) + "*" + truthtableList[index]
        return (True, simExpre)
    else:
        return (False, "") # FIX: added "" to fix this mess -- caller must ensure tup[0] is True though


def refine_mba(mbaExpre: str, vnumber: int) -> str:
    """after simplification, refine the simplified expression.
    Args:
        mbaExpre: the expression after simplification.
        vnumber: the number of variable in the mba expression.
    Returns:
        resList[1]: the new expression after refining.
        mbaExpre: cannot be refined, return the orignal mba expression.
    """
    logger.debug(f"refine_mba(mbaExpre={mbaExpre} (type={type(mbaExpre)}), vnumber={vnumber} (type={type(vnumber)}))")
    truthList = truthtable_expression(mbaExpre, vnumber)
    resList = refine_simplification(truthList, vnumber)

    if resList[0]:
        return resList[1]
    else:
        return mbaExpre


def simplify_MBA(mbaExpre: str) -> Tuple[str, int, str]:
    """simplify a MBA expression.
    Args:
        mbaExpre: a MBA expression.
    Returns:
        simExpre: a expression after simplification.
        vnumber: the nubmer of variable in the mba expression.
        replaceStr: the variable name replacement relationship since our program only process the expression containing "x,y,z" variable.
    """
    logger.debug(f"simplify_MBA(mbaExpre={mbaExpre} (type={type(mbaExpre)}))")
    basisVecs = {2:["x", "y", "(x&y)", "~(x&~x)"], 3:["x", "y", "z", "(x&y)",  "(y&z)", "(x&z)", "(x&y&z)", "~(x&~x)"]}

    assert "0x" not in mbaExpre, f"Cannot deal with constants yet"
    variables = set(re.findall("[a-z]", mbaExpre))
    assert "x" in variables and "y" in variables, f"Code currently only works for x, y"
    vnumber = len(variables)
    print("+"*32 + "Stage 0" + "+"*32)
    logger.info("Stage 0: Create MBASimplify object and generate truth tables for basis vector")
    psObj = MBASimplify(vnumber, basisVecs[vnumber])
    print("+"*32 + "Stage 0 done" + "+"*32)
    simExpre = psObj.simplify_non_normalized(mbaExpre)
    return (simExpre, vnumber, "xy")



def simplify_string(mba: str, groundtruth: Optional[str]) -> str:
    cmbaExpre = mba.replace(" ", "")
    if len(cmbaExpre) > 1:
        while cmbaExpre[0] == "(" and cmbaExpre[-1] == ")":
            cmbaExpre = cmbaExpre[1:-1]
    (simExpre, vnumber, replaceStr) = simplify_MBA(cmbaExpre)
    print(f"input={cmbaExpre} -> ({simExpre}, {vnumber}, {replaceStr})")
    try:
        simExpre = refine_mba(simExpre, vnumber)
    except:
        logger.warning("Refining MBA failed")
    # if len(replaceStr) == 2:
    #     simExpre = simExpre.replace("x", replaceStr[0]).replace("y", replaceStr[1])
    # elif len(replaceStr) == 3:
    #     simExpre = simExpre.replace("x", replaceStr[0]).replace("y", replaceStr[1]).replace("z", replaceStr[2])
    # else:
    #     print("bug in simplify_dataset")
    print("complex MBA expression: ", cmbaExpre)
    print("after simplification:   ", simExpre)
    if groundtruth:
        print("z3 checking...")
        groundtruth = groundtruth.replace(" ", "")
        z3res = verify_mba_unsat(groundtruth, simExpre, 8)
        if not z3res:
            print("z3 solved: ", z3res, groundtruth, cmbaExpre, simExpre)
        else:
            print("z3 solved: ", z3res)
    else:
        print("no groundtruth provided")
    return simExpre




if __name__ == "__main__":
    parser = ArgumentParser(description="Rewrite of MBA Blast")
    parser.add_argument("mba", type=str, help="MBA to simplify")
    parser.add_argument("groundtruth", type=str, default=None, \
                            help="Groundtruth")
    args = parser.parse_args()
    simplify_string(args.mba, args.groundtruth)
