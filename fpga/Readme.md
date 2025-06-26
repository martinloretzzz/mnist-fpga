## Install

pip install cocotb pytest torch torchvision
sudo apt update
sudo apt install iverilog

ALM Usage:
- Initial Design: 14418

Initial Design:
- Clock: 25MHz
- ALM: 14.4k
- Power: 510mW
- 49.02 Mimg/s/W

Combine same discrete values inside tree (OR Gate, only single leaf active):
- Clock: 25MHz
- ALM: 11.3k
- Setup Slack: 4.1
- Power: 473mW
- 52.85 Mimg/s/W
- 56.53 Mimg/s @ 27.5MHz & 486mW

Paralell prefix sum with 6 input on the first stage:
- Clock: 25MHz
- ALM: 11.3k
- Setup Slack: 7.76
- Power: 469mW
- 53.3 Mimg/s/W
- 62.5 Mimg/s @ 31MHz & 496mW

Pipeline classifier:
- Clock: 100MHz
- ALM: 13.8k
- Setup Slack: 0.39
- Power: 424mW
- 235.8 Mimg/s/W

Pipeline everything to the maximum and aggressive perfomance compiler:
- Clock: 200MHz
- ALM: 16.0k
- Setup Slack: 0.312 (Fmax=213.3 MHz)
- Power: 892.7mW
- 224.2 Mimg/s/W
- 228.0 Mimg/s/W @ 210.5MHz & 921mW

Power:
- 350mW Static (Base) Power consumption
- 61mW @ 10MHz
- 152mW @ 25MHz
- 305mW @ 50MHz
- 610mW @ 100MHz

> Higher clock rates yield higher img/s/W, because the relative fraction of the static power gets smaller.
