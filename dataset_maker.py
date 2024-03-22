import os
import PIL
import numpy as np
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import Dataset, DataLoader

def load_images_and_labels(parent_folder, target_size=(150,150)):
    """Returns image data in form of a numpy array
    
    args: 
        parent_folder: folder containing classes of images to move through sequentially 
        target_size: size of resulting images in image array
    """
    images = []
    labels = []
    class_mapping = {"beans" : 0, "bell_pepper" : 1, "potato" : 2, "tomato" : 3}

    for class_folder in os.listdir(parent_folder):
        class_path = os.path.join(parent_folder, class_folder)
        if os.path.isdir(class_path) and class_folder in class_mapping:
            label = class_mapping[class_folder]
            for image_file in os.listdir(class_path):
                image_path = os.path.join(class_path, image_file)
                try:
                    image = PIL.Image.open(image_path)
                    if image is not None:
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        image = image.resize(target_size)
                        images.append(image)
                        labels.append(label)
                except Exception as e:
                    print(f'Error reading image {image_path}: {e}')

    return np.array(images), np.array(labels)

def preprocess(images_arr):
    """Preprocess an array of images.

    Args:
        images_arr (numpy.ndarray): Array of images to be preprocessed.

    Returns:
        numpy.ndarray: Preprocessed array of images, pixel values between -1 and 1.
    """
    images_arr = images_arr.astype(np.float32)
    images_arr = images_arr/255.0
    images_arr = (images_arr * 2.0) - 1.0

    return images_arr

def normalization_vals(images_arr):
    """Calculate mean and standard deviation values for normalizing an array of images.

    Args:
        images_arr (numpy.ndarray): Array of images for which to calculate normalization values.

    Returns:
        tuple: A tuple containing the mean and standard deviation values for each channel.
    """
    means = np.mean(images_arr, axis=(0,1,2))
    stds = np.std(images_arr, axis=(0,1,2))
    means = tuple(means)
    stds = tuple(stds)
    return means, stds

class Ingredients(Dataset):
    """Class creating pytorch dataset from images and their labels.

    Args:
        images (list): List of images.
        labels (list): List of corresponding labels.
        transform (callable, optional): Augmentation of the images.

    Attributes:
        images (list): List of images.
        labels (list): List of corresponding labels.
        transform (callable, optional): Augmentation of the images.

    Methods:
        __len__(self): Returns the number of samples in the dataset.
        __getitem__(self, idx): Retrieves the item at the given index.

    """
    def __init__(self, images, labels, transform=None):
        """Initializes the Ingredients dataset.

        Args:
            images (list): List of images.
            labels (list): List of corresponding labels.
            transform (callable, optional): Augmentation of the images.
        """
        self.images = images
        self.labels = labels
        self.transform = transform

    def __len__(self):
        """Returns the number of samples in the dataset.

        Returns:
            int: Number of samples in the dataset.
        """
        return len(self.images)

    def __getitem__(self, idx):
        """Retrieves the item at the given index.

        Args:
            idx (int): Index of the item to retrieve.

        Returns:
            tuple: A tuple containing the image and its corresponding label.
        """
        image = self.images[idx]
        image = PIL.Image.fromarray(image)
        label = self.labels[idx]
        if self.transform:
            image = self.transform(image)
        return image, label