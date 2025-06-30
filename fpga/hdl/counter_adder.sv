`timescale 1ns / 1ps

module counter_adder(input logic clk, input logic [7:0] val [0:12], output logic [7:0] score);
	logic [7:0] negative_score;
	logic [7:0] negative_score_reg;
	logic [7:0] negative_score_tmp;
	logic [7:0] negative_score_tmp_reg;

	logic [7:0] positive_score;
	logic [7:0] positive_score_reg;
	logic [7:0] positive_score_tmp [0:1];
	logic [7:0] positive_score_tmp_reg [0:1];

	logic [7:0] val_reg [0:12];

	// -0.015625, -0.03125, -0.0625
	assign negative_score_tmp = ((((val[4] >> 1) + val[3]) >> 1) + val[2]);

	// 0.015625, 0.03125, 0.0625
	assign positive_score_tmp[0] = ((((val[5] >> 1) + val[6]) >> 1) + val[7]);

	// 0.5, 1.0, 2.0
	assign positive_score_tmp[1] = (val[10] << 1) + (val[11] << 2) + (val[12] << 3);

    always_ff @(posedge clk) begin
        negative_score_tmp_reg <= negative_score_tmp;
        positive_score_tmp_reg[0] <= positive_score_tmp[0];
		positive_score_tmp_reg[1] <= positive_score_tmp[1];
		for (int i = 0; i < 13; i = i + 1) begin
            val_reg[i] <= val[i];
		end
    end

	// tmp, -0.125, -0.25
	assign negative_score = (((negative_score_tmp_reg >> 1) + val_reg[1]) >> 1) + val_reg[0];
	// tmp[0], 0.125, 0.25, tmp[1]
	assign positive_score = (((positive_score_tmp_reg[0] >> 1) + val_reg[8]) >> 1) + val_reg[9] + positive_score_tmp_reg[1];

    always_ff @(posedge clk) begin
		negative_score_reg <= negative_score;
		positive_score_reg <= positive_score;
    end

	// Score is in base 0.25 with 128 as the zero value (so we can use unsigned int8)
	assign score = 8'd128 - negative_score_reg + positive_score_reg;
endmodule
