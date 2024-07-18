"""Quantize Huggingface models with BitNet."""

import torch.nn as nn
from isobits.torch_bitnet import TorchBitNet


def replace_linears_with_torchbitnet(model, norm_dim):
    """Replace all nn.Linear layers in the given model with TorchBitNet layers.

    Args:
        model (nn.Module): The PyTorch model in which to replace the layers.
        norm_dim (int): Dimension for normalization in TorchBitNet.
    """
    for name, module in model.named_children():
        if isinstance(module, nn.Linear):
            in_features = module.in_features
            out_features = module.out_features

            setattr(
                model,
                name,
                TorchBitNet(
                    input_dim=in_features,
                    output_dim=out_features,
                    norm_dim=norm_dim,
                )
            )
        else:
            # Recursively apply to child modules
            replace_linears_with_torchbitnet(module, norm_dim)
