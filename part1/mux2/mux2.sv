module mux2
  (input [0:0] a_i
  ,input [0:0] b_i
  ,input [0:0] select_i
  ,output [0:0] c_o);

   // For Lab 3, do not use _any_ behavioral verilog in this
   // module. You may use assign statments to connect wires, but not
   // to perform logic. 

   // Your code here:

  LUT6
    #(.INIT(64'b1100101011001010110010101100101011001010110010101100101011001010))
  LUT6_inst (
    .I0(a_i),
    .I1(b_i),
    .I2(select_i),
    .I3(1'b0),
    .I4(1'b0),
    .I5(1'b0),
    .O(c_o)
  );

endmodule
