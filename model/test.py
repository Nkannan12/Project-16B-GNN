import torch
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

def run_test(model, test_loader, device, model_save_path):
    """Run testing on the test data using the trained model.

    Args:
        model (torch.nn.Module): The trained model.
        test_loader (torch.utils.data.DataLoader): DataLoader containing the test data.
        device (torch.device): The device to be used for testing (cuda or cpu).
        model_save_path (str): Path to the saved model.

    Returns:
        float: Accuracy achieved by the model on the test data.
    """
    model.load_state_dict(torch.load(model_save_path))
    model.to(device)
    model.eval()

    all_labels = []
    all_predictions = []

    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predictions = torch.max(outputs, 1)
            all_labels.extend(labels.cpu().numpy())
            all_predictions.extend(predictions.cpu().numpy())

    accuracy = accuracy_score(all_labels, all_predictions)

    return accuracy
