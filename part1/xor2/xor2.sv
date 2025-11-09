module xor2
  (input [0:0] a_i
  ,input [0:0] b_i
  ,output [0:0] c_o);

   // Your code here:

  LUT6
    #(.INIT(64'b0110011001100110011001100110011001100110011001100110011001100110))
  LUT6_inst (
    .I0(a_i),
    .I1(b_i),
    .I2(1'b0),
    .I3(1'b0),
    .I4(1'b0),
    .I5(1'b0),
    .O(c_o)
  );

endmodule
