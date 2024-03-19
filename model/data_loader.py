import torch
from torch.utils.data import DataLoader, SubsetRandomSampler
from torchvision import transforms
from dataset_maker import load_images_and_labels, preprocess, Ingredients
import numpy as np

def get_data(val_split=0.5):
    """
    Prepares DataLoader instances for training, validation, and testing splits of an image dataset.
    
    Parameters:
    - val_split (float, optional): Proportion of the training set to use for validation. Default is 0.5.

    Returns:
    - Tuple[DataLoader, DataLoader, DataLoader, int, int]: A tuple containing DataLoader instances for the 
      training, validation, and test datasets, the number of unique labels in the dataset, and the number 3, 
      whose specific meaning may depend on context (e.g., number of color channels).
    """
    parent_folder = "/content/drive/MyDrive/proj_files/ingredients/ingredients"
    images, labels = load_images_and_labels(parent_folder)
    preprocess(images)
    transform = transforms.Compose([
        transforms.RandomHorizontalFlip(),
        transforms.RandomResizedCrop(32),
        transforms.ToTensor(),
        transforms.Normalize((0.38046584, 0.10854615, -0.13485776), (0.5249659, 0.59474176, 0.6634378))
    ])

    dataset = Ingredients(images, labels, transform)
        
    batch_size = 64 # change to appropriate value for dataset in use

    dataset_size = len(dataset)
    indices = list(range(dataset_size))
    train_test_split = int(np.floor(0.8 * dataset_size))
    train_val_split = int(np.floor(val_split * dataset_size))

    np.random.shuffle(indices)

    train_idx, test_idx = indices[train_test_split:], indices[:train_test_split]
    val_idx = train_idx[:train_val_split]

    train_loader = DataLoader(dataset,
                              batch_size=batch_size,
                              sampler=SubsetRandomSampler(train_idx),
                              num_workers=4) 
    
    test_loader = DataLoader(dataset,
                             batch_size=batch_size,
                             sampler=SubsetRandomSampler(test_idx),
                             num_workers=4) 

    val_loader = DataLoader(dataset,
                            batch_size=batch_size,
                            sampler=SubsetRandomSampler(val_idx),
                            num_workers=4) 
    
    return train_loader, val_loader, test_loader, len(np.unique(labels)), 3

