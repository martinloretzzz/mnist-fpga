`timescale 1ns / 1ps

module counter_adder(input logic [7:0] val [0:12], output logic [7:0] score);
	logic [7:0] negative_score;
	logic [7:0] positive_score;

	// -0.015625, -0.03125, -0.0625, -0.125, -0.25
	assign negative_score = (((((((val[4] >> 1) + val[3]) >> 1) + val[2]) >> 1) + val[1]) >> 1) + val[0];

	// 0.015625, 0.03125, 0.0625, 0.125, 0.25, 0.5, 1.0, 2.0
	assign positive_score = (((((((val[5] >> 1) + val[6]) >> 1) + val[7]) >> 1) + val[8]) >> 1) + val[9] + (val[10] << 1) + (val[11] << 2) + (val[12] << 3);

	// Score is in base 0.25 with 128 as the zero value (so we can use unsigned int8)
	assign score = 128 - negative_score + positive_score;
endmodule
