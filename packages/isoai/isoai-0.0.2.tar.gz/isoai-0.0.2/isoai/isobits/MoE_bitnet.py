"""Apply bitnet to MoE"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional


class GatingMechanism(nn.Module):
    """Gating mechanism to route inputs to experts."""
    def __init__(self, input_dim: int, num_experts: int):
        super().__init__()
        self.num_experts = num_experts
        self.gate = nn.Linear(input_dim, num_experts)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass of the gating mechanism."""
        logits = self.gate(x)
        gate_values = F.softmax(logits, dim=-1)
        return gate_values

class MoETransformerBlock(nn.Module):
    """Mixture of Experts Transformer Block."""
    def __init__(self, layer_id: int, args):
        super().__init__()
        self.num_experts = args.num_experts
        self.experts = nn.ModuleList([TransformerBlock(layer_id, args) for _ in range(self.num_experts)])
        self.gate = GatingMechanism(args.dim, self.num_experts)
        self.layer_id = layer_id

    def forward(self, x: torch.Tensor, start_pos: int, freqs_cis: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass through the MoE Transformer block."""
        gate_values = self.gate(x)  # Shape: [batch_size, seqlen, num_experts]
        expert_outputs = torch.stack([expert(x, start_pos, freqs_cis, mask) for expert in self.experts], dim=-1)  # Shape: [batch_size, seqlen, dim, num_experts]
        weighted_expert_output = torch.einsum('bte,btde->btd', gate_values, expert_outputs)  # Adjusted einsum equation
        return weighted_expert_output

class MoETransformer(nn.Module):
    """Mixture of Experts Transformer model with BitNet-enhanced LLAMA architecture."""
    def __init__(self, params):
        super().__init__()
        self.tok_embeddings = nn.Embedding(params.vocab_size, params.dim)
        self.layers = nn.ModuleList([MoETransformerBlock(layer_id, params) if layer_id % 2 == 0 else TransformerBlock(layer_id, params) for layer_id in range(params.n_layers)])
        self.norm = RMSNorm(params.dim, eps=params.norm_eps)
        self.output = nn.Linear(params.dim, params.vocab_size, bias=False)
        self.freqs_cis = compute_frequency_tensor(params.dim // params.n_heads, params.max_seq_len * 2)

    @torch.no_grad()
    def forward(self, tokens: torch.Tensor, start_pos: int) -> torch.Tensor:
        """Forward pass through the MoE Transformer model."""
        bsz, seqlen = tokens.shape
        h = self.tok_embeddings(tokens)
        self.freqs_cis = self.freqs_cis
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






