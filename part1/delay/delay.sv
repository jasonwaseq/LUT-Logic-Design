module delay
  #(parameter delay_p = 5
    )
   (input [0:0] clk_i
   ,input [0:0] reset_i
   ,input [0:0] en_i
   ,input [0:0] d_i
   ,output [0:0] d_o);

   // For Lab 3, do not use _any_ behavioral verilog in this
   // module. You may use assign statments to connect wires, but not
   // to perform logic. 

   // Your code here:
   /* verilator lint_off WIDTHTRUNC */

  wire [3:0] address;
  assign address = delay_p - 1;

  wire unused_w;
  assign unused_w = reset_i;

  SRL16E 
    #(.INIT(16'h0000),
      .IS_CLK_INVERTED(1'b0))
  SRL16E_inst (
    .A0(address[0]), 
    .A1(address[1]), 
    .A2(address[2]), 
    .A3(address[3]), 
    .CE(en_i),
    .CLK(clk_i),
    .D(d_i),
    .Q(d_o)
  );


endmodule
