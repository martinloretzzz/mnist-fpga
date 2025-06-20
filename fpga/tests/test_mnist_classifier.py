import cocotb
from cocotb.triggers import Timer
from util import get_mnist_dataset

x_test, y_test = get_mnist_dataset(train=False)
x_test, y_test = x_test.long(), y_test.long()

def set_vector(signal, values):
    assert len(signal) == len(values)
    for i in range(len(signal)):
        signal[i].value = values[i]


@cocotb.test(skip=True)
async def test_classifier_on_first_digit(dut):
    image_id = 0
    first_image = x_test[image_id].tolist()
    first_label = y_test[image_id].tolist()

    set_vector(dut.image, first_image)
    await Timer(1, units="ns")

    assert dut.digit.value == first_label


@cocotb.test(skip=False)
async def test_classifier_on_10_digits(dut):
    correct = 0
    for i in range(10):
        image_id = 10 + i
        image = x_test[image_id].tolist()
        label = y_test[image_id].tolist()

        set_vector(dut.image, image)
        await Timer(1, units="ns")

        correct += dut.digit.value == label

        print(f"{i}: {dut.digit.value}/{label} y_pred/y_true")
    assert correct >= 9
