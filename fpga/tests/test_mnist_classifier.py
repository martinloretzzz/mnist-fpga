import cocotb
import torch
import torchvision
from cocotb.triggers import Timer

def binarize(x):
    x = x.flatten(1)
    return torch.where(x > 0.3, torch.tensor(1.0), torch.tensor(0.0))

def get_mnist_test_dataset():
    test_dataset = torchvision.datasets.MNIST(root='../../../data', train=False, download=True, transform=torchvision.transforms.ToTensor())
    data = binarize(test_dataset.data).view(-1, 28*28).long()
    targets = test_dataset.targets
    return data, targets

x_test, y_test = get_mnist_test_dataset()

def set_vector(signal, values):
    assert len(signal) == len(values)
    for i in range(len(signal)):
        signal[i].value = values[i]


@cocotb.test()
async def test_classifier_on_first_digit(dut):
    image_id = 0
    first_image = x_test[image_id].tolist()
    first_label = y_test[image_id].tolist()

    set_vector(dut.image, first_image)
    await Timer(1, units="ns")

    assert dut.digit.value == first_label
