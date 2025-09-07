import cocotb
from cocotb.triggers import Timer
from cocotb.clock import Clock

# Simple ALU function to compute expected result
def alu_expected(A, B, opcode):
    if opcode == 0b0000:  # ADD
        return (A + B) & 0xF
    if opcode == 0b0001:  # SUB
        return (A - B) & 0xF
    if opcode == 0b0010:  # MUL
        return (A * B) & 0xF
    if opcode == 0b0011:  # DIV
        return (A // B) if B != 0 else 0xF
    if opcode == 0b0100:  # SHL
        return (A << 1) & 0xF
    if opcode == 0b0101:  # SHR
        return (A >> 1) & 0xF
    if opcode == 0b0110:  # ROL
        return ((A << 1) | (A >> 3)) & 0xF
    if opcode == 0b0111:  # ROR
        return ((A >> 1) | ((A & 1) << 3)) & 0xF
    if opcode == 0b1000:  # AND
        return A & B
    if opcode == 0b1001:  # OR
        return A | B
    if opcode == 0b1010:  # XOR
        return A ^ B
    if opcode == 0b1011:  # NOR
        return ~(A | B) & 0xF
    if opcode == 0b1100:  # NAND
        return ~(A & B) & 0xF
    if opcode == 0b1101:  # XNOR
        return ~(A ^ B) & 0xF
    if opcode == 0b1110:  # GT
        return 1 if A > B else 0
    if opcode == 0b1111:  # EQ
        return 1 if A == B else 0
    return 0

@cocotb.test()
async def test_tt_um_alu_wrapper(dut):
    """Waveform-friendly ALU test with expected result display."""

    # Start clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Initialize inputs
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.ena.value = 1
    dut.rst_n.value = 0

    # Hold reset
    await Timer(50, units='ns')
    dut.rst_n.value = 1
    await Timer(20, units='ns')

    # Test vectors: (A, B, opcode, name)
    test_vectors = [
        (0b0011, 0b0101, 0b0000, "ADD"),
        (0b0010, 0b0001, 0b0001, "SUB"),
        (0b0010, 0b0011, 0b0010, "MUL"),
        (0b0100, 0b0010, 0b0011, "DIV"),
        (0b0010, 0b0010, 0b1000, "AND"),
        (0b1100, 0b1010, 0b1001, "OR"),
        (0b1100, 0b1010, 0b1010, "XOR"),
    ]

    # Apply test vectors
    for A, B, opcode, name in test_vectors:
        dut.ui_in.value = (B << 4) | A
        dut.uio_in.value = opcode
        await Timer(50, units='ns')

        # Compute expected result
        expected = alu_expected(A, B, opcode)

        # Print DUT output and expected
        print(f"{name}: A={A:04b}, B={B:04b}, opcode={opcode:04b} -> "
              f"uo_out={dut.uo_out.value}, expected={expected:04b}")
