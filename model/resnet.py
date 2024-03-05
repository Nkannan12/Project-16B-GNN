"""Paper outlining architecture
    https://arxiv.org/abs/1512.03385v1
"""

import torch
import torch.nn as nn

DIM=64

class BasicBlock(nn.Module):
    """Basic Block for resnet 18 and resnet 34

    """

    # BasicBlock for smaller models, BottleNeck block is for the big boys
    expansion = 1

    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()

        # actual residual function
        self.residual_function = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels * BasicBlock.expansion, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels * BasicBlock.expansion)
        )

        # shortcut function
        self.shortcut = nn.Sequential()

        if stride != 1 or in_channels != BasicBlock.expansion * out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels * BasicBlock.expansion, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels * BasicBlock.expansion)
            )

    def forward(self, x):
        return nn.ReLU(inplace=True)(self.residual_function(x) + self.shortcut(x))

class BottleNeck(nn.Module):
    """Residual block for resnet over 50 layers

    """
    expansion = 4
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.residual_function = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, stride=stride, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels * BottleNeck.expansion, kernel_size=1, bias=False),
            nn.BatchNorm2d(out_channels * BottleNeck.expansion),
        )

        self.shortcut = nn.Sequential()

        if stride != 1 or in_channels != out_channels * BottleNeck.expansion:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels * BottleNeck.expansion, stride=stride, kernel_size=1, bias=False),
                nn.BatchNorm2d(out_channels * BottleNeck.expansion)
            )

    def forward(self, x):
        return nn.ReLU(inplace=True)(self.residual_function(x) + self.shortcut(x))

class ResNet(nn.Module):

    def __init__(self, block, num_block, num_classes=100,num_channel=3):
        super().__init__()

        self.in_channels = DIM

        if num_classes == 1000:
            self.conv1 = nn.Sequential(
                nn.Conv2d(num_channel, DIM, kernel_size=7, stride=2, padding=3, bias=False),
                nn.BatchNorm2d(DIM),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
            )
        else:
            self.conv1 = nn.Sequential(
                nn.Conv2d(num_channel, DIM, kernel_size=3, padding=1, bias=False),
                nn.BatchNorm2d(DIM),
                nn.ReLU(inplace=True))
        self.conv2_x = self._make_layer(block, DIM, num_block[0], 1)
        self.conv3_x = self._make_layer(block, DIM*2, num_block[1], 2)
        self.conv4_x = self._make_layer(block, DIM*4, num_block[2], 2)
        self.conv5_x = self._make_layer(block, DIM*8, num_block[3], 2)
        self.avg_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(DIM*8 * block.expansion, num_classes)
        self.sigmoid = nn.Sigmoid()

    def _make_layer(self, block, out_channels, num_blocks, stride):
        """makes resnet layers from residual blocks

        Args:
            block: basic block or bottle neck block
            out_channels: number of channels in ouput of this layer
            num_blocks: number of blocks per layer
            stride: the stride of the first block in the layer

        Return:
            returns a resnet layer
        """

        strides = [stride] + [1] * (num_blocks - 1)
        layers = []
        for stride in strides:
            layers.append(block(self.in_channels, out_channels, stride))
            self.in_channels = out_channels * block.expansion

        return nn.Sequential(*layers)

    def forward(self, x):
        output = self.conv1(x)
        output = self.conv2_x(output)
        output = self.conv3_x(output)
        output = self.conv4_x(output)
        output = self.conv5_x(output)
        output = self.avg_pool(output)
        output = output.view(output.size(0), -1)
        output = self.fc(output)

        return self.sigmoid(output)

class ResNet_tiny(nn.Module):

    def __init__(self, block, num_block, num_classes=100,num_channel=3):
        super().__init__()

        self.in_channels = DIM

        self.conv1 = nn.Sequential(
            nn.Conv2d(num_channel, DIM, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(DIM),
            nn.ReLU(inplace=True))
        self.conv2_x = self._make_layer(block, DIM, num_block[0], 1)
        self.conv3_x = self._make_layer(block, DIM*2, num_block[1], 2)
        self.conv4_x = self._make_layer(block, DIM*4, num_block[2], 2)
        self.avg_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(DIM*4 * block.expansion, num_classes)
        self.sigmoid = nn.Sigmoid()

    def _make_layer(self, block, out_channels, num_blocks, stride):
        """makes resnet layers from residual blocks

        Args:
            block: basic block or bottle neck block
            out_channels: number of channels in ouput of this layer
            num_blocks: number of blocks per layer
            stride: the stride of the first block in the layer

        Return:
            returns a resnet layer
        """

        # the first block can be 1 or 2, other blocks are always 1
        strides = [stride] + [1] * (num_blocks - 1)
        layers = []
        for stride in strides:
            layers.append(block(self.in_channels, out_channels, stride))
            self.in_channels = out_channels * block.expansion

        return nn.Sequential(*layers)

    def forward(self, x):
        output = self.conv1(x)
        output = self.conv2_x(output)
        output = self.conv3_x(output)
        output = self.conv4_x(output)
        output = self.avg_pool(output)
        output = output.view(output.size(0), -1)
        output = self.fc(output)

        return self.sigmoid(output)


def resnet14(num_classes,num_channel):
    """ returns a ResNet 14 object
    """
    return ResNet(BasicBlock, [1, 1, 1, 1],num_classes,num_channel)


def resnet18(num_classes,num_channel):
    """ returns a ResNet 18 object
    """
    return ResNet(BasicBlock, [2, 2, 2, 2],num_classes,num_channel)

def resnet34(num_classes,num_channel):
    """ returns a ResNet 34 object
    """
    return ResNet(BasicBlock, [3, 4, 6, 3],num_classes,num_channel)

def resnet50(num_classes,num_channel):
    """ returns a ResNet 50 object
    """
    return ResNet(BottleNeck, [3, 4, 6, 3],num_classes,num_channel)

def resnet101(num_classes,num_channel):
    """ returns a ResNet 101 object
    """
    return ResNet(BottleNeck, [3, 4, 23, 3],num_classes,num_channel)

def resnet152(num_classes,num_channel):
    """ returns a ResNet 152 object
    """
    return ResNet(BottleNeck, [3, 8, 36, 3],num_classes,num_channel)
