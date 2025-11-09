module full_add
  (input [0:0] a_i
  ,input [0:0] b_i
  ,input [0:0] carry_i
  ,output [0:0] carry_o
  ,output [0:0] sum_o);

   // For Lab 3, do not use _any_ behavioral verilog in this
   // module. You may use assign statments to connect wires, but not
   // to perform logic. 

   // Your code here:

  wire unused_w;

  ICESTORM_LC 
    #(.LUT_INIT(16'b1001011010010110),
      .CIN_SET(1'b0),
      .CARRY_ENABLE(1'b1)
    )
  ICESTORM_LC_inst (
    .I0(carry_i), 
    .I1(a_i), 
    .I2(b_i), 
    .I3(1'b0), 
    .CIN(carry_i), 
    .CLK(1'b0), 
    .CEN(1'b0), 
    .SR(1'b0),
	  .LO(sum_o),
	  .O(unused_w),
	  .COUT(carry_o)
  );

endmodule
