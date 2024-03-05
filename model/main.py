import torch
import torch.optim as optim
# from torchinfo import summary

from logger import Logger
from train import run_epoch
from resnet import resnet14, resnet18, resnet34, resnet50
from data_loader import get_data
from test import run_test

torch.manual_seed(0)

EPOCHS = 100
EARLY_STOP = 5
LR = 0.1
MOMENTUM = 0.9
WEIGHT_DECAY = 0.0005 # 0.0005 test
VAL_SPLIT = 0.1

model_save_path = f'./model_logs/Ingredients1'

log = Logger()
log.set_logger(f'{model_save_path}.log')

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
train_loader, val_loader, test_loader, num_classes, num_channels = get_data(VAL_SPLIT)
model = resnet18(num_classes, num_channels)
optimizer = optim.SGD(model.parameters(), LR, MOMENTUM, weight_decay=WEIGHT_DECAY)
# scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=200)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=20, gamma=0.1)

run_epoch(model, train_loader, val_loader, optimizer, scheduler, EPOCHS, EARLY_STOP, f'{model_save_path}.pth', device, log)
accuracy = run_test(model, test_loader, device, f"{model_save_path}.pth")
log.logger.info("Accuracy: {:.10f}".format(accuracy))