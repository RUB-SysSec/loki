from __future__ import print_function

from collections import OrderedDict
from os import popen

from miasm.core.locationdb import LocationDB
from miasm.expression.expression import *
from miasm.expression.simplifications import expr_simp
from miasm.ir.ir import AssignBlock, IRBlock
from pathlib import Path



def get_context_address(file_path: str) -> int:
    return int(popen('nm {} | grep context'.format(file_path)).read().split(" ")[0], 16)


def get_bytecode_address(file_path: str) -> int:
    return int(popen('nm {} | grep bytecode'.format(file_path)).read().split(" ")[0], 16)

def get_handler_address(file_path: str, index: int) -> int:
    return int(popen('nm {} | grep vm_alu{}_rrr_generated'.format(file_path, index)).read().split(" ")[0], 16)

def get_key(file_: Path, key_index: int) -> int:
    """Retrieve the key of the key_index-th entry"""
    with open(file_, 'rb') as byte_code_file:
        # 24 bytes = 1 entry; key is last 8 bytes
        bytecode = byte_code_file.read()[24*(key_index-1)+16:24*key_index][::-1]
    return int(''.join(['{:02x}'.format(b) for b in bytecode]), 16)

def drop_index(expr):
    if isinstance(expr, (ExprLoc, ExprInt)):
        return expr

    if isinstance(expr, ExprId):
        return ExprId(expr.name.split('.')[0], expr.size)

    if isinstance(expr, ExprAssign):
        return ExprAssign(drop_index(expr.dst), drop_index(expr.src))

    if isinstance(expr, ExprMem):
        return ExprMem(drop_index(expr.ptr), expr.size)

    if isinstance(expr, ExprOp):
        args = iter(drop_index(arg) for arg in expr.args)
        return ExprOp(expr.op, *args)

    if isinstance(expr, ExprCompose):
        args = iter(drop_index(arg) for arg in expr.args)
        return ExprCompose(*args)

    if isinstance(expr, ExprCond):
        return ExprCond(drop_index(expr.cond), drop_index(expr.src1),
                        drop_index(expr.src2))

    if isinstance(expr, ExprSlice):
        return ExprSlice(drop_index(expr.arg), expr.start, expr.stop)

    assert False, 'Unsupported expression: {}.'.format(repr(expr))


def drop_indices(cfg):
    for location, block in cfg.blocks.items():
        new_assignments = []
        for assignment in block:
            new_irs = {
                drop_index(k): drop_index(v)
                for k, v in assignment.items()
            }

            new_assignments.append(AssignBlock(new_irs, assignment.instr))

        new_block = IRBlock(block.loc_key, new_assignments)
        cfg.blocks[location] = new_block


# Append fake assignments to the CFG for each out register to make sure the
# effects of the register update are kept during DCE.
#
# `cfg` is a regular non-SSA CFG. Returns the labels of new blocks that contain
# the fake assignments.
def append_assignments(arch, cfg):
    labels = []
    for loc in cfg.leaves():
        block = cfg.blocks.get(loc)
        if block is None:
            continue

        regs = {}
        for reg in arch.get_out_regs(block):
            regs[reg] = reg

        assignments = list(block)

        new_assignment = AssignBlock(regs, assignments[-1].instr)
        assignments.append(new_assignment)

        new_block = IRBlock(block.loc_key, assignments)
        labels.append(new_block.loc_key)
        cfg.blocks[loc] = new_block

    return labels


def is_in_cfg(addr, ircfg):
    if ircfg.get_loc_key(addr) in ircfg.blocks:
        return True

    return False


def is_path_in_cfg(cfg, path):
    blocks = cfg.blocks

    for loc in path:
        if not loc in blocks:
            return False

    return True


# Remove the fake assignments, given an SSA CFG `cfg` and the versions of the
# left-hand side of all fake assignments.
def remove_assignments(arch, cfg, versions):
    # Detect whether the given key/value pair constitutes a fake assignment of
    # the same register.
    def filter_key(entry):
        key, value = entry
        if key in versions and isinstance(value, ExprId) and \
                key.name.split('.')[0] == value.name.split('.')[0]:
            return False

        return True

    # `versions` may contain IRDst which we do not want to remove.
    versions.remove(arch.IRDst)

    for loc in cfg.leaves():
        block = cfg.blocks.get(loc)
        if block is None:
            continue

        new_assignments = []
        for assignment in block:
            new_irs = dict(filter(filter_key, assignment.items()))
            new_assignments.append(AssignBlock(new_irs, assignment.instr))

        new_block = IRBlock(block.loc_key, new_assignments)
        cfg.blocks[loc] = new_block


