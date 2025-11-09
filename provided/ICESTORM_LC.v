module ICESTORM_LC (
	input I0, I1, I2, I3, CIN, CLK, CEN, SR,
	output LO,
	output O,
	output COUT
);
	parameter [15:0] LUT_INIT = 0;

	parameter [0:0] NEG_CLK      = 0;
	parameter [0:0] CARRY_ENABLE = 0;
	parameter [0:0] DFF_ENABLE   = 0;
	parameter [0:0] SET_NORESET  = 0;
	parameter [0:0] ASYNC_SR     = 0;

	parameter [0:0] CIN_CONST    = 0;
	parameter [0:0] CIN_SET      = 0;

	wire I0_pd = I0;
	wire I1_pd = I1;
	wire I2_pd = I2;
	wire I3_pd = I3;
	wire SR_pd = SR;
	wire CEN_pu = CEN;

	wire mux_cin = CIN_CONST ? CIN_SET : CIN;

	assign COUT = CARRY_ENABLE ? (I1_pd && I2_pd) || ((I1_pd || I2_pd) && mux_cin) : 1'bx;

	wire [7:0] lut_s3 = I3_pd ? LUT_INIT[15:8] : LUT_INIT[7:0];
	wire [3:0] lut_s2 = I2_pd ?   lut_s3[ 7:4] :   lut_s3[3:0];
	wire [1:0] lut_s1 = I1_pd ?   lut_s2[ 3:2] :   lut_s2[1:0];
	wire       lut_o  = I0_pd ?   lut_s1[   1] :   lut_s1[  0];

	assign LO = lut_o;

	wire polarized_clk;
	assign polarized_clk = CLK ^ NEG_CLK;

	reg o_reg = 1'b0;
	always @(posedge polarized_clk)
		if (CEN_pu)
			o_reg <= SR_pd ? SET_NORESET : lut_o;

	reg o_reg_async = 1'b0;
	always @(posedge polarized_clk, posedge SR_pd)
		if (SR_pd)
			o_reg_async <= SET_NORESET;
		else if (CEN_pu)
			o_reg_async <= lut_o;

	assign O = DFF_ENABLE ? ASYNC_SR ? o_reg_async : o_reg : lut_o;
endmodule
