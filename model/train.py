import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt

def train(model, train_loader, optimizer, device):
    """Train the given model using the provided data loader and optimizer.

    Args:
        model (torch.nn.Module): The model to be trained.
        train_loader (torch.utils.data.DataLoader): DataLoader containing the training data.
        optimizer (torch.optim.Optimizer): The optimizer to update the model's parameters.
        device (torch.device): The device to be used for training (e.g., 'cuda' or 'cpu').

    Returns:
        float: The average loss over all batches for the current epoch.
    """
    epoch_loss = 0.0
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.cross_entropy(output, target, reduction='mean')
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()
    epoch_loss /= len(train_loader)
    return epoch_loss

def val(model, val_loader, device):
    """Validate the given model using the provided data loader.

    Args:
        model (torch.nn.Module): The model to be validated.
        val_loader (torch.utils.data.DataLoader): DataLoader containing the validation data.
        device (torch.device): The device to be used for validation (cuda or cpu).

    Returns:
        float: The loss over one iteration using the trained model.
    """
    model.eval()
    test_loss = 0.0
    with torch.no_grad():
        for batch_idx, (data, target) in enumerate(val_loader):
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.cross_entropy(output, target, reduction='mean')
        test_loss /= len(val_loader)
        return test_loss

def run_epoch(model:torch.nn.Module, train_loader:torch.utils.data.DataLoader, val_loader:torch.utils.data.DataLoader, optimizer, scheduler, epochs:int, early_stop:int, model_save_path:str, device:torch.device, log, loading=False):
    """Run training and validation for the given number of epochs.

    Args:
        model (torch.nn.Module): The model.
        train_loader (torch.utils.data.DataLoader): DataLoader for training data.
        val_loader (torch.utils.data.DataLoader): DataLoader for validation data.
        optimizer: The optimizer to update the model's parameters.
        scheduler: Learning rate scheduler.
        epochs (int): Number of epochs for training.
        early_stop (int): Number of epochs to wait before early stopping if validation loss doesn't improve.
        model_save_path (str): Path to save the best model.
        device (torch.device): Device to be used for training (cuda or cpu).
        log: Logger object for logging.
        loading (bool): Flag indicating whether to load a pre-trained model. Default is False.

    Returns:
        None
    """
    train_losses = []
    val_losses = []
    if loading==True:
        model.load_state_dict(torch.load(model_save_path))
        log.logger.info("-------------Model Loaded------------")
        
    best_loss=0
    #curr_early_stop = early_stop
    model.to(device)
    for epoch in range(epochs):
        train_loss = train(model, train_loader, optimizer, device)
        val_loss = val(model, val_loader, device)
        scheduler.step()
       
        log.logger.info((f"Epoch: {epoch+1} - loss: {train_loss:.10f} - test_loss: {val_loss:.10f}"))

        train_losses.append(train_loss)
        val_losses.append(val_loss)
        
        if epoch == 0:
            best_loss=val_loss
        if val_loss<=best_loss:
            torch.save(model.state_dict(), model_save_path)    
            best_loss=val_loss
            log.logger.info("-------- Save Best Model! --------")
            #curr_early_stop = early_stop
        #else:
            #curr_early_stop-=1
            #log.logger.info("Early Stop Left: {}".format(curr_early_stop))
        #if curr_early_stop == 0:
            #log.logger.info("-------- Early Stop! --------")
            #break
    
    # visualize train and val loss
    train_losses = torch.tensor(train_losses)  
    val_losses = torch.tensor(val_losses)
    plt.plot(train_losses.cpu(), label='Train Loss') 
    plt.plot(val_losses.cpu(), label='Validation Loss')  
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Train and Validation Loss')
    plt.show()