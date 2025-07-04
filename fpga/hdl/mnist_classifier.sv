// AUTOGENERATED DO NOT EDIT

`timescale 1ns / 1ps


module mnist_classifier(input logic clk, input logic [0:783] image, output logic [3:0] digit);
    logic [7:0] score [0:9];

    // Digit 0
    wire [0:1411] leaf_0;
    wire [7:0] val_count_0 [0:12];
    wire [7:0] score_0;
    (* preserve, noprune *) reg [0:783] image_0_reg;
    reg [7:0] val_count_0_reg [0:12];
    
    decision_tree_leaves_0 dtl_0 (.f(image_0_reg), .leaf(leaf_0));
    leaf_counter_0 lc_0 (.clk(clk), .l(leaf_0), .val(val_count_0));
    counter_adder ca_0 (.clk(clk), .val(val_count_0_reg), .score(score_0));

    always_ff @(posedge clk) begin
        image_0_reg <= image;
        for (int i = 0; i < 13; i = i + 1) begin
            val_count_0_reg[i] <= val_count_0[i];
        end
        score[0] <= score_0;
    end
    


    // Digit 1
    wire [0:1154] leaf_1;
    wire [7:0] val_count_1 [0:12];
    wire [7:0] score_1;
    (* preserve, noprune *) reg [0:783] image_1_reg;
    reg [7:0] val_count_1_reg [0:12];
    
    decision_tree_leaves_1 dtl_1 (.f(image_1_reg), .leaf(leaf_1));
    leaf_counter_1 lc_1 (.clk(clk), .l(leaf_1), .val(val_count_1));
    counter_adder ca_1 (.clk(clk), .val(val_count_1_reg), .score(score_1));

    always_ff @(posedge clk) begin
        image_1_reg <= image;
        for (int i = 0; i < 13; i = i + 1) begin
            val_count_1_reg[i] <= val_count_1[i];
        end
        score[1] <= score_1;
    end
    


    // Digit 2
    wire [0:1374] leaf_2;
    wire [7:0] val_count_2 [0:12];
    wire [7:0] score_2;
    (* preserve, noprune *) reg [0:783] image_2_reg;
    reg [7:0] val_count_2_reg [0:12];
    
    decision_tree_leaves_2 dtl_2 (.f(image_2_reg), .leaf(leaf_2));
    leaf_counter_2 lc_2 (.clk(clk), .l(leaf_2), .val(val_count_2));
    counter_adder ca_2 (.clk(clk), .val(val_count_2_reg), .score(score_2));

    always_ff @(posedge clk) begin
        image_2_reg <= image;
        for (int i = 0; i < 13; i = i + 1) begin
            val_count_2_reg[i] <= val_count_2[i];
        end
        score[2] <= score_2;
    end
    


    // Digit 3
    wire [0:1472] leaf_3;
    wire [7:0] val_count_3 [0:12];
    wire [7:0] score_3;
    (* preserve, noprune *) reg [0:783] image_3_reg;
    reg [7:0] val_count_3_reg [0:12];
    
    decision_tree_leaves_3 dtl_3 (.f(image_3_reg), .leaf(leaf_3));
    leaf_counter_3 lc_3 (.clk(clk), .l(leaf_3), .val(val_count_3));
    counter_adder ca_3 (.clk(clk), .val(val_count_3_reg), .score(score_3));

    always_ff @(posedge clk) begin
        image_3_reg <= image;
        for (int i = 0; i < 13; i = i + 1) begin
            val_count_3_reg[i] <= val_count_3[i];
        end
        score[3] <= score_3;
    end
    


    // Digit 4
    wire [0:1315] leaf_4;
    wire [7:0] val_count_4 [0:12];
    wire [7:0] score_4;
    (* preserve, noprune *) reg [0:783] image_4_reg;
    reg [7:0] val_count_4_reg [0:12];
    
    decision_tree_leaves_4 dtl_4 (.f(image_4_reg), .leaf(leaf_4));
    leaf_counter_4 lc_4 (.clk(clk), .l(leaf_4), .val(val_count_4));
    counter_adder ca_4 (.clk(clk), .val(val_count_4_reg), .score(score_4));

    always_ff @(posedge clk) begin
        image_4_reg <= image;
        for (int i = 0; i < 13; i = i + 1) begin
            val_count_4_reg[i] <= val_count_4[i];
        end
        score[4] <= score_4;
    end
    


    // Digit 5
    wire [0:1401] leaf_5;
    wire [7:0] val_count_5 [0:12];
    wire [7:0] score_5;
    (* preserve, noprune *) reg [0:783] image_5_reg;
    reg [7:0] val_count_5_reg [0:12];
    
    decision_tree_leaves_5 dtl_5 (.f(image_5_reg), .leaf(leaf_5));
    leaf_counter_5 lc_5 (.clk(clk), .l(leaf_5), .val(val_count_5));
    counter_adder ca_5 (.clk(clk), .val(val_count_5_reg), .score(score_5));

    always_ff @(posedge clk) begin
        image_5_reg <= image;
        for (int i = 0; i < 13; i = i + 1) begin
            val_count_5_reg[i] <= val_count_5[i];
        end
        score[5] <= score_5;
    end
    


    // Digit 6
    wire [0:1336] leaf_6;
    wire [7:0] val_count_6 [0:12];
    wire [7:0] score_6;
    (* preserve, noprune *) reg [0:783] image_6_reg;
    reg [7:0] val_count_6_reg [0:12];
    
    decision_tree_leaves_6 dtl_6 (.f(image_6_reg), .leaf(leaf_6));
    leaf_counter_6 lc_6 (.clk(clk), .l(leaf_6), .val(val_count_6));
    counter_adder ca_6 (.clk(clk), .val(val_count_6_reg), .score(score_6));

    always_ff @(posedge clk) begin
        image_6_reg <= image;
        for (int i = 0; i < 13; i = i + 1) begin
            val_count_6_reg[i] <= val_count_6[i];
        end
        score[6] <= score_6;
    end
    


    // Digit 7
    wire [0:1279] leaf_7;
    wire [7:0] val_count_7 [0:12];
    wire [7:0] score_7;
    (* preserve, noprune *) reg [0:783] image_7_reg;
    reg [7:0] val_count_7_reg [0:12];
    
    decision_tree_leaves_7 dtl_7 (.f(image_7_reg), .leaf(leaf_7));
    leaf_counter_7 lc_7 (.clk(clk), .l(leaf_7), .val(val_count_7));
    counter_adder ca_7 (.clk(clk), .val(val_count_7_reg), .score(score_7));

    always_ff @(posedge clk) begin
        image_7_reg <= image;
        for (int i = 0; i < 13; i = i + 1) begin
            val_count_7_reg[i] <= val_count_7[i];
        end
        score[7] <= score_7;
    end
    


    // Digit 8
    wire [0:1497] leaf_8;
    wire [7:0] val_count_8 [0:12];
    wire [7:0] score_8;
    (* preserve, noprune *) reg [0:783] image_8_reg;
    reg [7:0] val_count_8_reg [0:12];
    
    decision_tree_leaves_8 dtl_8 (.f(image_8_reg), .leaf(leaf_8));
    leaf_counter_8 lc_8 (.clk(clk), .l(leaf_8), .val(val_count_8));
    counter_adder ca_8 (.clk(clk), .val(val_count_8_reg), .score(score_8));

    always_ff @(posedge clk) begin
        image_8_reg <= image;
        for (int i = 0; i < 13; i = i + 1) begin
            val_count_8_reg[i] <= val_count_8[i];
        end
        score[8] <= score_8;
    end
    


    // Digit 9
    wire [0:1347] leaf_9;
    wire [7:0] val_count_9 [0:12];
    wire [7:0] score_9;
    (* preserve, noprune *) reg [0:783] image_9_reg;
    reg [7:0] val_count_9_reg [0:12];
    
    decision_tree_leaves_9 dtl_9 (.f(image_9_reg), .leaf(leaf_9));
    leaf_counter_9 lc_9 (.clk(clk), .l(leaf_9), .val(val_count_9));
    counter_adder ca_9 (.clk(clk), .val(val_count_9_reg), .score(score_9));

    always_ff @(posedge clk) begin
        image_9_reg <= image;
        for (int i = 0; i < 13; i = i + 1) begin
            val_count_9_reg[i] <= val_count_9[i];
        end
        score[9] <= score_9;
    end
    

    // Get maximum score
    max_value_index mvi(.clk(clk), .score(score), .digit(digit));
endmodule