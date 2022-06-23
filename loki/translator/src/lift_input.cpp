
#include <fstream>
#include <iostream>
#include <iterator>
#include <set>
#include <sstream>
#include <string>

#include <llvm/Bitcode/BitcodeWriter.h>
#include <llvm/IR/IRBuilder.h>
#include <llvm/IR/InstIterator.h>
#include <llvm/IR/LegacyPassManager.h>
#include <llvm/Transforms/IPO/PassManagerBuilder.h>
#include <llvm/Transforms/IPO.h>
#include <llvm/IR/Verifier.h>
#include <llvm/IRReader/IRReader.h>
#include <llvm/Support/FileSystem.h>
#include <llvm/Support/FormatVariadic.h>
#include <llvm/Support/SourceMgr.h>
#include <llvm/Support/TargetRegistry.h>
#include <llvm/Target/TargetMachine.h>
#include <llvm/Transforms/Scalar.h>
#include <llvm/Transforms/Utils.h>
#include <llvm/Transforms/InstCombine/InstCombine.h>
#include <llvm/IR/Module.h>

using namespace std;
using namespace llvm;

enum IlOpType {
  kIlUnknown = 0,
  kIlAdd,
  kIlSub,
  kIlOr,
  kIlAnd,
  kIlXor,
  kIlNand,
  kIlNor,
  kIlNot,
  kIlNeg, // does not exist in LLVM
  kIlAshr,
  kIlLshr,
  kIlShl,
  kIlMul,
  kIlUdiv,
  kIlSdiv,
  kIlUrem,
  kIlSrem,
  kIlUlt,
  kIlSlt,
  kIlUle,
  kIlSle,
  kIlEqual,
  kIlIte,
  kIlZeroExt,
  kIlSignExt,
  kIlTrunc,
  kIlGep,
  kIlBitcast,
  kIlLoad,
  kIlStore,
  kIlAlloc,

  kIlConst,
  kIlReg,


  kMaxIlOps,
};

const char *il_op_string[] = {
    "Unknown", "Add",   "Sub",   "Or",         "And",        "Xor",   "Nand",
    "Nor",     "Not",   "Neg",   "Ashr",       "Lshr",       "Shl",   "Mul",
    "Udiv",    "Sdiv",  "Urem",  "Srem",       "Ult",        "Slt",   "Ule",
    "Sle",     "Equal", "Ite",   "ZeroExtend", "SignExtend", "Trunc", "GEP",
    "BitCast", "Load",  "Store", "Alloca",     "Const",      "Reg"
};

const size_t il_op_str_count = sizeof(il_op_string) / sizeof(*il_op_string);
static_assert(il_op_str_count == kMaxIlOps,
              "Mapping from IL op to string out of sync.");

// If an LLVM definition has no name, we need to generate one. This map keeps
// track of new names for `Value`s.
static map<Value *, string> value_identifiers;
static unsigned value_identifier = 0;
static unsigned memory_identifier = 0;

static string generate_name() {
  return formatv("__id_{0}", value_identifier++);
}

static string generate_memory_name() {
  return formatv("__mem_{0}", memory_identifier++);
}

struct IlLinearExpr {
  IlOpType op = kIlUnknown;
  size_t size = 0;

  uint64_t imm = 0;
  string name = "";
  uint8_t a = 0, b = 0;

  string to_json() const {
    stringstream stream;
    stream << "{";
    stream << R"("size": )" << size;
    stream << ",";

    if (op > kIlUnknown && op < kIlConst) {
      stream << R"("op":")";
      stream << il_op_string[op];
      stream << "\"";
    } else {
      stream << R"("op":{)";

      switch (op) {
      case kIlConst:
        stream << R"("Const":)" << imm;
        break;

      case kIlReg:
        stream << R"("Reg":")" << name << "\"";
        break;

      default:
        llvm_unreachable("to_json: Unknown type?");
      }

      stream << "}";
    }
    stream << "}";
    return stream.str();
  }
};

