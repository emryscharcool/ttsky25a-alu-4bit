//=========================================================
// Author   : Emrys Leowhel Oling
// Date     : 2025-09-07
// Design   : Tiny Tapeout Wrapper for 4-bit ALU
// License  : Apache-2.0
//=========================================================

`default_nettype none
`timescale 1ns/1ns

module tt_um_alu_4bit_wrapper (
    input  wire [7:0] ui_in,    // [3:0] = A, [7:4] = B
    output wire [7:0] uo_out,   // {Flags[3:0], ALU_Out[3:0]}
    input  wire [7:0] uio_in,   // [3:0] = ALU_Sel
    output wire [7:0] uio_out,  // Not used
    output wire [7:0] uio_oe,   // Not used
    input  wire ena,            // enable (unused)
    input  wire clk,            // clock (unused)
    input  wire rst_n           // reset (unused)
);

    assign uio_out = 8'h00;
    assign uio_oe  = 8'h00;

    // Internal wires
    wire [3:0] alu_out;
    wire carry, zero, negative, overflow;

    // Explicit operand split
    wire [3:0] a_in   = ui_in[3:0]; // Operand A
    wire [3:0] b_in   = ui_in[7:4]; // Operand B
    wire [3:0] sel_in = uio_in[3:0];// ALU select

    // Instantiate ALU
    alu_4bit alu_inst (
        .clk(clk),
        .rst_n(rst_n),
        .A(a_in),
        .B(b_in),
        .ALU_Sel(sel_in),
        .ALU_Out(alu_out),
        .Carry(carry),
        .Zero(zero),
        .Negative(negative),
        .Overflow(overflow)
    );

    // Pack outputs: upper 4 bits = flags, lower 4 bits = ALU result
    assign uo_out = {carry, zero, negative, overflow, alu_out};

endmodule
