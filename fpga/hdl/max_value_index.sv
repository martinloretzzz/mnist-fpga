`timescale 1ns / 1ps

module max_value_index(input logic [7:0] score [0:9], output logic [3:0] digit);
	logic [3:0] max_l0_idx [0:4];
	logic [3:0] max_l0_val [0:4];
	logic [3:0] max_l1_idx [0:2];
	logic [3:0] max_l1_val [0:2];
	logic [3:0] max_l2_idx;
	logic [3:0] max_l2_val;

	assign max_l0_idx[0] = (score[0] >= score[1]) ? 4'd0 : 4'd1;
	assign max_l0_val[0] = (score[0] >= score[1]) ? score[0] : score[1];
	assign max_l0_idx[1] = (score[2] >= score[3]) ? 4'd2 : 4'd3;
	assign max_l0_val[1] = (score[2] >= score[3]) ? score[2] : score[3];
	assign max_l0_idx[2] = (score[4] >= score[5]) ? 4'd4 : 4'd5;
	assign max_l0_val[2] = (score[4] >= score[5]) ? score[4] : score[5];
	assign max_l0_idx[3] = (score[6] >= score[7]) ? 4'd6 : 4'd7;
	assign max_l0_val[3] = (score[6] >= score[7]) ? score[6] : score[7];
	assign max_l0_idx[4] = (score[8] >= score[9]) ? 4'd8 : 4'd9; 
	assign max_l0_val[4] = (score[8] >= score[9]) ? score[8] : score[9];

	assign max_l1_idx[0] = (max_l0_val[0] >= max_l0_val[1]) ? max_l0_idx[0] : max_l0_idx[1];
	assign max_l1_val[0] = (max_l0_val[0] >= max_l0_val[1]) ? max_l0_val[0] : max_l0_val[1];
	assign max_l1_idx[1] = (max_l0_val[2] >= max_l0_val[3]) ? max_l0_idx[2] : max_l0_idx[3];
	assign max_l1_val[1] = (max_l0_val[2] >= max_l0_val[3]) ? max_l0_val[2] : max_l0_val[3];

	assign max_l2_idx = (max_l1_val[0] >= max_l1_val[1]) ? max_l1_idx[0] : max_l1_idx[1];
	assign max_l2_val = (max_l1_val[0] >= max_l1_val[1]) ? max_l1_val[0] : max_l1_val[1];

	assign digit = (max_l2_val >= max_l0_val[4]) ? max_l2_idx : max_l0_idx[4];
endmodule
