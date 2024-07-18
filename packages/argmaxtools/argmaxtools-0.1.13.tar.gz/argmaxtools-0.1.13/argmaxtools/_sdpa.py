#
# For licensing see accompanying LICENSE.md file.
# Copyright (C) 2023 Argmax, Inc. All Rights Reserved.
#

from abc import ABC, abstractmethod
from beartype import beartype
from typing import Optional
import torch
from argmaxtools import tensor_typing as tt


__all__ = ["Cat", "SplitHeadsQ", "SplitKV"]


@beartype
class SDPAImplementation(ABC):
    """ Abstract base class for the non-parametric Scaled Dot Product Attention (SDPA)
    """
    def __init__(self, embed_dim, n_heads, scale=True):
        """
        Args:
            embed_dim:  The embedding dimensions of the input and output tensors
            n_heads:    The number of attention heads
        """
        assert embed_dim % n_heads == 0
        self.embed_dim = embed_dim
        self.n_heads = n_heads
        self.per_head_dim = self.embed_dim // self.n_heads
        self.qk_denom = self.per_head_dim ** -0.5 if scale else None

    @abstractmethod
    def sdpa(self,
             query: tt.SDPAQueryType,
             key: tt.SDPAKeyType,
             value: tt.SDPAValueType,
             key_padding_mask: tt.SDPAKeyPaddingMaskType,
             causal: bool,
             return_w: bool = False,
             qk_mask: Optional[tt.SDPAQKMaskType] = None,
             ) -> tt.SDPAOutputType:
        pass


class Cat(SDPAImplementation):
    """ Original SDPA
    """
    def sdpa(self, query, key, value, key_padding_mask, causal, return_w=False, qk_mask=None):
        batch_size = query.shape[0]
        bhcx = (batch_size, self.n_heads, self.per_head_dim, -1)

        mh_q = query.view(*bhcx)
        if self.qk_denom is not None:
            mh_q = mh_q * self.qk_denom

        mh_k = key.view(*bhcx)
        mh_w = torch.einsum('bhcq,bhck->bhqk', mh_q, mh_k)

        if key_padding_mask is not None:
            mh_w = mh_w + key_padding_mask[:, None, None, :]

        if causal:
            q_seq_len, k_seq_len = mh_w.shape[-2:]
            assert q_seq_len == k_seq_len

            causal_mask = torch.triu(
                torch.ones(q_seq_len, k_seq_len, device=mh_w.device), 1
            )[None, None, :, :] * -1e4
            mh_w = mh_w + causal_mask

        if qk_mask is not None:
            # If qk_mask is same for all heads, broadcast it
            if len(qk_mask.shape) == 3:
                qk_mask = qk_mask.unsqueeze(1)
            mh_w = mh_w + qk_mask

        mh_w = mh_w.softmax(dim=3)

        mh_v = value.view(*bhcx)
        attn = torch.einsum("bhqk,bhck->bhcq", [mh_w, mh_v])
        attn = attn.reshape(batch_size, self.embed_dim, 1, -1)

        if return_w:
            return attn, mh_w
        return attn


