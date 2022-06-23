
#include <fstream>
#include <iostream>
#include <set>
#include <sstream>
#include <string>
#include <vector>

#include <llvm/ADT/SetVector.h>
#include <llvm/Bitcode/BitcodeWriter.h>
#include <llvm/IR/IRBuilder.h>
#include <llvm/IR/LegacyPassManager.h>
#include <llvm/IR/Verifier.h>
#include <llvm/IRReader/IRReader.h>
#include <llvm/Support/FileSystem.h>
#include <llvm/Support/SourceMgr.h>
#include <llvm/Support/TargetRegistry.h>
#include <llvm/Target/TargetMachine.h>

using namespace std;
using namespace llvm;

constexpr bool kDebugReplaceHandler = true;
constexpr uint16_t kNumALUFiles = 511;
constexpr size_t kOffsetIp = 1;
static string workdir;

using RegMap = map<string, Value *>;

using CbUnary = decltype(&IRBuilder<>::CreateNot);
using CbBinaryA = decltype(&IRBuilder<>::CreateAdd);
using CbBinaryL = decltype(&IRBuilder<>::CreateURem);
using CbTernary = decltype(&IRBuilder<>::CreateSelect);

using CbMapUnary = map<string, CbUnary>;
using CbMapBinaryA = map<string, CbBinaryA>;
using CbMapBinaryL = map<string, CbBinaryL>;
using CbMapTernary = map<string, CbTernary>;

std::set<string> OP_UNARY = {"NOT", "NEG", "ZEXT", "SEXT"};
std::set<string> OP_BINARY = {"ADD",  "SUB",    "UREM", "SREM", "AND",
                              "OR",   "ICMPEQ", "SHL",  "XOR",  "LSHR",
                              "ASHR", "MUL",    "UDIV", "SDIV", "UREM",
                              "SREM", "ULT",    "SLT",  "ULE",  "SLE"};
std::set<string> OP_TERNARY = {"ITE"};

Value *parse_operand(RegMap &reg_map, stringstream &token_stream) {
  string result;

  token_stream >> result;
  token_stream >> result;
  token_stream >> result;
  return reg_map[result];
}