def drop_index(expr):
    if isinstance(expr, (ExprLoc, ExprInt)):
        return expr

    if isinstance(expr, ExprId):
        return ExprId(expr.name.split('.')[0], expr.size)

    if isinstance(expr, ExprAssign):
        return ExprAssign(drop_index(expr.dst), drop_index(expr.src))

    if isinstance(expr, ExprMem):
        return ExprMem(drop_index(expr.ptr), expr.size)

    if isinstance(expr, ExprOp):
        args = iter(drop_index(arg) for arg in expr.args)
        return ExprOp(expr.op, *args)

    if isinstance(expr, ExprCompose):
        args = iter(drop_index(arg) for arg in expr.args)
        return ExprCompose(*args)

    if isinstance(expr, ExprCond):
        return ExprCond(drop_index(expr.cond), drop_index(expr.src1),
                        drop_index(expr.src2))

    if isinstance(expr, ExprSlice):
        return ExprSlice(drop_index(expr.arg), expr.start, expr.stop)

    assert False, 'Unsupported expression: {}.'.format(repr(expr))


def drop_indices(cfg):
    for location, block in cfg.blocks.items():
        new_assignments = []
        for assignment in block:
            new_irs = {
                drop_index(k): drop_index(v)
                for k, v in assignment.items()
            }

            new_assignments.append(AssignBlock(new_irs, assignment.instr))

        new_block = IRBlock(block.loc_key, new_assignments)
        cfg.blocks[location] = new_block


def to_dot(graph):
    with open('./graph-ir.dot', 'w') as f:
        # f.write(graph.graph.dot())
        f.write(graph.dot())


def native_block(block):
    previous_offset = None
    for assignment_blocks in block.assignblks:
        if not assignment_blocks.instr:
            continue

        if previous_offset == assignment_blocks.instr.offset:
            previous_offset = assignment_blocks.instr.offset
            continue

        yield assignment_blocks.instr
        previous_offset = assignment_blocks.instr.offset


def native_cfg(cfg):
    for location, block in cfg.blocks.items():
        for instr in native_block(block):
            yield instr


def show_block_ir(cfg, address):
    block = cfg.get_block(address)
    print('\n'.join(str(i) for i in block.assignblks))


def show_cfg_ir_with_instr(cfg):
    for block in cfg.blocks.values():
        for i in block.assignblks:
            print("block.instr:")
            print(i.instr)
            print("assignblks:")
            print('\n'.join(str(i) for i in block.assignblks))
            print()


def show_cfg_ir(cfg):
    for block in cfg.blocks.values():
        print("{}:".format(block.loc_key))
        for assgnblk in block.assignblks:
            # assgnblk = adjust_assgnblk(assgnblk)

            for dst, src in assgnblk.items():
                print("{} = {}".format(dst, src))

        print()


def cfg_ir_to_str(cfg):
    cfg_str = ""

    for block in cfg.blocks.values():
        cfg_str += "{}:".format(block.loc_key)
        for assgnblk in block.assignblks:
            assgnblk = adjust_assgnblk(assgnblk)

            for dst, src in assgnblk.items():
                cfg_str += "{} = {}".format(dst, src)

        cfg_str += "\n"

    return cfg_str


def adjust_assgnblk(assgnblk):
    instr_name = assgnblk.instr.name
    p_instrs = ["PUSH", "POP", "PUSHAD", "POPAD"]

    if instr_name in p_instrs:
        assgnblk = adjust_p_instrs(assgnblk)

    return assgnblk


def adjust_p_instrs(assgnblk):
    new_assgnblk = OrderedDict()
    esp_dst, esp_src = None, None

    for dst, src in assgnblk.items():
        if dst == ExprId("ESP", 32):
            esp_dst, esp_src = dst, src
        else:
            new_assgnblk[dst] = src

    if esp_dst is None or \
            esp_src is None:
        return assgnblk

    new_assgnblk[esp_dst] = esp_src

    return new_assgnblk


def _show_block_native_helper(block, previous_offset=None):
    for assignment_blocks in block.assignblks:
        if not assignment_blocks.instr:
            continue

        if previous_offset == assignment_blocks.instr.offset:
            previous_offset = assignment_blocks.instr.offset
            continue

        print('{:X} {}'.format(assignment_blocks.instr.offset,
                               assignment_blocks.instr))

        previous_offset = assignment_blocks.instr.offset

    return previous_offset


def show_block_native(cfg, address):
    return _show_block_native_helper(cfg.get_block(address))


def show_cfg_native(cfg, start_addr=None, end_addr=None):
    start_addr_reached = False

    for location, block in cfg.blocks.items():
        _a = cfg.loc_db.get_location_offset(location)
        print('{}:'.format(location))

        for instr in native_block(block):
            if (not end_addr is None and
                    instr.offset == end_addr):
                return

            if (not start_addr is None and
                    instr.offset == start_addr):
                start_addr_reached = True

            if start_addr is None:
                print('{:X} {}'.format(instr.offset, instr))
            else:
                if start_addr_reached:
                    print('{:X} {}'.format(instr.offset, instr))

        print('')


