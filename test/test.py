import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.result import TestFailure

# ALU operation mapping for readability
ALU_OPS = {
    0b0000: "ADD",
    0b0001: "SUB",
    0b0010: "MUL",
    0b0011: "DIV",
    0b0100: "SHL",
    0b0101: "SHR",
    0b0110: "ROL",
    0b0111: "ROR",
    0b1000: "AND",
    0b1001: "OR",
    0b1010: "XOR",
    0b1011: "NOR",
    0b1100: "NAND",
    0b1101: "XNOR",
    0b1110: "GT",
    0b1111: "EQ",
}

# Helper function to compute expected result
def compute_expected(A, B, sel):
    if sel == 0b0000:  # ADD
        res = (A + B) & 0xF
    elif sel == 0b0001:  # SUB
        res = (A - B) & 0xF
    elif sel == 0b0010:  # MUL
        res = (A * B) & 0xF
    elif sel == 0b0011:  # DIV
        res = (A // B) if B != 0 else 0b1111
    elif sel == 0b0100:  # SHL
        res = (A << 1) & 0xF
    elif sel == 0b0101:  # SHR
        res = (A >> 1) & 0xF
    elif sel == 0b0110:  # ROL
        res = ((A << 1) | (A >> 3)) & 0xF
    elif sel == 0b0111:  # ROR
        res = ((A >> 1) | ((A & 1) << 3)) & 0xF
    elif sel == 0b1000:  # AND
        res = A & B
    elif sel == 0b1001:  # OR
        res = A | B
    elif sel == 0b1010:  # XOR
        res = A ^ B
    elif sel == 0b1011:  # NOR
        res = ~(A | B) & 0xF
    elif sel == 0b1100:  # NAND
        res = ~(A & B) & 0xF
    elif sel == 0b1101:  # XNOR
        res = ~(A ^ B) & 0xF
    elif sel == 0b1110:  # GT
        res = 0b1 if A > B else 0b0
    elif sel == 0b1111:  # EQ
        res = 0b1 if A == B else 0b0
    else:
        res = 0b0
    return res

@cocotb.test()
async def alu_wrapper_test(dut):
    """Test the 4-bit ALU wrapper with multiple operations using binary operands"""

    # Create clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset
    dut.rst_n.value = 0
    dut.ena.value = 1
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Test all ALU operations for a few operand combinations (binary literals)
    test_vectors = [
        (0b0011, 0b0010),  # 3, 2
        (0b1111, 0b0001),  # 15, 1
        (0b0111, 0b0111),  # 7, 7
        (0b0000, 0b0101),  # 0, 5
        (0b1010, 0b0101),  # 10, 5
    ]

    for A, B in test_vectors:
        dut.ui_in.value = (B << 4) | A
        for sel in range(16):
            dut.uio_in.value = sel
            await RisingEdge(dut.clk)
            await Timer(1, units="ns")  # small propagation delay

            expected = compute_expected(A, B, sel)
            alu_out = int(dut.uo_out.value & 0xF)
            
            if alu_out != expected:
                raise TestFailure(f"ALU Error: A={A:04b}, B={B:04b}, OP={ALU_OPS[sel]} expected={expected:04b}, got={alu_out:04b}")
            
            dut._log.info(f"A={A:04b} B={B:04b} OP={ALU_OPS[sel]} -> OUT={alu_out:04b}")