struct IlAssignment {
  size_t size = 0;
  vector<IlLinearExpr> lhs;
  vector<IlLinearExpr> rhs;

  string to_json() const {
    stringstream stream;
    stream << "{";

    stream << R"("lhs":[)";
    for (auto &e : lhs) {
      stream << e.to_json();
      if (&e != &lhs.back()) {
        stream << ",";
      }
    }
    stream << "],";

    stream << R"("rhs":[)";
    for (auto &e : rhs) {
      stream << e.to_json();
      if (&e != &rhs.back()) {
        stream << ",";
      }
    }

    stream << "],";
    stream << R"("size":)" << size;

    stream << "}";
    return stream.str();
  }
};

IlLinearExpr generate_memory_reg(size_t sz) {
  IlLinearExpr result = {};

  result.op = kIlReg;
  result.size = sz;

  string name = generate_memory_name();
  result.name = name;
  return result;
}

string generate_value_name(Value &value) {
  string result;
  if (value.hasName()) {
    result = value.getName().str();
  } else {
    // TODO: Consider slot mechanism in AsmWriter.
    auto it = value_identifiers.find(&value);
    if (it != value_identifiers.end()) {
      result = it->second;
    } else {
      result = generate_name();
      value_identifiers[&value] = result;
    }
  }

  return result;
}

IlLinearExpr translate_int(Value &value, size_t value_sz = 0) {
  IlLinearExpr result = {};

  auto sz = value_sz;
  if (!sz) {
    sz = value.getType()->getPrimitiveSizeInBits();
    if (sz > 64) {
      llvm_unreachable("translate_int: Bad size?");
    }
  }

  if (auto c = dyn_cast<ConstantInt>(&value)) {
    result.op = kIlConst;
    result.size = sz;
    result.imm = c->getZExtValue();
    return result;
  }

  if (isa<Argument>(&value) || isa<Instruction>(&value) ||
      isa<Operator>(&value)) {
    result.op = kIlReg;
    result.size = sz;
    result.name = generate_value_name(value);
    return result;
  }

  llvm_unreachable("translate_int: Unknown type?");
}

/*
IlLinearExpr translate_gep(GEPOperator &gep, vector<IlAssignment> &pre,
                           Module &module) {
  llvm_unreachable("translate_gep: function is deprecated");
  auto &dl = module.getDataLayout();
  auto sz = dl.getIndexTypeSizeInBits(gep.getType());

  APInt offset(sz, 0);
  if (gep.accumulateConstantOffset(dl, offset)) {
    IlAssignment add;
    add.size = sz;

    auto *base = gep.getPointerOperand();

    IlLinearExpr expr_base;
    expr_base.op = kIlReg;
    expr_base.size = sz;
    expr_base.name = generate_value_name(*base);

    IlLinearExpr expr_offset;
    expr_offset.op = kIlConst;
    expr_offset.size = sz;
    expr_offset.imm = offset.getZExtValue();

    IlLinearExpr expr_add;
    expr_add.op = kIlAdd;
    expr_add.size = sz;

    add.rhs.push_back(expr_offset);
    add.rhs.push_back(expr_base);
    add.rhs.push_back(expr_add);

    IlLinearExpr lhs;
    lhs.op = kIlReg;
    lhs.size = sz;
    lhs.name = generate_name();

    add.lhs.push_back(lhs);
    pre.push_back(add);
    return lhs;
  }

  llvm_unreachable("translate_gep: Cannot handle GEP.");
}
*/

IlLinearExpr translate_value(Value &value, vector<IlAssignment> &pre,
                             Module *module = nullptr) {
  auto ty = value.getType();

  // if (module && isa<GEPOperator>(value)) {
  //   return translate_gep(cast<GEPOperator>(value), pre, *module);
  // } else
  if (ty->getTypeID() == Type::IntegerTyID) {
    return translate_int(value);
  } else if (ty->getTypeID() == Type::PointerTyID) {
    // TODO: Fix for sequential types (store size).
    return translate_int(value, 64);
  }

  llvm_unreachable("translate_value: Unknown type?");
}

