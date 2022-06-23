from miasm.ir.symbexec import *


class InOutDataFlowSe(SymbolicExecutionEngine):
    def __init__(self, ir_arch, state=None):
        super(self.__class__, self).__init__(ir_arch, state=state)
        self.r_mem = set()
        self.w_mem = set()

    def mem_read(self, expr):
        self.r_mem.add(expr)
        return super(self.__class__, self).mem_read(expr)

    def mem_write(self, dst, src):
        self.w_mem.add(dst)
        super(self.__class__, self).mem_write(dst, src)

    def reset_r_w_mem(self):
        self.r_mem = set()
        self.w_mem = set()