Value *emit_alu(IRBuilder<> &builder, RegMap &reg_map, const string &path_alu) {
  ifstream alu(path_alu);
  if (!alu.is_open()) {
    errs() << "Cannot find ALU file: " << path_alu << "\n";
    return nullptr;
  }

  LLVMContext &context = builder.getContext();

  CbMapBinaryL handle_2_l;
  handle_2_l["UREM"] = &IRBuilder<>::CreateURem;
  handle_2_l["SREM"] = &IRBuilder<>::CreateSRem;
  handle_2_l["AND"] = &IRBuilder<>::CreateAnd;
  handle_2_l["OR"] = &IRBuilder<>::CreateOr;
  handle_2_l["XOR"] = &IRBuilder<>::CreateXor;

  CbMapBinaryA handle_2_a;
  handle_2_a["ADD"] = &IRBuilder<>::CreateAdd;
  handle_2_a["SUB"] = &IRBuilder<>::CreateSub;
  handle_2_a["SHL"] = &IRBuilder<>::CreateShl;
  handle_2_a["MUL"] = &IRBuilder<>::CreateMul;

  CbMapTernary handle_3;

  string line, token;
  string target, op, size;

  unsigned i = 0;

  Value *last = nullptr;
  while (getline(alu, line)) {
    if (line.find_first_not_of(' ') == string::npos) {
      break;
    }

    stringstream token_stream(line);
    token_stream >> target;
    token_stream >> token; // ignore
    token_stream >> op;
    token_stream >> size;

    auto target_size_ty = IntegerType::get(context, stoi(size.c_str()));

    if (op == "REG") {
      token_stream >> token;
      auto it = reg_map.find(token);
      if (it == reg_map.end()) {
        errs() << "Unknown register " << token << ".\n";
        return nullptr;
      }

      reg_map[target] = it->second;
      continue;
    } else if (op == "INT") {
      token_stream >> token;
      reg_map[target] = builder.getInt(APInt(stoi(size), token.substr(2), 16));
      continue;
    }

    if (OP_UNARY.find(op) != OP_UNARY.cend()) {
      Value *p = parse_operand(reg_map, token_stream);

      if (op == "NOT") {
        last = builder.CreateNot(p, target);
      } else if (op == "NEG") {
        last = builder.CreateNeg(p, target);
      } else if (op == "ZEXT") {
        last = builder.CreateZExt(p, target_size_ty);
      } else if (op == "SEXT") {
        last = builder.CreateSExt(p, target_size_ty);
      }

      reg_map[target] = last;
    } else if (OP_BINARY.find(op) != OP_BINARY.cend()) {
      Value *l = parse_operand(reg_map, token_stream);
      Value *r = parse_operand(reg_map, token_stream);

      auto it_l = handle_2_l.find(op);
      if (it_l != handle_2_l.end()) {
        auto cb = it_l->second;
        last = (builder.*cb)(l, r, target);

        reg_map[target] = last;
        continue;
      }

      auto it_a = handle_2_a.find(op);
      if (it_a != handle_2_a.end()) {
        auto cb = it_a->second;
        last = (builder.*cb)(l, r, target, false, false);

        reg_map[target] = last;
        continue;
      }

      if (op == "LSHR") {
        last = builder.CreateLShr(l, r);
      } else if (op == "ASHR") {
        last = builder.CreateAShr(l, r);
      } else if (op == "UDIV") {
        last = builder.CreateUDiv(l, r);
      } else if (op == "SDIV") {
        last = builder.CreateSDiv(l, r);
      } else if (op == "ULT") {
        last = builder.CreateICmpULT(l, r);
        last = builder.CreateZExt(last, target_size_ty);
      } else if (op == "SLT") {
        last = builder.CreateICmpSLT(l, r);
        last = builder.CreateZExt(last, target_size_ty);
      } else if (op == "ULE") {
        last = builder.CreateICmpULE(l, r);
        last = builder.CreateZExt(last, target_size_ty);
      } else if (op == "SLE") {
        last = builder.CreateICmpSLE(l, r);
        last = builder.CreateZExt(last, target_size_ty);
      } else if (op == "ICMPEQ") {
        last = builder.CreateICmpEQ(l, r);
        last = builder.CreateZExt(last, target_size_ty);
      } else {
        errs() << "Unknown binary instruction " << op << "\n";
        return nullptr;
      }

      reg_map[target] = last;
    } else if (OP_TERNARY.find(op) != OP_TERNARY.cend()) {
      Value *c = parse_operand(reg_map, token_stream);
      Value *l = parse_operand(reg_map, token_stream);
      Value *r = parse_operand(reg_map, token_stream);

      auto it = handle_3.find(op);
      if (it != handle_3.cend()) {
        auto cb = it->second;
        last = (builder.*cb)(c, l, r, target, nullptr);

        reg_map[target] = last;
        continue;
      }

      if (op == "ITE") {
        last = builder.CreateICmpNE(c, builder.getInt64(0));
        last = builder.CreateSelect(last, l, r);
      }

      reg_map[target] = last;
    } else {
      errs() << "Unknown instruction " << op << ".\n";
      return nullptr;
    }
  }

  return last;
}

struct Entities {
  GlobalValue *context = nullptr;
  GlobalValue *handlers = nullptr;
  GlobalValue *bytecode = nullptr;

  Value *ip = nullptr;
};

Value *get_pointer(IRBuilder<> &builder, GlobalValue *value, Value *index) {
  return builder.CreateInBoundsGEP(value->getValueType(), value,
                                   {builder.getInt32(0), index});
}

Value *get_pointer_vip(IRBuilder<> &builder, const Entities &ent) {
  return builder.CreateInBoundsGEP(
      ent.context->getValueType(), ent.context,
      {builder.getInt32(0), builder.getInt32(0), builder.getInt32(kOffsetIp)});
}