vector<IlAssignment> translate_direct(Instruction &instr, IlOpType opcode) {
  vector<IlAssignment> result_assigns;
  IlAssignment result = {};

  IlLinearExpr lhs = translate_value(instr, result_assigns);
  result.lhs.push_back(lhs);
  result.size = instr.getType()->getPrimitiveSizeInBits();

  for (auto &op : instr.operands()) {
    IlLinearExpr e = translate_value(*op, result_assigns);
    result.rhs.push_back(e);
  }

  IlLinearExpr op = {};
  op.op = opcode;
  op.size = result.size;
  result.rhs.push_back(op);

  result_assigns.push_back(result);
  return result_assigns;
}

vector<IlAssignment> translate_add(Instruction &instr) {
  return translate_direct(instr, kIlAdd);
}

vector<IlAssignment> translate_sub(Instruction &instr) {
  return translate_direct(instr, kIlSub);
}

vector<IlAssignment> translate_or(Instruction &instr) {
  return translate_direct(instr, kIlOr);
}

vector<IlAssignment> translate_and(Instruction &instr) {
  return translate_direct(instr, kIlAnd);
}

vector<IlAssignment> translate_xor(Instruction &instr) {
  return translate_direct(instr, kIlXor);
}

vector<IlAssignment> translate_not(Instruction &instr) {
  return translate_direct(instr, kIlNot);
}

vector<IlAssignment> translate_ashr(Instruction &instr) {
  return translate_direct(instr, kIlAshr);
}

vector<IlAssignment> translate_lshr(Instruction &instr) {
  return translate_direct(instr, kIlLshr);
}

vector<IlAssignment> translate_shl(Instruction &instr) {
  return translate_direct(instr, kIlShl);
}

vector<IlAssignment> translate_mul(Instruction &instr) {
  return translate_direct(instr, kIlMul);
}

vector<IlAssignment> translate_sdiv(Instruction &instr) {
  return translate_direct(instr, kIlSdiv);
}

vector<IlAssignment> translate_udiv(Instruction &instr) {
  return translate_direct(instr, kIlUdiv);
}

vector<IlAssignment> translate_urem(Instruction &instr) {
  return translate_direct(instr, kIlUrem);
}

vector<IlAssignment> translate_srem(Instruction &instr) {
  return translate_direct(instr, kIlSrem);
}

vector<IlAssignment> translate_trunc(Instruction &instr) {
  return translate_direct(instr, kIlTrunc);
}