def cfg_native_to_str(cfg, start_addr=None, end_addr=None):
    start_addr_reached = False
    cfg_str = ""

    for location, block in cfg.blocks.items():
        _a = cfg.loc_db.get_location_offset(location)
        cfg_str += '{}:\n'.format(location)

        for instr in native_block(block):
            if (not end_addr is None and
                    instr.offset == end_addr):
                return

            if (not start_addr is None and
                    instr.offset == start_addr):
                start_addr_reached = True

            if start_addr is None:
                cfg_str += '{:X} {}\n'.format(instr.offset, instr)
            else:
                if start_addr_reached:
                    cfg_str += '{:X} {}\n'.format(instr.offset, instr)

        cfg_str += '\n'

    return cfg_str


def show_effects(se, registers=None):
    for expression, value in sorted(se.symbols.symbols_id.items()):
        if (registers is not None and expression not in registers) or \
                se.ir_arch.arch.regs.regs_init.get(expression) == value:
            continue

        print(expression, '=', value)

    print('')

    for expression, value in sorted(se.symbols.symbols_mem.items()):
        expression, value = expr_simp(expression), expr_simp(value)
        if expression == value:
            continue

        print(expression, '=', value)


def contains_element_from_list(expr, lst):
    for el in lst:
        if el in expr:
            return True

    return False


def print_dict(dct, title_str=""):
    if title_str != "":
        print(title_str)

    for k, v in dct.items():
        print("{} = {}".format(k, v))
    print()


def print_list(lst, title_str=""):
    if title_str != "":
        print(title_str)

    for el in lst:
        print(el)
    print()


def dict_to_str(dct, title_str=""):
    if title_str != "":
        dct_str = title_str + "\n"

    for k, v in dct.items():
        dct_str += "{} = {}\n".format(k, v)

    dct_str += "\n"

    return dct_str


def delete_keys_from_dict(dct, keys):
    for key in keys:
        if dct.has_key(key):
            del dct[key]


def merge_dicts(dct1, dct2):
    dct_ret = dct1.copy()
    dct_ret.update(dct2)
    return dct_ret


def cast_to_exprint(expr):
    """
    Casts ExprCompose instances which do only conain
    ExprInt arguments to a single ExprInt instace.
    """
    assert isinstance(expr, Expr)

    if expr.is_int():
        return expr

    elif expr.is_compose():
        res = 0
        prev_size = 0
        size = 0
        for arg in expr.args:
            tmp = cast_to_exprint(arg)
            res = res | (tmp.arg.arg << prev_size)
            prev_size = tmp.size
            size += tmp.size
        return ExprInt(res, size)

    else:
        raise CastExprComposeExprIntException("ERROR: expr {} is" + \
                                              "not an ExprId or ExprCompose")


class CastExprComposeExprIntException(Exception):
    pass


def contains_expr_cond(expr):
    assert isinstance(expr, Expr)

    if expr.is_int():
        return False

    elif expr.is_id():
        return False

    elif expr.is_loc():
        return False

    elif expr.is_mem():
        return contains_expr_cond(expr.ptr)

    elif expr.is_op() or expr.is_compose():
        contains_cond = False
        for arg in expr.args:
            contains_cond |= contains_expr_cond(arg)
        return contains_cond

    elif expr.is_cond():
        return True

    elif expr.is_slice():
        return False

    else:
        print("ERROR in containexpr_cond:" + \
              "{} not supported".format(type(expr)))
        exit()


def contains_slice_of_expr(expr, s_expr):
    assert isinstance(expr, Expr) and \
           isinstance(s_expr, Expr)

    if s_expr.is_int():
        return False

    elif s_expr.is_id():
        return False

    elif s_expr.is_loc():
        return False

    elif s_expr.is_mem():
        return contains_slice_of_expr(expr, s_expr.ptr)

    elif s_expr.is_op() or s_expr.is_compose():
        contains_slice = False
        for arg in s_expr.args:
            contains_slice |= contains_slice_of_expr(expr, arg)

        return contains_slice

    elif s_expr.is_cond():
        contains_slice = contains_slice_of_expr(expr,
                                                s_expr.cond)
        contains_slice |= contains_slice_of_expr(expr,
                                                 s_expr.src1)
        contains_slice |= contains_slice_of_expr(expr,
                                                 s_expr.src2)

        return contains_slice

    elif s_expr.is_slice():
        if expr == s_expr.arg:
            return True

        return False

    else:
        print("ERROR in contains_slice_of_expr (helper.py):" + \
              "{} not supported".format(type(expr)))
        exit()


def transform_to_loc_key(el, loc_db):
    assert isinstance(loc_db, LocationDB)

    if isinstance(el, ExprInt):
        return loc_db.get_offset_location(el.arg.arg)
    elif isinstance(el, ExprLoc):
        return el.loc_key

    return el
