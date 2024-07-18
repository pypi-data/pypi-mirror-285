"""Test iso."""
import unittest
import torch
from isoai.model import (
    RMSNorm, compute_frequency_tensor, reshape_freqs_for_broadcast,
    apply_rotary_embeddings, repeat_key_value_tensor, MultiheadAttention,
    FeedForward, TransformerBlock, GatingMechanism, MoETransformerBlock, MoETransformer
)

class TestModel(unittest.TestCase):
    
    def setUp(self):
        # Setting up common test data
        self.args = type('', (), {})()  # Mock object for arguments
        self.args.vocab_size = 30522
        self.args.dim = 768
        self.args.n_heads = 12
        self.args.n_kv_heads = 12
        self.args.max_seq_len = 512
        self.args.norm_eps = 1e-5
        self.args.multiple_of = 64
        self.args.ffn_dim_multiplier = 4
        self.args.max_batch_size = 32
        self.args.num_experts = 4
        
        self.tokens = torch.randint(0, self.args.vocab_size, (2, self.args.max_seq_len)).cuda()
        self.freqs_cis = compute_frequency_tensor(self.args.dim // self.args.n_heads, self.args.max_seq_len * 2)

    def test_rmsnorm(self):
        rmsnorm = RMSNorm(self.args.dim)
        x = torch.randn(2, self.args.max_seq_len, self.args.dim).cuda()
        output = rmsnorm(x)
        self.assertEqual(output.shape, x.shape)

    def test_compute_frequency_tensor(self):
        freqs_cis = compute_frequency_tensor(8, 10)
        self.assertEqual(freqs_cis.shape, (10, 4))

    def test_reshape_freqs_for_broadcast(self):
        x = torch.randn(4, 10, 16)
        freqs_complex = torch.randn(10, 8, dtype=torch.complex64)
        reshaped_freqs = reshape_freqs_for_broadcast(freqs_complex, x)
        self.assertEqual(reshaped_freqs.shape, (1, 10, 1, 8))

    def test_apply_rotary_embeddings(self):
        xq = torch.randn(4, 10, 16)
        xk = torch.randn(4, 10, 16)
        xq_rotary, xk_rotary = apply_rotary_embeddings(xq, xk, self.freqs_cis)
        self.assertEqual(xq_rotary.shape, xq.shape)
        self.assertEqual(xk_rotary.shape, xk.shape)

    def test_repeat_key_value_tensor(self):
        x = torch.randn(4, 10, 8, 16)
        repeated_tensor = repeat_key_value_tensor(x, 2)
        self.assertEqual(repeated_tensor.shape, (4, 10, 16, 16))

    def test_multihead_attention(self):
        multihead_attention = MultiheadAttention(self.args)
        x = torch.randn(2, 10, self.args.dim).cuda()
        output = multihead_attention(x, start_pos=0, freqs_cis=self.freqs_cis)
        self.assertEqual(output.shape, x.shape)

    def test_feed_forward(self):
        feed_forward = FeedForward(
            dim=self.args.dim,
            hidden_dim=4 * self.args.dim,
            multiple_of=self.args.multiple_of,
            ffn_dim_multiplier=self.args.ffn_dim_multiplier
        )
        x = torch.randn(2, self.args.dim).cuda()
        output = feed_forward(x)
        self.assertEqual(output.shape, x.shape)

    def test_transformer_block(self):
        transformer_block = TransformerBlock(layer_id=0, args=self.args)
        x = torch.randn(2, 10, self.args.dim).cuda()
        output = transformer_block(x, start_pos=0, freqs_cis=self.freqs_cis)
        self.assertEqual(output.shape, x.shape)

    def test_gating_mechanism(self):
        gating = GatingMechanism(input_dim=self.args.dim, num_experts=self.args.num_experts)
        x = torch.randn(2, self.args.dim).cuda()
        gate_values = gating(x)
        self.assertEqual(gate_values.shape, (2, self.args.num_experts))

    def test_moe_transformer_block(self):
        moe_block = MoETransformerBlock(layer_id=0, args=self.args)
        x = torch.randn(2, 10, self.args.dim).cuda()
        output = moe_block(x, start_pos=0, freqs_cis=self.freqs_cis)
        self.assertEqual(output.shape, x.shape)

    def test_moe_transformer(self):
        moe_transformer = MoETransformer(self.args)
        output = moe_transformer(self.tokens, start_pos=0)
        self.assertEqual(output.shape, (2, self.args.max_seq_len, self.args.vocab_size))

if __name__ == '__main__':
    unittest.main()
