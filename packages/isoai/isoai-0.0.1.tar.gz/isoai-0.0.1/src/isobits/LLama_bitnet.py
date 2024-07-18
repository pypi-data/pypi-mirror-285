"""Apply bitnet to LLAMA"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple
from isobits.torch_bitnet import RMSNorm
from isobits.GPT_bitnet import compute_frequency_tensor
from isobits.GPT_bitnet import TransformerBlock

class BitNetLLAMA(nn.Module):
    """BitNet applied to a LLAMA model."""
    def __init__(self, params):
        super().__init__()
        self.tok_embeddings = nn.Embedding(params.vocab_size, params.dim)
        self.layers = nn.ModuleList([TransformerBlock(layer_id, params) for layer_id in range(params.n_layers)])
        self.norm = RMSNorm(params.dim, eps=params.norm_eps)
        self.output = nn.Linear(params.dim, params.vocab_size, bias=False)
        self.freqs_cis = compute_frequency_tensor(params.dim // params.n_heads, params.max_seq_len * 2)

    @torch.no_grad()
    def forward(self, tokens: torch.Tensor, start_pos: int) -> torch.Tensor:
        """Perform a forward pass through the BitNetLLAMA model.

        Args:
            tokens (torch.Tensor): Input token indices.
            start_pos (int): Starting position for attention caching.

        Returns:
            torch.Tensor: Output logits after applying the BitNetLLAMA model.
        """
        bsz, seqlen = tokens.shape
        h = self.tok_embeddings(tokens)
        self.freqs_cis = self.freqs_cis.to(h.device)
        freqs_cis = self.freqs_cis[start_pos : start_pos + seqlen]

        mask = None
        if seqlen > 1:
            mask = torch.full((seqlen, seqlen), float("-inf"), device=tokens.device)
            mask = torch.triu(mask, diagonal=1)
            mask = torch.hstack([torch.zeros((seqlen, start_pos), device=tokens.device), mask]).type_as(h)

        for layer in self.layers:
            h = layer(h, start_pos, freqs_cis, mask)
        h = self.norm(h)
        return self.output(h).float()

