//=========================================================
// Author   : Emrys Leowhel Oling
// Date     : 2025-09-07
// Design   : 4-bit ALU with Flags (Clocked Version)
// Purpose  : For TTsky25a ALU (Tiny Tapeout project)
// License  : APACHE-2.0
//=========================================================

`default_nettype none
`timescale 1ns/1ns

module alu_4bit (
    input  wire       clk,       // Clock
    input  wire       rst_n,     // Active-low reset (optional)
    input  wire [3:0] A,         // First operand
    input  wire [3:0] B,         // Second operand
    input  wire [3:0] ALU_Sel,   // Operation select
    output reg  [3:0] ALU_Out,   // ALU result

    // Status flags
    output reg Carry,
    output reg Zero,
    output reg Negative,
    output reg Overflow
);
     /*    ALU Operations:  0000=ADD, 
                        0001=SUB, 
                        0010=MUL, 
                        0011=DIV, 
                        0100=SHL, 
                        0101=SHR, 
                        0110=ROL, 
                        0111=ROR, 
                        1000=AND, 
                        1001=OR, 
                        1010=XOR, 
                        1011=NOR, 
                        1100=NAND, 
                        1101=XNOR, 
                        1110=GT, 
                        1111=EQ */
    reg [4:0] tmp;   

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            // Reset all outputs
            ALU_Out  <= 4'h0;
            Carry    <= 1'b0;
            Zero     <= 1'b0;
            Negative <= 1'b0;
            Overflow <= 1'b0;
        end else begin
            // Default values
            ALU_Out  <= 4'h0;
            Carry    <= 1'b0;
            Zero     <= 1'b0;
            Negative <= 1'b0;
            Overflow <= 1'b0;

            case (ALU_Sel)
                // Arithmetic
                4'b0000: begin // ADD
                    tmp      = A + B;
                    ALU_Out  <= tmp[3:0];
                    Carry    <= tmp[4];
                    Overflow <= (A[3] == B[3]) && (ALU_Out[3] != A[3]);
                end
                4'b0001: begin // SUB
                    tmp      = A - B;
                    ALU_Out  <= tmp[3:0];
                    Carry    <= tmp[4];
                    Overflow <= (A[3] != B[3]) && (ALU_Out[3] != A[3]);
                end
                4'b0010: ALU_Out <= A * B;                      // MUL (truncated)
                4'b0011: ALU_Out <= (B != 0) ? (A / B) : 4'hF;  // DIV safe

                // Shifts / rotates
                4'b0100: begin ALU_Out <= A << 1; Carry <= A[3]; end
                4'b0101: begin ALU_Out <= A >> 1; Carry <= A[0]; end
                4'b0110: ALU_Out <= {A[2:0], A[3]}; // rotate left
                4'b0111: ALU_Out <= {A[0], A[3:1]}; // rotate right

                // Logical
                4'b1000: ALU_Out <= A & B;
                4'b1001: ALU_Out <= A | B;
                4'b1010: ALU_Out <= A ^ B;
                4'b1011: ALU_Out <= ~(A | B);
                4'b1100: ALU_Out <= ~(A & B);
                4'b1101: ALU_Out <= ~(A ^ B);

                // Comparisons
                4'b1110: ALU_Out <= (A > B)  ? 4'd1 : 4'd0;
                4'b1111: ALU_Out <= (A == B) ? 4'd1 : 4'd0;
            endcase

            // Common flags
            Zero     <= (ALU_Out == 4'h0);
            Negative <= ALU_Out[3];
        end
    end

endmodule
