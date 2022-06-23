from miasm.arch.x86.ira import ir_a_x86_32


class BaseArchitecture(ir_a_x86_32):
    def call_effects(self, addr, instr):
        new_sp = ExprOp("+", self.sp, ExprOp("-", ExprInt(0x4, 32)))
        next_label = self.get_next_loc_key(instr)

        """
        TODO: only apply the following LoCs if call target
        is next instr.
        """
        block1 = AssignBlock([
            ExprAssign(self.sp, new_sp),
            ExprAssign(ExprMem(new_sp, 32), ExprLoc(next_label, 32))
        ], instr)
        # block2 = AssignBlock([ExprAssign(self.IRDst, addr)])
        return [block1], []


class SsaArchitecture(BaseArchitecture):
    def get_out_regs(self, ir_block):
        registers = super(self.__class__, self).get_out_regs(ir_block)

        # Translate the out registers (non-SSA) provided by the base class to
        # their latest SSA version.
        collect = {}
        for assignment in ir_block:
            for dst in assignment:
                reg = self.ssa_var.get(dst, None)
                if reg in registers:
                    collect[reg] = dst

        registers = set(collect.values())
        return registers
