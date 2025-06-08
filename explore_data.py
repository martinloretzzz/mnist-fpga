# Import libraries
import torch
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

# Set random seed
torch.manual_seed(42)

# Check device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Using device: {device}')

# Define transformation
transform = transforms.ToTensor()

# Load MNIST datasets
trainset = torchvision.datasets.MNIST(root='../data', train=True, download=True, transform=transform)
testset = torchvision.datasets.MNIST(root='../data', train=False, download=True, transform=transform)

# Create data loaders
trainloader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True)
testloader = torch.utils.data.DataLoader(testset, batch_size=64, shuffle=False)

# Dataset sizes
print(f'Training set size: {len(trainset)}')
print(f'Test set size: {len(testset)}')


full_dataset = trainset.data.float() / 255.0
fd_binary = torch.where(full_dataset > 0.5, 1.0, 0.0)
fd_flat = fd_binary.view(-1, 28 * 28)
fd_zero_count = (fd_flat == 0).sum(dim=0)

treshhold = 0.0005
fd_unused_pixel_count = (len(trainset) - fd_zero_count) / len(trainset)
unused_pixel_mask = (fd_unused_pixel_count <= treshhold)
fd_unused_pixel = fd_unused_pixel_count[unused_pixel_mask]
fd_unused_percent = len(fd_unused_pixel) / (28*28)
print(f'Unused pixels in train dataset: {len(fd_unused_pixel)} ({fd_unused_percent:.2%})')

torch.save(unused_pixel_mask, "mnist_unused_mask.pth")

unused_pixel_image = unused_pixel_mask.float().view(28, 28) 
plt.figure(figsize=(6, 6))
plt.imshow(unused_pixel_image, cmap='binary', interpolation='nearest')
plt.title(f'MNIST Unused (>{treshhold} active) Pixels ({len(fd_unused_pixel)} pixels, {fd_unused_percent:.2f}%)')
plt.axis('off')  # Hide axes for clarity
plt.savefig('mnist_unused_pixels.png')
plt.show()


# Class distribution
train_labels = [label for _, label in trainset]
test_labels = [label for _, label in testset]
train_counts = Counter(train_labels)
test_counts = Counter(test_labels)
print('Training set class distribution:', dict(train_counts))
print('Test set class distribution:', dict(test_counts))

# Visualize sample images
def imshow(img):
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)), cmap='gray')
    plt.axis('off')

# Get some random training images
images, labels = next(iter(trainloader))
fig = plt.figure(figsize=(10, 8))
for i in range(8):
    plt.subplot(4, 4, 2 * i + 1)
    imshow(images[i])
    plt.title(f'Label: {labels[i].item()}')

    plt.subplot(4, 4, 2 * i + 2)
    imshow(torch.where(images[i] > 0.5, 1.0, 0.0))
    plt.title(f'Label: {labels[i].item()}')
plt.tight_layout()
plt.show()


# Pixel value distribution
all_pixels = torch.cat([img.flatten() for img, _ in trainset]).numpy()
plt.figure(figsize=(8, 6))
plt.hist(all_pixels, bins=50, density=True)
plt.title('Pixel Value Distribution in Training Set')
plt.xlabel('Pixel Value')
plt.ylabel('Density')
plt.show()

# Basic statistics
pixel_mean = all_pixels.mean()
pixel_std = all_pixels.std()
print(f'Pixel Mean: {pixel_mean:.4f}')
print(f'Pixel Std: {pixel_std:.4f}')