Value *get_pointer_register(IRBuilder<> builder, const Entities &ent,
                            Value *ip) {
  auto ptr_i16_ty =
      PointerType::get(builder.getInt16Ty(), ent.context->getAddressSpace());
  Value *v = builder.CreateInBoundsGEP(ent.bytecode->getValueType(),
                                       ent.bytecode, {builder.getInt64(0), ip});
  v = builder.CreateBitCast(v, ptr_i16_ty);

  v = builder.CreateLoad(v);
  v = builder.CreateZExt(v, builder.getInt32Ty());
  v = builder.CreateInBoundsGEP(ent.context->getValueType(), ent.context,
                                {builder.getInt32(0), builder.getInt32(0), v});

  return v;
}

void build_dispatcher(IRBuilder<> &builder, Entities &ent) {
  Value *ptr_ip = get_pointer_vip(builder, ent);

  Value *opc = get_pointer(builder, ent.bytecode, ent.ip);
  auto ptr_i16_ty =
      PointerType::get(builder.getInt16Ty(), ent.context->getAddressSpace());
  opc = builder.CreateBitCast(opc, ptr_i16_ty);
  opc = builder.CreateLoad(opc);

  Value *entry = get_pointer(builder, ent.handlers, opc);
  entry = builder.CreateLoad(entry);

  ent.ip = builder.CreateAdd(ent.ip, builder.getInt64(2));
  builder.CreateStore(ent.ip, ptr_ip);

  CallInst *call = builder.CreateCall(entry, {ent.context});
  call->setTailCall(true);

  builder.CreateRetVoid();
}

using CallbackEncodingRRR =
    std::function<void(IRBuilder<> &, Entities &, Value *, Value *, Value *,
                       Value *, Value *, uint16_t)>;

void build_encoding_rrr(IRBuilder<> &builder, Entities &ent,
                        const CallbackEncodingRRR &cb_semantics,
                        uint16_t index) {
  LLVMContext &context = builder.getContext();
  auto ptr_i64_ty =
      PointerType::get(builder.getInt64Ty(), ent.context->getAddressSpace());

  ent.ip = get_pointer_vip(builder, ent);
  ent.ip = builder.CreateLoad(ent.ip);

  Value *reg_0 = get_pointer_register(builder, ent, ent.ip);
  ent.ip = builder.CreateAdd(ent.ip, builder.getInt64(2));

  Value *reg_1 = get_pointer_register(builder, ent, ent.ip);
  ent.ip = builder.CreateAdd(ent.ip, builder.getInt64(2));

  Value *reg_2 = get_pointer_register(builder, ent, ent.ip);
  ent.ip = builder.CreateAdd(ent.ip, builder.getInt64(2));

  Value *imm64 = get_pointer(builder, ent.bytecode, ent.ip);
  imm64 = builder.CreateBitCast(imm64, ptr_i64_ty);
  imm64 = builder.CreateLoad(imm64);

  ent.ip = builder.CreateAdd(ent.ip, builder.getInt64(8));

  Value *key = get_pointer(builder, ent.bytecode, ent.ip);
  key = builder.CreateBitCast(key, ptr_i64_ty);
  key = builder.CreateLoad(key);

  ent.ip = builder.CreateAdd(ent.ip, builder.getInt64(8));

  cb_semantics(builder, ent, reg_0, reg_1, reg_2, imm64, key, index);
  build_dispatcher(builder, ent);
}

using CallbackCodeGen = std::function<void(IRBuilder<> &, Entities &)>;

bool replace_handler(Module &module, Entities &ent, StringRef name,
                     const CallbackCodeGen &cb) {
  auto new_name = name.str() + "_generated";

  auto address_space = ent.context->getAddressSpace();
  FunctionCallee callee = module.getOrInsertFunction(
      new_name, Type::getVoidTy(module.getContext()),
      PointerType::get(ent.context->getValueType(), address_space));

  auto *function = dyn_cast<Function>(callee.getCallee());
  if (!function) {
    return false;
  }

  auto *block = BasicBlock::Create(module.getContext(), "entry", function);
  IRBuilder<> builder(block);

  ent.ip = nullptr;
  cb(builder, ent);

  Function *original_function = module.getFunction(name);
  if (!original_function) {
    return false;
  }

  original_function->replaceAllUsesWith(function);
  return true;
}

