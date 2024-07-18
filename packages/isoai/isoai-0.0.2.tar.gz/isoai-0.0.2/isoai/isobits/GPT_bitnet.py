import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Optional, Tuple
from isobits.torch_bitnet import RMSNorm


def compute_frequency_tensor(dim: int, end: int,
                             theta: float = 10000.0) -> torch.Tensor:
    """Calculate a frequency tensor with complex exponentials.

    Args:
        dim (int): Dimension of the frequency tensor.
        end (int): End index for precomputing frequencies.
        theta (float, optional): Scaling factor for frequency computation.
        Defaults to 10000.0.

    Returns:
        torch.Tensor: Precomputed frequency tensor with complex exponentials.
    """
    # Calculate the frequency values
    freqs = 1.0 / (theta ** (torch.arange(0, dim, 2).float() / dim))

    # Create the time index tensor
    t = torch.arange(end)

    # Outer product to get the frequency matrix
    freqs_matrix = torch.outer(t, freqs)

    # Convert frequency matrix to complex values with module 1 and freqs_matrix
    freqs_complex = torch.polar(torch.ones_like(freqs_matrix), freqs_matrix)

    return freqs_complex


def apply_rotary_embeddings(
    xq: torch.Tensor,
    xk: torch.Tensor,
    freqs_complex: torch.Tensor
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Apply rotary embeddings to query and key tensors using the frequency
    tensor.

    Args:
        xq (torch.Tensor): Query tensor to apply rotary embeddings.
        xk (torch.Tensor): Key tensor to apply rotary embeddings.
        freqs_complex (torch.Tensor): Precomputed frequency tensor for complex
        exponentials.

    Returns:
        Tuple[torch.Tensor, torch.Tensor]: Tuple of modified query tensor and
        key tensor with rotary embeddings.
    """
    # Reshape the input tensors to complex numbers
    xq_complex = torch.view_as_complex(xq.float()
                                       .reshape(*xq.shape[:-1], -1, 2))
    xk_complex = torch.view_as_complex(xk.float()
                                       .reshape(*xk.shape[:-1], -1, 2))

    # Reshape the frequency tensor for broadcasting compatibility
    freqs_complex = reshape_freqs_for_broadcast(freqs_complex, xq_complex)

    # Apply the rotary embeddings
    xq_rotary = torch.view_as_real(xq_complex * freqs_complex).flatten(3)
    xk_rotary = torch.view_as_real(xk_complex * freqs_complex).flatten(3)

    return xq_rotary.type_as(xq), xk_rotary.type_as(xk)


def reshape_freqs_for_broadcast(freqs_complex: torch.Tensor,
                                x: torch.Tensor) -> torch.Tensor:
    """Reshape frequency tensor for broadcasting compatibility with the target
    tensor.

    Args:
        freqs_complex (torch.Tensor): Frequency tensor to be reshaped.
        x (torch.Tensor): Target tensor for broadcasting compatibility.

    Returns:
        torch.Tensor: Reshaped frequency tensor.
    """
    # Get the number of dimensions of the target tensor
    ndim = x.ndim

    # Frequency tensor must have same shape as the target tensor
    shape = [1] * ndim
    shape[1] = x.shape[1]  # Match the second dimension
    shape[-1] = x.shape[-1]  # Match the last dimension

    # Reshape the frequency tensor
    return freqs_complex.view(*shape)


def repeat_key_value_tensor(x: torch.Tensor, n_rep: int) -> torch.Tensor:
    """Repeat the key-value tensor along the specified dimension.

    Args:
        x (torch.Tensor): Input tensor to be repeated.
        n_rep (int): Number of repetitions.

    Returns:
        torch.Tensor: Repeated tensor.
    """
    bs, slen, n_kv_heads, head_dim = x.shape
    if n_rep == 1:
        return x
    return (
        x[:, :, :, None, :]
        .expand(bs, slen, n_kv_heads, n_rep, head_dim)
        .reshape(bs, slen, n_kv_heads * n_rep, head_dim)
    )


class MultiheadAttention(nn.Module):
    """Multi-head attention module incorporating rotary embeddings."""
    def __init__(self, args):
        """
        Initialize the MultiheadAttention module.

        Args:
            args: Model configuration parameters.
        """
        super().__init__()
        self.n_kv_heads = args.n_heads if args.n_kv_heads is None else args.n_kv_heads
        self.n_local_heads = args.n_heads
        self.n_local_kv_heads = self.n_kv_heads
        self.n_rep = self.n_local_heads // self.n_local_kv_heads
        self.head_dim = args.dim // args.n_heads

        self.wq = nn.Linear(args.dim, args.n_heads * self.head_dim, bias=False)
        self.wk = nn.Linear(args.dim, self.n_kv_heads * self.head_dim,
                            bias=False)
        self.wv = nn.Linear(args.dim, self.n_kv_heads * self.head_dim,
                            bias=False)
        self.wo = nn.Linear(args.n_heads * self.head_dim, args.dim,
                            bias=False)

        self.cache_k = torch.zeros(args.max_batch_size, args.max_seq_len,
                                   self.n_local_kv_heads, self.head_dim)
        self.cache_v = torch.zeros(args.max_batch_size, args.max_seq_len,
                                   self.n_local_kv_heads, self.head_dim)

    def forward(
        self,
        x: torch.Tensor,
        start_pos: int,
        freqs_complex: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Forward pass of the MultiheadAttention module.

        Args:
            x (torch.Tensor): Input tensor.
            start_pos (int): Starting position for caching.
            freqs_complex (torch.Tensor): Precomputed frequency tensor.
            mask (torch.Tensor, optional): Attention mask tensor.

        Returns:
            torch.Tensor: Output tensor after attention.
        """
        bsz, seqlen, _ = x.shape
        xq, xk, xv = self.wq(x), self.wk(x), self.wv(x)

        xq = xq.view(bsz, seqlen, self.n_local_heads, self.head_dim)
        xk = xk.view(bsz, seqlen, self.n_local_kv_heads, self.head_dim)
        xv = xv.view(bsz, seqlen, self.n_local_kv_heads, self.head_dim)

        xq, xk = apply_rotary_embeddings(xq, xk, freqs_complex=freqs_complex)

        self.cache_k = self.cache_k.to(xq)
        self.cache_v = self.cache_v.to(xq)

        self.cache_k[:bsz, start_pos: start_pos + seqlen] = xk
        self.cache_v[:bsz, start_pos: start_pos + seqlen] = xv

        keys = self.cache_k[:bsz, : start_pos + seqlen]
        values = self.cache_v[:bsz, : start_pos + seqlen]

        keys = repeat_key_value_tensor(keys, self.n_rep)
        values = repeat_key_value_tensor(values, self.n_rep)

        xq = xq.transpose(1, 2)
        keys = keys.transpose(1, 2)
        values = values.transpose(1, 2)
        scores = torch.matmul(xq, keys.transpose(2, 3)) / math.sqrt(self.head_dim)
        if mask is not None:
            scores = scores + mask
        scores = F.softmax(scores.float(), dim=-1).type_as(xq)
        output = torch.matmul(scores, values)
        output = output.transpose(1, 2).contiguous().view(bsz, seqlen, -1)
        return self.wo(output)

class FeedForward(nn.Module):
    """FeedForward module with custom hidden dimension and optional multiplier."""
    def __init__(
        self,
        dim: int,
        hidden_dim: int,
        multiple_of: int,
        ffn_dim_multiplier: Optional[float] = None,
    ):
        super().__init__()
        hidden_dim = int(2 * hidden_dim / 3)
        if ffn_dim_multiplier is not None:
            hidden_dim = int(ffn_dim_multiplier * hidden_dim)
        hidden_dim = multiple_of * ((hidden_dim + multiple_of - 1) // multiple_of)

        self.w1 = nn.Linear(dim, hidden_dim, bias=False)
        self.w2 = nn.Linear(hidden_dim, dim, bias=False)
        self.w3 = nn.Linear(dim, hidden_dim, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.w2(F.silu(self.w1(x)) * self.w3(x))


class TransformerBlock(nn.Module):
    """Transformer block consisting of attention and feedforward layers with normalization.

    Args:
        layer_id (int): Identifier for the layer.
        args (ModelArgs): Model configuration parameters.
    """
    def __init__(self, layer_id: int, args):
        super().__init__()
        self.attention = MultiheadAttention(args)
        self.feed_forward = FeedForward(
            dim=args.dim,
            hidden_dim=4 * args.dim,
            multiple_of=args.multiple_of,
            ffn_dim_multiplier=args.ffn_dim_multiplier,
        )
        self.layer_id = layer_id
        self.attention_norm = RMSNorm(args.dim, eps=args.norm_eps)
        self.ffn_norm = RMSNorm(args.dim, eps=args.norm_eps)

    def forward(
        self,
        x: torch.Tensor,
        start_pos: int,
        freqs_complex: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Perform a forward pass through the TransformerBlock.

        Args:
            x (torch.Tensor): Input tensor.
            start_pos (int): Starting position for attention caching.
            freqs_complex (torch.Tensor): Precomputed frequency tensor.
            mask (torch.Tensor, optional): Attention mask tensor.

        Returns:
            torch.Tensor: Output tensor after applying attention and feedforward layers.
        """
        h = x + self.attention(self.attention_norm(x), start_pos, freqs_complex, mask)
        return h + self.feed_forward(self.ffn_norm(h))

class Transformer(nn.Module):
    """Transformer model consisting of multiple layers of Transformer blocks.

    Args:
        params (ModelArgs): Model configuration parameters.
    """
    def __init__(self, params):
        super().__init__()
        self.tok_embeddings = nn.Embedding(params.vocab_size, params.dim)
        self.layers = nn.ModuleList([TransformerBlock(layer_id, params) for layer_id in range(params.n_layers)])
        self.norm = RMSNorm(params.dim, eps=params.norm_eps)
        self.output = nn.Linear(params.dim, params.vocab_size, bias=False)
        self.freqs_complex = compute_frequency_tensor(params.dim // params.n_heads, params.max_seq_len * 2)

    @torch.no_grad()
    def forward(self, tokens: torch.Tensor, start_pos: int) -> torch.Tensor:
        """Perform a forward pass through the Transformer model.

        Args:
            tokens (torch.Tensor): Input token indices.
            start_pos (int): Starting position for attention caching.

        Returns:
            torch.Tensor: Output logits after applying the Transformer model.
        """
        bsz, seqlen = tokens.shape
        h = self.tok_embeddings(tokens)
        self.freqs_complex = self.freqs_complex.to(h.device)
        freqs_complex = self.freqs_complex[start_pos : start_pos + seqlen]

        mask = None
        if seqlen > 1:
            mask = torch.full((seqlen, seqlen), float("-inf"), device=tokens.device)
            mask = torch.triu(mask, diagonal=1)
            mask = torch.hstack([torch.zeros((seqlen, start_pos), device=tokens.device), mask]).type_as(h)

        for layer in self.layers:
            h = layer(h, start_pos, freqs_complex, mask)
        h = self.norm(h)
        return self.output(h).float()