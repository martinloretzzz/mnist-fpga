import torch
import torchvision
import numpy as np

torch.manual_seed(42)
torch.set_printoptions(linewidth=200)

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
