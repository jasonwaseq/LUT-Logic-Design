module triadder
  #(parameter width_p = 5)
  // You must fill in the bit widths of a_i, b_i and sum_o. a_i and
  // b_i must be width_p bits.
  (input [width_p-1:0] a_i
  ,input [width_p-1:0] b_i
  ,input [width_p-1:0] c_i
  ,output [width_p+1:0] sum_o);

   // Your code here

  wire [width_p-1:0] carry_w;
  wire [width_p-1:0] sum_w;

  genvar i;
  generate
    for (i=0; i < width_p; i++) begin : fa
      full_add
        #()
      full_add_inst (
        .a_i(a_i[i]),
        .b_i(b_i[i]),
        .carry_i(c_i[i]),
        .carry_o(carry_w[i]),
        .sum_o(sum_w[i])
      );
    end
  endgenerate

  wire [width_p+1:0] sum_extended = {{2{1'b0}}, sum_w};
  wire [width_p+1:0] carry_shifted = {{1{1'b0}}, carry_w, 1'b0};
  
  assign sum_o = sum_extended + carry_shifted;

endmodule
