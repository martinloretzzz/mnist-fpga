`timescale 1ns / 1ps

// This module has dynamic memory, so that that synthesisation tool can't optimize it away.

module mnist_runner (
    input logic clk,
    output logic [3:0] digit [0:3],
    input logic write_enable,
    input logic [1:0] write_digit,
    input logic [9:0] write_addr,
    input logic [7:0] write_data
);
    reg [0:783] image_mem [0:3];
    reg [3:0] digit_mem [0:3];
    logic [3:0] digit_out [0:3];

    initial begin
        for (int d = 0; d < 4; d++) begin
            for (int i = 0; i < 784; i++) begin
                image_mem[d][i] = 0;
            end
        end
    end

    mnist_classifier mcl0 (.clk(clk), .image(image_mem[0]), .digit(digit_out[0]));
    mnist_classifier mcl1 (.clk(clk), .image(image_mem[1]), .digit(digit_out[1]));
    mnist_classifier mcl2 (.clk(clk), .image(image_mem[2]), .digit(digit_out[2]));
    mnist_classifier mcl3 (.clk(clk), .image(image_mem[3]), .digit(digit_out[3]));

    always_ff @(posedge clk) begin
        digit_mem <= digit_out;
    end

    always_ff @(posedge clk) begin
        if (write_enable) begin
            image_mem[write_digit][write_addr] <= write_data;
        end
        digit <= digit_mem;
    end
endmodule
