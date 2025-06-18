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

Power:
- 350mW Static (Base) Power consumption
- 61mW @ 10MHz
- 152mW @ 25MHz
- 305mW @ 50MHz
- 610mW @ 100MHz

> Higher clock rates yield higher img/s/W, because the relative fraction of the static power gets smaller.