void add_from_alu(IRBuilder<> &builder, Entities &ent, Value *pReg_0,
                  Value *pReg_1, Value *pReg_2, Value *imm64, Value *key64,
                  uint16_t index) {
  Value *reg_1 = builder.CreateLoad(pReg_1, "reg_1");
  Value *reg_2 = builder.CreateLoad(pReg_2, "reg_2");

  RegMap reg_map;
  reg_map["x"] = reg_1;
  reg_map["y"] = reg_2;
  reg_map["c"] = imm64;
  reg_map["k"] = key64;

  Value *res =
      emit_alu(builder, reg_map,
               workdir + "/alus/alu" + to_string(index) + ".txt");
  assert(res && "ALU parsing failed.");

  builder.CreateStore(res, pReg_0);
}

vector<unsigned char> parse_bytecode(const string path_bytecode) {
  ifstream bc(path_bytecode, ios::binary);
  if (!bc.is_open()) {
    return {};
  }

  vector<unsigned char> buffer(istreambuf_iterator<char>(bc), {});
  return buffer;
}

using BcArguments = vector<uint32_t>;

BcArguments parse_arguments(const string path_arguments) {
  ifstream args(path_arguments);
  if (!args.is_open()) {
    return {};
  }

  uint32_t index;
  string line, name, index_str;

  vector<uint32_t> arg_vec;
  while (getline(args, line)) {
    stringstream stream(line);
    stream >> name >> index_str;

    index = stoi(index_str, /* idx = */ nullptr, /* base = */ 16);
    arg_vec.push_back(index);
  }

  return arg_vec;
}

bool replace_initializer(GlobalVariable &gv,
                         ArrayRef<Constant *> new_elements) {
  auto *type = gv.getInitializer()->getType()->getArrayElementType();

  auto *new_initializer = ConstantArray::get(
      ArrayType::get(type, new_elements.size()), new_elements);
  if (!new_initializer) {
    return false;
  }

  auto *new_argument_indices =
      new GlobalVariable(*gv.getParent(), new_initializer->getType(),
                         gv.isConstant(), gv.getLinkage(), new_initializer);

  new_argument_indices->takeName(&gv);
  new_argument_indices->copyAttributesFrom(&gv);

  // LLVM can only replace values of the same type. We cheat here a bit
  // and explicitly cast the global variable to the proper type. This is
  // required as arrays have their length encoded within the type itself --
  // replacing a 3-element array, e.g., [3 x i32], with a 4-element one
  // ([4 x i32]) changes the type of both the GV and its initializer list.
  //
  // We add a bit cast here to make LLVM believe it is replacing the old GV
  // with an appropriate type. The cast itself is removed in the process and
  // all uses transition to the correct new type instead.
  //
  // See
  // https://opensource.apple.com/source/clang/clang-163.7.1/src/tools/clang/lib/CodeGen/CGDecl.cpp.
  Constant *type_cast =
      ConstantExpr::getBitCast(new_argument_indices, gv.getType());

  gv.replaceAllUsesWith(type_cast);
  gv.eraseFromParent();

  return true;
}

