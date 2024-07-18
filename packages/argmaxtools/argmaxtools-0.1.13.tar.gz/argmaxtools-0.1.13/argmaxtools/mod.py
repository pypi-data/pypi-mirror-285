#
# For licensing see accompanying LICENSE.md file.
# Copyright (C) 2023 Argmax, Inc. All Rights Reserved.
#
import torch
import torch.nn as nn

from argmaxtools import nn as agx
from argmaxtools.utils import get_logger


logger = get_logger(__name__)

# TODO(atiorh): Implement separate routers for kv and q for EncoderDecoderCrossAttention and KVCached*Attention
# TODO(atiorh): Implement causal routing (sort to ensure causal order)
SUPPORTED_ATTENTION_TYPES = [agx.AttentionType.SelfAttention]


class MoDAttention(agx.Attention):
    """ Mixture-of-Depths Attention [1]

    [1] https://arxiv.org/pdf/2404.02258
    """
    def __init__(self, capacity: float, embed_dim: int, *args, **kwargs) -> None:
        super().__init__(embed_dim, *args, **kwargs)
        self.mod_router = nn.Conv2d(embed_dim, 1, kernel_size=1, bias=False)
        nn.init.trunc_normal_(self.mod_router.weight, std=0.02)

        assert self.attention_type in SUPPORTED_ATTENTION_TYPES
        assert capacity <= 1. and capacity > 0.
        self.capacity = capacity
        logger.info(
            f"Initialized {self.__class__.__name__} with capacity: {self.capacity}")

        # TODO(atiorh)
        self.multiply_by_score = False

    @classmethod
    def from_attention(cls, attention: agx.Attention, capacity: float):
        """ Initialize MoDAttention from an existing Attention module
        """
        assert capacity <= 1. and capacity > 0.
        assert attention.attention_type in SUPPORTED_ATTENTION_TYPES

        mod_attention = cls(capacity,
                            attention.embed_dim,
                            attention.n_heads,
                            attention.attention_type,
                            attention.n_kv_heads)
        # FIXME(atiorh): Only allow mod_router to be missing
        mod_attention.load_state_dict(attention.state_dict(), strict=False)
        return mod_attention

    def forward(self, input_embeds, *args, **kwargs):
        assert not args
        assert not kwargs
        assert input_embeds.shape[0] == 1

        num_tokens = input_embeds.shape[-1]
        num_routed_tokens = int(num_tokens * self.capacity)

        # Separate sequence into routed and bypassed tokens
        descending_scores, descending_inds = self.mod_router(input_embeds).sort(dim=-1)
        routed_inds = descending_inds.squeeze()[:num_routed_tokens]
        bypass_inds = descending_inds.squeeze()[num_routed_tokens:]

        routed_tokens = super().forward(input_embeds[..., routed_inds])[0]
        if self.multiply_by_score:
            routed_scores = descending_scores[:num_routed_tokens]
            routed_tokens = routed_tokens * routed_scores

        bypassed_tokens = input_embeds[..., bypass_inds]

        return torch.cat([routed_tokens, bypassed_tokens], dim=-1)