class SplitHeadsQ(SDPAImplementation):
    """ SDPA with explicit multi-head splits and query sequence chunking
    """
    # Runtime configurable
    num_chunks: int = 4
    min_split_seq_len: int = 256

    def sdpa(self, query, key, value, key_padding_mask, causal, return_w=False, qk_mask=None):
        q_seq_length = query.size(3)

        if q_seq_length < self.min_split_seq_len:
            num_chunks = 1
            chunk_size = q_seq_length
        else:
            num_chunks = self.num_chunks
            assert q_seq_length % num_chunks == 0
            chunk_size = q_seq_length // num_chunks

        # Per head query chunk
        mh_q = [
            query[:, head_idx * self.per_head_dim:(head_idx + 1) * self.per_head_dim, :, :]
            for head_idx in range(self.n_heads)
        ]

        # Chunk over sequence length
        mh_q_chunked = [[
            h_q[..., chunk_idx * chunk_size:(chunk_idx + 1) * chunk_size]
            for chunk_idx in range(num_chunks)
        ] for h_q in mh_q]

        k = key.transpose(1, 3)
        mh_k = [
            k[:, :, :, head_idx * self.per_head_dim:(head_idx + 1) * self.per_head_dim]
            for head_idx in range(self.n_heads)
        ]

        mh_v = [
            value[:, head_idx * self.per_head_dim:(head_idx + 1) * self.per_head_dim, :, :]
            for head_idx in range(self.n_heads)
        ]

        mh_w = [[
            torch.einsum("bchq,bkhc->bkhq", [qi_chunk, ki])
            for qi_chunk in h_q_chunked
        ] for h_q_chunked, ki in zip(mh_q_chunked, mh_k)]

        if self.qk_denom is not None:
            mh_w = [[__mh_w * self.qk_denom for __mh_w in _mh_w] for _mh_w in mh_w]

        if key_padding_mask is not None:
            for h in range(self.n_heads):
                for chunk_idx in range(num_chunks):
                    mh_w[h][chunk_idx] = mh_w[h][chunk_idx] + key_padding_mask[:, :, None, None]

        if causal:
            raise NotImplementedError("TODO(atiorh)")

        if qk_mask is not None:
            if len(qk_mask.shape) == 4:
                qk_mask = qk_mask.permute(0, 3, 1, 2)
            elif len(qk_mask.shape) == 3:
                qk_mask = qk_mask.transpose(1, 2)
            else:
                raise ValueError(qk_mask.shape)

            for h in range(self.n_heads):
                for chunk_idx in range(num_chunks):
                    mh_w[h][chunk_idx] = mh_w[h][chunk_idx] + \
                        qk_mask[
                            :,
                            :,
                            None if len(qk_mask.shape) == 3 else h:h+1,
                            chunk_idx*chunk_size:(chunk_idx + 1) * chunk_size
                        ]

        attn_weights = [[
            aw_chunk.softmax(dim=1) for aw_chunk in aw_chunked]
            for aw_chunked in mh_w
        ]

        attn = [[
            torch.einsum("bkhq,bchk->bchq", wi_chunk, vi)
            for wi_chunk in wi_chunked
        ] for wi_chunked, vi in zip(attn_weights, mh_v)]

        attn = torch.cat([
            torch.cat(attn_chunked, dim=3) for attn_chunked in attn
        ], dim=1)

        if return_w:
            return attn, torch.cat([
                torch.cat(_mh_w, dim=1).permute(0, 2, 3, 1) for _mh_w in mh_w
            ], dim=1)  # bkhq -> bhqk
        return attn


# Memory-efficient SDPA with Lazy Softmax from https://arxiv.org/pdf/2112.05682.pdf
class SplitKV(SDPAImplementation):
    # Runtime configurable
    num_chunks: int = 4
    min_split_seq_len: int = 256

    def sdpa(self, query, key, value, key_padding_mask, causal, return_w=False):
        if return_w:
            raise NotImplementedError("TODO(atiorh)")

        # Validate chunkability
        k_seq_len = key.shape[3]

        if k_seq_len < self.min_split_seq_len:
            kv_chunk_size = k_seq_len
        else:
            assert k_seq_len % self.num_chunks == 0
            kv_chunk_size = k_seq_len // self.num_chunks

        # Reshape and scale query
        batch_size = query.shape[0]
        bhcx = (batch_size, self.n_heads, self.per_head_dim, -1)
        mh_q = query.view(*bhcx)
        if self.qk_denom is not None:
            mh_q = mh_q * self.qk_denom

        mh_v = value.view(*bhcx).split(kv_chunk_size, dim=3)

        # Reshape and split key into chunks
        mh_k = key.view(*bhcx).split(kv_chunk_size, dim=3)
        mh_w = [torch.einsum('bhcq,bhck->bhqk', mh_q, ki) for ki in mh_k]

        if key_padding_mask is not None:
            key_padding_masks = key_padding_mask.split(kv_chunk_size, dim=1)
            for i, key_padding_mask_chunk in enumerate(key_padding_masks):
                mh_w[i] = mh_w[i] + key_padding_mask_chunk

        if causal:
            raise NotImplementedError("TODO(atiorh)")

        # Figure 1, Line 14-16
        mh_w_max = [wi.max(dim=3, keepdim=True)[0] for wi in mh_w]
        mh_w_exp = [(wi - wi_max).exp() for wi, wi_max in zip(mh_w, mh_w_max)]
        mh_w_exp_sum = [wi.sum(dim=3, keepdim=True) for wi in mh_w_exp]

        mh_v_exp = [
            torch.einsum("bhqk,bhck->bhcq", [w_exp_i, v_i])
            for w_exp_i, v_i in zip(mh_w_exp, mh_v)
        ]

        # Figure 1, Line 33-36
        mh_w_max_global = torch.cat(mh_w_max, dim=3).max(dim=3, keepdim=True)[0]
        max_diffs = [(wi_max - mh_w_max_global).exp() for wi_max in mh_w_max]
        mh_v_exp = [vi_exp * max_diff for vi_exp, max_diff in zip(mh_v_exp, max_diffs)]
        mh_w_exp_sum = [
            wi_exp_sum * max_diff for wi_exp_sum, max_diff in zip(mh_w_exp_sum, max_diffs)]

        # Figure 1, Line 38-39
        attn = torch.cat(mh_v_exp, dim=3).sum(dim=3) / torch.cat(mh_w_exp_sum, dim=3).sum(dim=3)

        attn = attn.reshape(batch_size, self.embed_dim, 1, -1)

        return attn
