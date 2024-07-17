from typing import List

import torch
import torch_npu

# from nexfort.utils.fx_passes import replace_pattern_with_filters

aten = torch.ops.aten


def fx_pass_fuse_group_norm(gm: torch.fx.GraphModule, example_inputs: List[torch.Tensor]) -> torch.fx.GraphModule:
    for act, fused_op in [(aten.silu.default, torch_npu.npu_group_norm_silu)]:

        def pattern0(x: torch.Tensor, num_groups: int):
            y = aten.group_norm.default(x, num_groups)
            out = act(y)
            return out

        def pattern1(x: torch.Tensor, weight: torch.Tensor, bias: torch.Tensor, num_groups: int):
            y = aten.group_norm.default(x, num_groups, weight, bias)
            out = act(y)
            return out

        def replacement0(x: torch.Tensor, num_groups: int):
            return fused_op(x, weight=None, bias=None, group=num_groups)[0]

        def replacement1(x: torch.Tensor, weight: torch.Tensor, bias: torch.Tensor, num_groups: int):
            return fused_op(x, weight=weight, bias=bias, group=num_groups)[0]

        # TODO(): torch_npu.npu_group_norm_silu leads to wrong results
        # gm = replace_pattern_with_filters(gm, pattern0, replacement0, match_filters=[], name="fuse_group_norm")
        # gm = replace_pattern_with_filters(gm, pattern1, replacement1, match_filters=[], name="fuse_group_norm")

    return gm