/* In case we cannot calculate a constant offset, we resort to dynamically calculate it */
vector<IlAssignment> translate_gep_with_dynamic_offset(Instruction &instr) {
  vector<IlAssignment> result_assigns;
  IlAssignment result = {};

  auto &dl = instr.getModule()->getDataLayout();
  assert (isa<GEPOperator>(instr) && "translate_gep_with_dynamic_offset: Instr must be GEPOperator");
  auto *gep = &cast<GEPOperator>(instr);
  auto index_sz = dl.getIndexTypeSizeInBits(gep->getType());
  auto array_sz = gep->getResultElementType()->getScalarSizeInBits();

  // Collect all operands
  vector<IlLinearExpr> ops;
  for (auto &op : gep->operands()) {
    // skip first operand which is pointer to element for which we calculate offset
    if (!op->getType()->isPointerTy()) {
      IlLinearExpr op_expr = translate_value(*op, result_assigns);
      op_expr.size = index_sz;
      ops.push_back(op_expr);
    }
  }

  // sum all operands
  IlLinearExpr prev_lhs = ops.front();
  for (int i = 1; i < ops.size(); ++i) {
    IlAssignment add;
    add.size = index_sz;

    IlLinearExpr expr_add;
    expr_add.op = kIlAdd;
    expr_add.size = index_sz;

    add.rhs.push_back(prev_lhs);
    add.rhs.push_back(ops[i]);
    add.rhs.push_back(expr_add);

    IlLinearExpr lhs;
    lhs.op = kIlReg;
    lhs.size = index_sz;
    lhs.name = generate_name();

    add.lhs.push_back(lhs);
    prev_lhs = lhs;
    result_assigns.push_back(add);
  }

  // Convert element index to offset in bytes by multiplying the element index with the underlying size
  IlAssignment mul;
  mul.size = index_sz;

  IlLinearExpr expr_mul;
  expr_mul.op = kIlMul;
  expr_mul.size = index_sz;

  IlLinearExpr size_expr;
  size_expr.op = kIlConst;
  size_expr.imm = (array_sz / 8); // size in bytes
  size_expr.size = index_sz;

  mul.rhs.push_back(prev_lhs);
  mul.rhs.push_back(size_expr);
  mul.rhs.push_back(expr_mul);

  IlLinearExpr mul_lhs_expr;
  mul_lhs_expr.op = kIlReg;
  mul_lhs_expr.size = index_sz;
  mul_lhs_expr.name = generate_name();

  mul.lhs.push_back(mul_lhs_expr);
  result_assigns.push_back(mul);


  // mul_lhs_expr contains the result of the sum multiplied by the size (i.e., offset in bytes)
  // now, build GEP with ptr operand we skipped before and sum as offset
  auto *base = gep->getPointerOperand();

  IlLinearExpr expr_base = translate_value(*base, result_assigns);
  // expr_base.op = kIlReg;
  // expr_base.size = 64; // Pointer size
  // expr_base.name = generate_value_name(*base);

  IlLinearExpr expr_offset = mul_lhs_expr;

  IlLinearExpr expr_gep;
  expr_gep.op = kIlGep;
  expr_gep.size = index_sz; // Size of accessed array -> is used in Rust code to calculate true offset

  result.rhs.push_back(expr_base);
  result.rhs.push_back(expr_offset);
  result.rhs.push_back(expr_gep);

  IlLinearExpr lhs = translate_value(instr, result_assigns);
  result.lhs.push_back(lhs);
  result.size = 64;

  result_assigns.push_back(result);
  return result_assigns;
}

vector<IlAssignment> translate_gep(Instruction &instr) {
  vector<IlAssignment> result_assigns;
  IlAssignment result = {};

  IlLinearExpr lhs = translate_value(instr, result_assigns);
  result.lhs.push_back(lhs);

  auto module = instr.getModule();
  auto &dl = module->getDataLayout();
  assert (isa<GEPOperator>(instr) && "translate_gep: Instr must be GEPOperator");
  auto *gep = &cast<GEPOperator>(instr);
  auto sz = dl.getIndexTypeSizeInBits(gep->getType());

  APInt offset(sz, 0);
  if (gep->accumulateConstantOffset(dl, offset)) {
    result.size = sz;

    auto *base = gep->getPointerOperand();

    IlLinearExpr expr_base;
    expr_base.op = kIlReg;
    expr_base.size = sz;
    expr_base.name = generate_value_name(*base);

    IlLinearExpr expr_offset;
    expr_offset.op = kIlConst;
    expr_offset.size = sz;
    expr_offset.imm = offset.getZExtValue();

    IlLinearExpr expr_gep;
    expr_gep.op = kIlGep;
    expr_gep.size = sz;

    result.rhs.push_back(expr_base);
    result.rhs.push_back(expr_offset);
    result.rhs.push_back(expr_gep);

    result_assigns.push_back(result);
    return result_assigns;
  }

  // cerr << "Could not translate gep - using translate_gep_with_dynamic_offset!" << endl;
  return translate_gep_with_dynamic_offset(instr);
}

