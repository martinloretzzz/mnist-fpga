`timescale 1ns / 1ps

module max_value_index (
    input logic clk,
    input logic [7:0] score [0:9],
    output logic [3:0] digit
);

    // Stage 0
    logic [3:0] max_l0_idx [0:4];
    logic [7:0] max_l0_val [0:4];
    logic [3:0] max_l0_idx_reg [0:4];
    logic [7:0] max_l0_val_reg [0:4];

    // Stage 1
    logic [3:0] max_l1_idx [0:1];
    logic [7:0] max_l1_val [0:1];
    logic [3:0] max_l1_idx_reg [0:1];
    logic [7:0] max_l1_val_reg [0:1];
    logic [3:0] max_l0_idx_reg2; // Pass max_l0_idx[4]
    logic [7:0] max_l0_val_reg2; // Pass max_l0_val[4]

    // Stage 2
    logic [3:0] max_l2_idx;
    logic [7:0] max_l2_val;
    logic [3:0] max_l2_idx_reg;
    logic [7:0] max_l2_val_reg;
    logic [3:0] max_l0_idx_reg3; // Pass max_l0_idx[4]
    logic [7:0] max_l0_val_reg3; // Pass max_l0_val[4]

    // Stage 0
    always_comb begin
        max_l0_idx[0] = (score[0] >= score[1]) ? 4'd0 : 4'd1;
        max_l0_val[0] = (score[0] >= score[1]) ? score[0] : score[1];
        max_l0_idx[1] = (score[2] >= score[3]) ? 4'd2 : 4'd3;
        max_l0_val[1] = (score[2] >= score[3]) ? score[2] : score[3];
        max_l0_idx[2] = (score[4] >= score[5]) ? 4'd4 : 4'd5;
        max_l0_val[2] = (score[4] >= score[5]) ? score[4] : score[5];
        max_l0_idx[3] = (score[6] >= score[7]) ? 4'd6 : 4'd7;
        max_l0_val[3] = (score[6] >= score[7]) ? score[6] : score[7];
        max_l0_idx[4] = (score[8] >= score[9]) ? 4'd8 : 4'd9;
        max_l0_val[4] = (score[8] >= score[9]) ? score[8] : score[9];
    end

    always_ff @(posedge clk) begin
        for (int i = 0; i < 5; i++) begin
            max_l0_idx_reg[i] <= max_l0_idx[i];
            max_l0_val_reg[i] <= max_l0_val[i];
        end
    end

    // Stage 1
    always_comb begin
        max_l1_idx[0] = (max_l0_val_reg[0] >= max_l0_val_reg[1]) ? max_l0_idx_reg[0] : max_l0_idx_reg[1];
        max_l1_val[0] = (max_l0_val_reg[0] >= max_l0_val_reg[1]) ? max_l0_val_reg[0] : max_l0_val_reg[1];
        max_l1_idx[1] = (max_l0_val_reg[2] >= max_l0_val_reg[3]) ? max_l0_idx_reg[2] : max_l0_idx_reg[3];
        max_l1_val[1] = (max_l0_val_reg[2] >= max_l0_val_reg[3]) ? max_l0_val_reg[2] : max_l0_val_reg[3];
    end

    always_ff @(posedge clk) begin
        max_l1_idx_reg[0] <= max_l1_idx[0];
        max_l1_val_reg[0] <= max_l1_val[0];
        max_l1_idx_reg[1] <= max_l1_idx[1];
        max_l1_val_reg[1] <= max_l1_val[1];
        max_l0_idx_reg2 <= max_l0_idx_reg[4];
        max_l0_val_reg2 <= max_l0_val_reg[4];
    end

    // Stage 2
    always_comb begin
        max_l2_idx = (max_l1_val_reg[0] >= max_l1_val_reg[1]) ? max_l1_idx_reg[0] : max_l1_idx_reg[1];
        max_l2_val = (max_l1_val_reg[0] >= max_l1_val_reg[1]) ? max_l1_val_reg[0] : max_l1_val_reg[1];
    end

    always_ff @(posedge clk) begin
        max_l2_idx_reg <= max_l2_idx;
        max_l2_val_reg <= max_l2_val;
        max_l0_idx_reg3 <= max_l0_idx_reg2;
        max_l0_val_reg3 <= max_l0_val_reg2;
    end

    // Stage 3
    always_ff @(posedge clk) begin
        digit <= (max_l2_val_reg >= max_l0_val_reg3) ? max_l2_idx_reg : max_l0_idx_reg3;
    end

endmodule