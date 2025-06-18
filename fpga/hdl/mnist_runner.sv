`timescale 1ns / 1ps

// This module has dynamic memory, so that that synthesisation tool can't optimize it away.

module mnist_runner (
    input logic clk,
    output logic [3:0] digit,
    input logic write_enable,
    input logic [9:0] write_addr,
    input logic [7:0] write_data
);
    logic [0:783] mem;
    logic [3:0] digit_out;

    initial begin
        for (int i = 0; i < 784; i++) begin
            mem[i] = 0;
        end
    end

    mnist_classifier mcl (.image(mem), .digit(digit_out));

    always_ff @(posedge clk) begin
        if (write_enable) begin
            mem[write_addr] <= write_data;
        end

        digit <= digit_out;
    end
endmodule