vector<IlAssignment> translate_bitcast(Instruction &instr) {
  vector<IlAssignment> result_assigns;
  IlAssignment result = {};

  auto dest_size = 0;
  if (BitCastInst *bc = dyn_cast<BitCastInst>(&instr)) {
    auto dest_ty = bc->getDestTy();
    if (dest_ty->isPointerTy()) {
      dest_size = 64; // dest_ty->getPointerElementType()->getScalarSizeInBits();
    } else if (dest_ty->isIntegerTy()) {
      dest_size = dest_ty->getScalarSizeInBits();
    } else {
      llvm_unreachable("translate_bitcast: Bitcast destination type is neither pointer nor int type");
    }
    IlLinearExpr operand = translate_value(*(bc->getOperand(0)), result_assigns);
    if (bc->getOperand(0)->getType()->isPointerTy()) {
      operand.size = 64; // ptr must have size 64
    }
    result.rhs.push_back(operand);
    /*
    auto src_ty = bc->getSrcTy();
    if (src_ty->isPointerTy()) {
      src_size = 64; // src_ty->getPointerElementType()->getScalarSizeInBits();
    } else if (src_ty->isIntegerTy())  {
      src_size = src_ty->getScalarSizeInBits();
    } else {
      llvm_unreachable("translate_bitcast: Bitcast source type is neither pointer nor int type");
    }
    */
  } else {
    llvm_unreachable("translate_bitcast: Instruction is not a bitcast");
  }

  IlLinearExpr lhs = translate_value(instr, result_assigns);
  lhs.size = dest_size;

  result.lhs.push_back(lhs);
  result.size = lhs.size;
  /*
  for (auto &op : instr.operands()) {
    IlLinearExpr e = translate_value(*op, result_assigns);
    e.size = src_size;
    result.rhs.push_back(e);
  }
  */

  IlLinearExpr op = {};
  op.op = kIlBitcast;
  op.size = dest_size;

  result.rhs.push_back(op);

  result_assigns.push_back(result);
  return result_assigns;
}

vector<IlAssignment> translate_ptrtoint(Instruction &instr) {
  vector<IlAssignment> result_assigns;
  IlAssignment result = {};

  assert (isa<PtrToIntOperator>(instr) && "translate_ptrtoint: Instr must be PtrToIntOperator");
  auto *ptrtoint = &cast<PtrToIntOperator>(instr);

  IlLinearExpr lhs = translate_value(instr, result_assigns);
  result.lhs.push_back(lhs);
  result.size = lhs.size;

  auto *base = ptrtoint->getPointerOperand();

  IlLinearExpr expr_base;
  expr_base.op = kIlReg;
  expr_base.size = 64; // Pointer size
  expr_base.name = generate_value_name(*base);

  IlLinearExpr expr_op;
  expr_op.op = kIlTrunc;
  expr_op.size = lhs.size;

  result.rhs.push_back(expr_base);
  result.rhs.push_back(expr_op);

  result_assigns.push_back(result);
  return result_assigns;
}

vector<IlAssignment> translate_inttoptr(Instruction &instr) {
  vector<IlAssignment> result_assigns;
  IlAssignment result = {};

  IlLinearExpr lhs = translate_value(instr, result_assigns);
  result.lhs.push_back(lhs);
  result.size = 64; // Pointer size

  auto int_operand = instr.operands().begin()->get();

  IlLinearExpr expr_base = translate_value(*int_operand, result_assigns);

  IlLinearExpr expr_op;
  expr_op.op = kIlZeroExt;
  expr_op.size = lhs.size;

  result.rhs.push_back(expr_base);
  result.rhs.push_back(expr_op);

  result_assigns.push_back(result);
  return result_assigns;
}

void il_append_not(vector<IlAssignment> &assignments) {
  IlAssignment &last = assignments.back();

  // TODO: Update this once memory model is fixed (likely not inline anymore).
  assert(last.lhs.size() == 1 && "No support for memory yet.");
  auto &interm_cmp = last.lhs[0];

  IlLinearExpr expr_not;
  expr_not.op = kIlNot;
  expr_not.size = last.size;

  IlAssignment assignment;
  assignment.size = last.size;

  assignment.rhs.push_back(interm_cmp);
  assignment.rhs.push_back(expr_not);

  IlLinearExpr lhs_not;
  lhs_not.op = kIlReg;
  lhs_not.size = last.size;

  /* In case we need to append IL semantics to LLVM instructions (i.e., no 1:1
   * translation is possible), we might need to rename TIL instructions. In this
   * case, we push the LLVM name as far down the chain as possible such that it
   * still reflects the original semantics. This requires us to choose
   * new names for intermediate computations and replace them accordingly.
   */

  // The original LLVM name should be the one after NOTing.
  lhs_not.name = last.lhs[0].name;
  interm_cmp.name = generate_name();

  // Replace former uses of the original LLVM name in our computation with the
  // new name. In our case, looking at our RHS is sufficient.
  for (auto &rhs : assignment.rhs) {
    if (rhs.name == lhs_not.name) {
      rhs.name = interm_cmp.name;
    }
  }

  assignment.lhs.push_back(lhs_not);
  assignments.push_back(assignment);
}

