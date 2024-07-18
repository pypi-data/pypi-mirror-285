"""Vanilla Implementation of BitNet1.58"""
import torch.nn as nn
from isobits.torch_bitnet import TorchBitNet


class BitNet1_5(nn.Module):
    """Implementation of BitNet1.5 as described in the paper:
    'BitNet: Scaling 1-bit Transformers for Large Language Models'.

    Args:
        input_dim (int): Dimension of the input features.
        hidden_dim (int): Dimension of the hidden features.
        output_dim (int): Dimension of the output features.
        norm_dim (int): Dimension for normalization in RMSNorm.
        num_layers (int): Number of layers in the network.
    """
    def __init__(self, input_dim, hidden_dim, output_dim, norm_dim,
                 num_layers):
        super(BitNet1_5, self).__init__()
        self.num_layers = num_layers
        self.layers = nn.ModuleList()

        # Input layer
        self.layers.append(TorchBitNet(input_dim, hidden_dim, norm_dim))

        # Hidden layers
        for _ in range(num_layers - 2):
            self.layers.append(TorchBitNet(hidden_dim, hidden_dim, norm_dim))

        # Output layer
        self.layers.append(TorchBitNet(hidden_dim, output_dim, norm_dim))

    def forward(self, x):
        """
        Forward pass for BitNet1.5.

        Args:
            x (Tensor): Input tensor.

        Returns:
            Tensor: Output tensor after passing through BitNet1.5.
        """
        # Convert quantized output back to float for next layer
        for layer in self.layers:
            x = layer(x).float()
        return x
