#=========================================================
# Author   : Emrys Leowhel Oling
# Date     : 2025-09-07
# Design   : Exhaustive Cocotb Testbench for 4-bit ALU with Flags
# License  : Apache License 2.0
#=========================================================

import cocotb
from cocotb.triggers import Timer


def compute_flags(A, B, sel, result):
    """Compute expected ALU flags for 4-bit operations"""
    carry = 0
    overflow = 0
    zero = 1 if result == 0 else 0
    negative = (result >> 3) & 1  # MSB of result

    if sel == 0b0000:  # ADD
        full = A + B
        carry = 1 if full > 0b1111 else 0
        overflow = 1 if (((A ^ result) & (B ^ result)) & 0b1000) else 0

    elif sel == 0b0001:  # SUB
        full = (A - B) & 0x1F  # 5 bits to catch borrow
        carry = 1 if (A < B) else 0
        overflow = 1 if (((A ^ B) & (A ^ result)) & 0b1000) else 0

    return carry, zero, negative, overflow


@cocotb.test()
async def alu_exhaustive_test(dut):
    """Exhaustive test: check all possible input combinations (A,B,Sel) and save results"""

    # Open a results file
    with open("alu_results.csv", "w") as f:
        # Write header
        f.write("A,B,Sel,Out,Carry,Zero,Negative,Overflow,Exp_Carry,Exp_Zero,Exp_Negative,Exp_Overflow\n")

        for A in range(16):       # 4-bit A
            for B in range(16):   # 4-bit B
                for sel in range(16):  # 4-bit ALU_Sel

                    # Apply inputs
                    dut.ui_in.value = (B << 4) | A  # [7:4]=B, [3:0]=A
                    dut.uio_in.value = sel          # ALU_Sel

                    await Timer(1, units="ns")

                    # Read DUT outputs
                    uo_val = dut.uo_out.value.integer
                    alu_out = uo_val & 0xF        # [3:0] = ALU result
                    carry   = (uo_val >> 7) & 1   # bit 7
                    zero    = (uo_val >> 6) & 1   # bit 6
                    negative= (uo_val >> 5) & 1   # bit 5
                    overflow= (uo_val >> 4) & 1   # bit 4

                    # Compute expected flags (only defined for ADD and SUB)
                    exp_carry, exp_zero, exp_negative, exp_overflow = compute_flags(A, B, sel, alu_out)

                    # Save line into file
                    f.write(f"{A},{B},{sel},{alu_out},{carry},{zero},{negative},{overflow},"
                            f"{exp_carry},{exp_zero},{exp_negative},{exp_overflow}\n")

                    # Also log in simulator
                    dut._log.info(
                        f"A={A:04b}({A}), B={B:04b}({B}), Sel={sel:04b}({sel}) "
                        f"=> Out={alu_out:04b}({alu_out}), Flags [CZN0]={carry}{zero}{negative}{overflow}"
                    )