vector<IlAssignment> translate_negated_cmp(Instruction &instr,
                                           IlOpType opcode) {
  auto assignments = translate_direct(instr, opcode);
  il_append_not(assignments);
  return assignments;
}

vector<IlAssignment> translate_icmp(Instruction &instr) {
  auto *cmp = dyn_cast<ICmpInst>(&instr);
  assert(cmp);

  switch (cmp->getPredicate()) {
  case ICmpInst::ICMP_EQ:
    return translate_direct(instr, kIlEqual);
  case ICmpInst::ICMP_NE:
    return translate_negated_cmp(instr, kIlEqual);
  case ICmpInst::ICMP_ULE:
    return translate_direct(instr, kIlUle);
  case ICmpInst::ICMP_UGT:
    return translate_negated_cmp(instr, kIlUle);
  case ICmpInst::ICMP_ULT:
    return translate_direct(instr, kIlUlt);
  case ICmpInst::ICMP_UGE:
    return translate_negated_cmp(instr, kIlUlt);
  case ICmpInst::ICMP_SLE:
    return translate_direct(instr, kIlSle);
  case ICmpInst::ICMP_SGT:
    return translate_negated_cmp(instr, kIlSle);
  case ICmpInst::ICMP_SLT:
    return translate_direct(instr, kIlSlt);
  case ICmpInst::ICMP_SGE:
    return translate_negated_cmp(instr, kIlSlt);

  default:
    llvm_unreachable("translate_icmp: Unknown ICmpInst predicate");
  }
}

vector<IlAssignment> translate_select(Instruction &instr) {
  return translate_direct(instr, kIlIte);
}

vector<IlAssignment> translate_zext(Instruction &instr) {
  return translate_direct(instr, kIlZeroExt);
}

vector<IlAssignment> translate_sext(Instruction &instr) {
  return translate_direct(instr, kIlSignExt);
}

vector<IlAssignment> translate_load(Instruction &instr) {
  return translate_direct(instr, kIlLoad);
}

vector<IlAssignment> translate_alloc(Instruction &instr) {
  vector<IlAssignment> result_assigns;
  IlAssignment result = {};

  IlLinearExpr lhs = translate_value(instr, result_assigns);
  lhs.size = 64;

  result.lhs.push_back(lhs);
  result.size = 64;

  size_t sz;
  auto t = instr.getType()->getPointerElementType();

  if (auto seq = dyn_cast<SequentialType>(t)) {
    sz = seq->getNumElements() * seq->getElementType()->getScalarSizeInBits();
  } else if (auto struc = dyn_cast<StructType>(t)) {
    // TODO: Maybe check for struct alignment?
    sz = 0;
    for (auto element : struc->elements()) {
      sz += element->getScalarSizeInBits();
    }
  } else {
    sz = t->getScalarSizeInBits();
  }

  IlLinearExpr il_size = {};
  il_size.op = kIlConst;
  il_size.size = 64;
  il_size.imm = sz;

  IlLinearExpr op = {};
  op.op = kIlAlloc;
  op.size = 64; // Pointer size.

  result.rhs.push_back(il_size);
  result.rhs.push_back(op);

  result_assigns.push_back(result);
  return result_assigns;
}

