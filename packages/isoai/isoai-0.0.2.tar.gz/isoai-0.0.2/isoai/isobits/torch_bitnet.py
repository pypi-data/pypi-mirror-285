"""Pytorch bitnet application.
"""

import torch
import torch.nn as nn


class RMSNorm(nn.Module):
    """Implements Root Mean Square Normalization as proposed in the paper:
    'Root Mean Square Layer Normalization' by Zhang and Sennrich, 2019.

    Args:
        normalized_shape (int): Input shape from an expected input of size
            (batch_size, normalized_shape).
        eps (float, optional): A value added to the denominator for
        numerical stability. Default: 1e-8.
    """
    def __init__(self, normalized_shape, eps=1e-8):
        super(RMSNorm, self).__init__()
        self.normalized_shape = normalized_shape
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(normalized_shape))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass for RMSNorm.

        Args:
            x (Tensor): Input tensor of shape (batch_size, normalized_shape).

        Returns:
            Tensor: Normalized tensor.
        """
        # Compute the root mean square of the input tensor
        rms = torch.sqrt(torch.mean(x**2, dim=-1, keepdim=True) + self.eps)

        # Normalize the input tensor
        x_normalized = x / rms

        # Scale the normalized tensor by the learnable weight
        return self.weight * x_normalized


def per_token_quantization(x: torch.Tensor) -> torch.Tensor:
    """Quantizes input tensor to 8 bits per token.

    Args:
        x (Tensor): Input tensor to be quantized.

    Returns:
        Tensor: Quantized tensor.
    """
    min_val = x.min()
    max_val = x.max()

    scale = (max_val - min_val) / 255.0
    zero_point = min_val

    q_x = ((x - zero_point) / scale).round().clamp(0, 255).to(torch.uint8)

    return q_x


class TorchBitNet(nn.Module):
    """Custom linear layer with RMSNorm and per-token 8-bit quantization.

    Args:
        input_dim (int): Dimension of the input features.
        output_dim (int): Dimension of the output features.
        norm_dim (int): Dimension for normalization.
        epsilon (float, optional): Small value to avoid division by zero in
        RMSNorm. Default is 1e-5.
    """
    def __init__(self, input_dim, output_dim, norm_dim, epsilon=1e-5):
        super(TorchBitNet, self).__init__()
        self.linear = nn.Linear(input_dim, output_dim)
        self.norm = RMSNorm(norm_dim, eps=epsilon)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass for the custom linear layer.

        Args:
            x (Tensor): Input tensor.

        Returns:
            Tensor: Quantized output tensor.
        """
        # Normalize the input
        x = self.norm(x)

        # Apply the linear transformation
        x = self.linear(x)

        # Quantize the output
        x = per_token_quantization(x)

        return x
