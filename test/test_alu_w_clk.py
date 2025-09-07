#=========================================================
# Author   : Emrys Leowhel Oling
# Date     : 2025-09-07
# Design   : Cocotb Testbench for 4-bit Clocked ALU
# License  : Apache License 2.0
#=========================================================

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


def compute_expected(A, B, sel):
    """Compute expected result and flags for a given operation"""
    alu_out = 0
    carry = 0
    overflow = 0

    if sel == 0b0000:  # ADD
        tmp = A + B
        alu_out = tmp & 0xF
        carry = (tmp >> 4) & 1
        overflow = (A >> 3 == B >> 3) and ((alu_out >> 3) != (A >> 3))
    elif sel == 0b0001:  # SUB
        tmp = (A - B) & 0x1F
        alu_out = tmp & 0xF
        carry = (tmp >> 4) & 1
        overflow = ((A >> 3) != (B >> 3)) and ((alu_out >> 3) != (A >> 3))
    elif sel == 0b0010:  # MUL
        alu_out = (A * B) & 0xF
    elif sel == 0b0011:  # DIV
        alu_out = (A // B) if B != 0 else 0xF
    elif sel == 0b0100:  # SHL
        alu_out = (A << 1) & 0xF
        carry = (A >> 3) & 1
    elif sel == 0b0101:  # SHR
        alu_out = (A >> 1) & 0xF
        carry = A & 1
    elif sel == 0b0110:  # ROL
        alu_out = ((A << 1) | (A >> 3)) & 0xF
    elif sel == 0b0111:  # ROR
        alu_out = ((A >> 1) | ((A & 1) << 3)) & 0xF
    elif sel == 0b1000:  # AND
        alu_out = A & B
    elif sel == 0b1001:  # OR
        alu_out = A | B
    elif sel == 0b1010:  # XOR
        alu_out = A ^ B
    elif sel == 0b1011:  # NOR
        alu_out = ~(A | B) & 0xF
    elif sel == 0b1100:  # NAND
        alu_out = ~(A & B) & 0xF
    elif sel == 0b1101:  # XNOR
        alu_out = ~(A ^ B) & 0xF
    elif sel == 0b1110:  # GT
        alu_out = 1 if A > B else 0
    elif sel == 0b1111:  # EQ
        alu_out = 1 if A == B else 0

    zero = 1 if alu_out == 0 else 0
    negative = (alu_out >> 3) & 1

    return alu_out, carry, zero, negative, overflow


@cocotb.test()
async def clocked_alu_exhaustive(dut):
    """Exhaustive test for clocked ALU"""

    # Start clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Loop over all combinations
    for A in range(16):
        for B in range(16):
            for sel in range(16):
                # Apply inputs
                dut.A.value = A
                dut.B.value = B
                dut.ALU_Sel.value = sel

                # Wait for next clock cycle
                await RisingEdge(dut.clk)

                # Get DUT outputs
                alu_out = int(dut.ALU_Out.value)
                carry = int(dut.Carry.value)
                zero = int(dut.Zero.value)
                negative = int(dut.Negative.value)
                overflow = int(dut.Overflow.value)

                # Compute expected
                exp_out, exp_carry, exp_zero, exp_negative, exp_overflow = compute_expected(A, B, sel)

                # Check
                assert alu_out == exp_out, f"Mismatch: A={A}, B={B}, Sel={sel:04b}, got Out={alu_out}, exp={exp_out}"
                assert carry == exp_carry, f"Carry mismatch: A={A}, B={B}, Sel={sel:04b}, got {carry}, exp {exp_carry}"
                assert zero == exp_zero, f"Zero mismatch: A={A}, B={B}, Sel={sel:04b}, got {zero}, exp {exp_zero}"
                assert negative == exp_negative, f"Negative mismatch: A={A}, B={B}, Sel={sel:04b}, got {negative}, exp {exp_negative}"
                assert overflow == exp_overflow, f"Overflow mismatch: A={A}, B={B}, Sel={sel:04b}, got {overflow}, exp {exp_overflow}"

                dut._log.info(
                    f"PASS: A={A:04b}, B={B:04b}, Sel={sel:04b} "
                    f"=> Out={alu_out:04b}, Flags CZN0={carry}{zero}{negative}{overflow}"
                )