vector<IlAssignment> translate_store(Instruction &instr) {
  vector<IlAssignment> result_assigns;
  IlAssignment result = {};

  auto sz = (*instr.operands().begin())->getType()->getPrimitiveSizeInBits();
  IlLinearExpr lhs = generate_memory_reg(sz);

  result.lhs.push_back(lhs);
  result.size = sz;

  for (auto i = instr.operands().end() - 1, e = instr.operands().begin();;
       --i) {
    IlLinearExpr expr = translate_value(**i, result_assigns, instr.getModule());
    result.rhs.push_back(expr);

    if (i == e) {
      break;
    }
  }

  IlLinearExpr op = {};
  op.op = kIlStore;
  op.size = result.size;
  result.rhs.push_back(op);

  result_assigns.push_back(result);
  return result_assigns;
}

using IlTranslator = vector<IlAssignment> (*)(Instruction &);

static map<unsigned, IlTranslator> translators{
    {Instruction::Add, translate_add},
    {Instruction::Sub, translate_sub},
    {Instruction::Mul, translate_mul},
    {Instruction::Or, translate_or},
    {Instruction::And, translate_and},
    {Instruction::Xor, translate_xor},
    {Instruction::Shl, translate_shl},
    {Instruction::AShr, translate_ashr},
    {Instruction::LShr, translate_lshr},
    {Instruction::UDiv, translate_udiv},
    {Instruction::SDiv, translate_sdiv},
    {Instruction::URem, translate_urem},
    {Instruction::SRem, translate_srem},
    {Instruction::ICmp, translate_icmp},
    {Instruction::Select, translate_select},
    {Instruction::ZExt, translate_zext},
    {Instruction::SExt, translate_sext},
    {Instruction::Trunc, translate_trunc},
    {Instruction::Load, translate_load},
    {Instruction::Store, translate_store},
    {Instruction::Alloca, translate_alloc},
    {Instruction::GetElementPtr, translate_gep},
    {Instruction::BitCast, translate_bitcast},
    {Instruction::PtrToInt, translate_ptrtoint},
    {Instruction::IntToPtr, translate_inttoptr}};

vector<IlAssignment> translate(Instruction &instr) {
  auto it = translators.find(instr.getOpcode());
  if (it == translators.cend()) {
    // DEBUG: Ignore unknown instructions for now.
    errs() << "Could not translate an instruction:";
    instr.print(errs(), true);
    errs() << "\n";
    return {};

    // errs() << "Unknown opcode " << instr.getOpcode() << ".\n";
    // llvm_unreachable("translate: Unknown opcode.");
  }

  return it->second(instr);
}

bool lift(Function &f, const string& out_dir) {
  vector<IlAssignment> all_assignments;

  for (auto &instr : instructions(f)) {
    auto assignments = translate(instr);

    all_assignments.reserve(all_assignments.size() + assignments.size());
    all_assignments.insert(all_assignments.end(), assignments.begin(),
                           assignments.end());
  }

  ofstream outfilestream;
  outfilestream.open(out_dir + "/lifted_input.txt");
  outfilestream << "{\n";

  // Print instructions.
  outfilestream << "\"instructions\": [\n";
  for (auto i = all_assignments.begin(), e = all_assignments.end(); i != e;
       ++i) {
    outfilestream << i->to_json();
    if (i != (e - 1)) {
      outfilestream << ",\n";
    } else {
      outfilestream << "\n";
    }
  }
  outfilestream << "],\n";

  // Print arguments.
  outfilestream << "\"arguments\": [\n";

  for (auto i = f.arg_begin(), e = f.arg_end(); i != e; ++i) {
    // Arguments not used by the function may have no name nor value_identifier assigned
    generate_value_name(*i);

    outfilestream << "\"";
    if (i->hasName()) {
      outfilestream << i->getName().str();
    } else {
      outfilestream << value_identifiers[i];
    }

    outfilestream << "\"";
    if (i != (e - 1)) {
      outfilestream << ",\n";
    } else {
      outfilestream << "\n";
    }
  }

  outfilestream << "\n]\n";
  outfilestream << "}\n";

  return true;
}