bool parse_module(const string& template_bitcode, const string& workdir) {
  LLVMContext context;
  SMDiagnostic error;

  vector<unsigned char> bc =
      // parse_bytecode("../../synthesis/vm_alu/byte_code.bin");
      parse_bytecode(workdir + "/byte_code.bin");
  if (bc.empty()) {
    errs() << "Could not parse input bytecode.\n";
    return false;
  }

  BcArguments arguments =
      parse_arguments(workdir + "/variable_map.txt");
  if (arguments.empty()) {
    errs() << "Could not parse bytecode arguments.\n";
    return false;
  }

  // TODO: does each workdir need its own template.bc<w?
  auto module = parseIRFile(template_bitcode, error, context);
  if (!module) {
    errs() << "Could not parse template bitcode.\n";
    error.print("generate_vm", errs());
    return false;
  }

  GlobalVariable *argument_indices =
      module->getGlobalVariable("argument_indices");
  auto *element_type =
      argument_indices->getInitializer()->getType()->getArrayElementType();

  SmallVector<Constant *, 16> vec_indices;
  for (auto &kv : arguments) {
    vec_indices.emplace_back(
        ConstantInt::get(element_type, kv, /* isSigned = */ false));
  }

  if (!replace_initializer(*argument_indices, vec_indices)) {
    errs() << "Could not inject argument indices.\n";
    return false;
  }

  GlobalVariable *argument_count = module->getGlobalVariable("argument_count");
  Constant *new_argument_count = ConstantInt::get(
      argument_count->getInitializer()->getType(), vec_indices.size(), false);
  for (Use &use : argument_count->uses()) {
    if (auto *user = cast<Instruction>(use.getUser())) {
      user->replaceAllUsesWith(new_argument_count);
    }
  }

  GlobalVariable *bc_global = module->getGlobalVariable("bytecode");
  element_type = bc_global->getInitializer()->getType()->getArrayElementType();

  std::vector<Constant *> bc_constants;
  for (auto &x : bc) {
    bc_constants.emplace_back(
        ConstantInt::get(element_type, x, /* isSigned = */ false));
  }

  ArrayRef<Constant *> meh(bc_constants);
  if (!replace_initializer(*bc_global, meh)) {
    errs() << "Could not inject bytecode.\n";
    return false;
  }

  Entities ent;

  ent.context = module->getGlobalVariable("context");
  if (!ent.context) {
    errs() << "Could not obtain global context.\n";
    return false;
  }

  ent.handlers = module->getGlobalVariable("handler_table");
  if (!ent.handlers) {
    errs() << "Could not obtain global handler table.\n";
    return false;
  }

  ent.bytecode = module->getGlobalVariable("bytecode");
  if (!ent.bytecode) {
    errs() << "Could not obtain global bytecode array.\n";
    return false;
  }

  if (kDebugReplaceHandler) {
    /* index = 0 is vm_exit, index = 1 is for memory operatoins */
    for (uint16_t index = 2; index <= kNumALUFiles; index++) {
      replace_handler(*module, ent, "vm_alu" + to_string(index) + "_rrr",
                      [index](IRBuilder<> &builder, Entities &ent) {
                        build_encoding_rrr(builder, ent, add_from_alu, index);
                      });
    }

    // replace_handler(
    //     *module, ent, "vm_add_rrr", [](IRBuilder<> &builder, Entities &ent) {
    //       auto semantics_add_rrr = [](IRBuilder<> &builder, Entities &ent,
    //                                   Value *reg_dst, Value *reg_1,
    //                                   Value *reg_2, Value *key64) {
    //         Value *r_1 = builder.CreateLoad(reg_1, "reg_1");
    //         Value *r_2 = builder.CreateLoad(reg_2, "reg_2");
    //         Value *res = builder.CreateAdd(r_1, r_2, "result");
    //         builder.CreateStore(res, reg_dst);
    //       };

    //       build_encoding_rrr(builder, ent, semantics_add_rrr);
    //     });
  }

  if (verifyModule(*module, &errs())) {
    printf("Module verifcation failed\n");
    return false;
  }

  error_code ec;
  llvm::raw_fd_ostream stream(workdir + "/obf.bc", ec, sys::fs::F_None);

  WriteBitcodeToFile(*module, stream);
  stream.flush();

  return true;
}

int main(int argc, char *argv[]) {
  if (argc < 3) {
    errs() << "Expected path to template_bitcode and workdir\n";
    return -1;
  }
  workdir = string(argv[2]);
  if (!parse_module(string(argv[1]), string(argv[2]))) {
    errs() << "Something went wrong.\n";
    return -1;
  }

  return 0;
}
