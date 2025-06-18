`timescale 1ns / 1ps

module max_value_index(input logic [7:0] score [0:9], output logic [7:0] digit);
	logic [3:0] max_l0 [0:4];
	logic [3:0] max_l1 [0:2];
	logic [3:0] max_l2;

	// Reduce first 8 elements
	assign max_l0[0] = (score[0] >= score[1]) ? 4'd0 : 4'd1;
	assign max_l0[1] = (score[2] >= score[3]) ? 4'd2 : 4'd3;
	assign max_l0[2] = (score[4] >= score[5]) ? 4'd4 : 4'd5;
	assign max_l0[3] = (score[6] >= score[7]) ? 4'd6 : 4'd7;

	assign max_l1[0] = (score[max_l0[0]] >= score[max_l0[1]]) ? max_l0[0] : max_l0[1];
	assign max_l1[1] = (score[max_l0[2]] >= score[max_l0[3]]) ? max_l0[2] : max_l0[3];

	assign max_l2 = (score[max_l1[0]] >= score[max_l1[1]]) ? max_l1[0] : max_l1[1];

	// Combine result of first 8 with the last 2 elements
	assign max_l0[4] = (score[8] >= score[9]) ? 4'd8 : 4'd9; 
	assign digit = (score[max_l2] >= score[max_l0[4]]) ? max_l2 : max_l0[4];
endmodule