bool parse_module(const string& workdir) {
  LLVMContext context;
  SMDiagnostic error;
  error_code EC;

  auto module = parseIRFile(workdir + "/input_program.bc", error, context);
  if (!module) {
    return false;
  }

  auto target_function = module->getFunction("target_function");
  if (!target_function) {
    return false;
  }

  legacy::PassManager pm;
  // explicit constructor param -> use get to retrieve ptr
  legacy::FunctionPassManager fpm(module.get());

  // Initialize Builder:
  PassManagerBuilder builder;
  builder.OptLevel = 3;
  builder.SizeLevel = 0;
  builder.Inliner = llvm::createFunctionInliningPass(3, 0, false);
  builder.DisableUnrollLoops = false;
  builder.LoopVectorize = false;
  builder.SLPVectorize = false;

  builder.populateFunctionPassManager(fpm);

  // execute the O3 optimizations:
  // - has to be done _before_ additional passes are executed
  fpm.doInitialization();
  fpm.run(*target_function);
  fpm.doFinalization();

  // add the custom additional loop and memory optimizations:
  // -mem2reg -loop-rotate -loop-unroll -unroll-threshold=0xFFFFFFFF
  // -simplifycfg -mem2reg -sroa
  // --> threshold -> 0xFFFFFFF -> GEP will cause problems otherwise

  // 1. Mem2reg pass (total 2)
  auto *mem2reg_pass_1 = createPromoteMemoryToRegisterPass();
  // 2. Mem2reg pass (total 2)
  auto *mem2reg_pass_2 = createPromoteMemoryToRegisterPass();
  auto *lp_rot_pass = createLoopRotatePass();
  auto *lp_unroll_pass = createLoopUnrollPass(
                           /*Optlevel = */ 3,
                           /*OnlyWhenForced = */ false,
                           /*Threshold = */ 0xFFFFFFF); 
  auto *simplify_cfg_pass_1 = createCFGSimplificationPass(); 
  auto *simplify_cfg_pass_2 = createCFGSimplificationPass(); 
  auto *sroa_pass_1 = createSROAPass();
  auto *gep_pass = createSeparateConstOffsetFromGEPPass(/* LowerGEP = */ true);
  auto *constprop_pass = createConstantPropagationPass();
  auto *gvn_pass = createNewGVNPass();
  auto *instcombine_pass = createInstructionCombiningPass();

  fpm.add(mem2reg_pass_1);
  fpm.add(lp_rot_pass);
  fpm.add(lp_unroll_pass);
  fpm.add(simplify_cfg_pass_1);

  fpm.doInitialization();
  fpm.run(*target_function);
  fpm.doFinalization();

  fpm.add(mem2reg_pass_2);
  fpm.add(sroa_pass_1);
  fpm.add(simplify_cfg_pass_2);
  fpm.add(constprop_pass);

  fpm.doInitialization();
  fpm.run(*target_function);
  fpm.doFinalization();

  // eliminate malloc/free of known size arrays
  fpm.add(gvn_pass);
  fpm.add(instcombine_pass);
  fpm.add(gep_pass);

  fpm.doInitialization();
  fpm.run(*target_function);
  fpm.doFinalization();

  // Execute O3 Optimizations again:
  builder.populateFunctionPassManager(fpm);

  // - has to be done _before_ additional passes are executed
  fpm.doInitialization();
  fpm.run(*target_function);
  fpm.doFinalization();

  // dump this to file:
  raw_fd_ostream OS(workdir + "/input_program_opt.bc", EC, llvm::sys::fs::F_None);
  WriteBitcodeToFile(*module, OS);
  OS.flush();

  if (!lift(*target_function, workdir)) {
    return false;
  }

  return true;
}

int main(int argc, char *argv[]) {
  if (argc < 2) {
    errs() << "Usage: ./lift_input < Path to src >\n";
    return -1;
  }
  if (!parse_module(string(argv[1]))) {
    errs() << "Something went wrong.\n";
    return -1;
  }

  errs() << "Done.\n";
  return 0;
}
