import cocotb
from util import get_mnist_dataset, wait_clock, set_vector

x_test, y_test = get_mnist_dataset(train=False)
x_test, y_test = x_test.long(), y_test.long()

classifier_latency = 17

@cocotb.test(skip=False)
async def test_classifier_on_first_digit(dut):
    image_id = 8
    first_image = x_test[image_id].tolist()
    first_label = y_test[image_id].tolist()

    set_vector(dut.image, [0] * (28*28))
    await wait_clock(dut, 1)

    set_vector(dut.image, first_image)
    await wait_clock(dut, 1)

    set_vector(dut.image, [0] * (28*28))
    await wait_clock(dut, classifier_latency - 1) 

    assert dut.digit.value == first_label


@cocotb.test(skip=False)
async def test_classifier_on_testset(dut):
    test_count = len(x_test) # 1000
    correct = 0
    set_vector(dut.image, [0] * (28*28))
    await wait_clock(dut, 1)

    for x_image_id in range(test_count + classifier_latency - 1):
        if x_image_id < len(y_test):
            image = x_test[x_image_id].tolist()
            set_vector(dut.image, image)

        await wait_clock(dut, 1)

        if x_image_id >= classifier_latency - 1:
            y_image_id = x_image_id - (classifier_latency - 1)
            label = y_test[y_image_id].tolist()
            y_pred = int(dut.digit.value)
            correct += y_pred == label

            print(f"{y_image_id}: {y_pred}/{label} {"Error" if y_pred != label else ""}")

            if y_image_id % 50 == 0 and y_image_id > 0:
                accuracy = 100 * correct / (y_image_id + 1)
                print(f"{y_image_id}: {accuracy:.2f}% accuracy")

    print("Final Result:")
    accuracy = 100 * correct / test_count
    print(f"Accuracy: {accuracy:.2f}%")
    assert accuracy >= 97.5
