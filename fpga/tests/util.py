from cocotb.triggers import Timer
import torch
import torchvision
import numpy as np

def binarize(x, treshhold):
    x = x.flatten(1)
    return torch.where(x > treshhold, torch.tensor(1.0), torch.tensor(0.0))

def get_mnist_dataset(train, as_np_array=False, treshhold=0.3):
    transform = torchvision.transforms.ToTensor()
    dataset = torchvision.datasets.MNIST(root='./data', train=train, download=True, transform=transform)

    data = []
    labels = []
    for img, label in dataset:
        data.append(img)
        labels.append(label)
    data = binarize(torch.cat(data, dim=0), treshhold=treshhold)

    if as_np_array:
        return np.array(data.numpy()), np.array(labels)

    labels = torch.tensor(labels, dtype=torch.long)
    return data, labels


async def wait_clock(dut, cycles):
    for i in range(cycles):
        dut.clk.value = 0
        await Timer(2, units="ns")
        dut.clk.value = 1
        await Timer(2, units="ns")


def vector_high_at(signal, high_indices):
    for i in range(len(signal)):
        signal[i].value = 0
    for index in high_indices:
        signal[index].value = 1

def set_vector(signal, values):
    assert len(signal) == len(values)
    for i in range(len(signal)):
        signal[i].value = values[i]

def print_vector_decimal(signal, zero_offset=0):
    print([(int(x) - zero_offset) if str(x).isdigit() else x for x in signal])

def print_signal_decimal(signal, zero_offset=0):
    print((int(signal) - zero_offset) if str(signal).isdigit() else signal)
