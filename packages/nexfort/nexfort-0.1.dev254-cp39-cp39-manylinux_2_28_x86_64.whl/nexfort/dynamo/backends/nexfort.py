from typing import Any, Dict, List, Optional

import torch
from torch._dynamo.backends.registry import register_backend

import nexfort as nexfort_lib
from nexfort.fx_compiler import compile_fx
from nexfort.utils.logging import logger


# Register nexfort backend to torch.compile so it can be called like `torch.compile(model, backend="nexfort")`.
# Reference: https://pytorch.org/docs/stable/torch.compiler_custom_backends.html
@register_backend
def nexfort(
    gm: torch.fx.GraphModule,
    example_inputs: List[torch.Tensor],
    mode: Optional[str] = None,
    options: Dict[str, Any] = None,
):
    """
    Compile a TorchScript graph module using the Nexfort backend.

    Args:
        gm (torch.fx.GraphModule): The input TorchScript graph module to compile.
        example_inputs (List[torch.Tensor]): List of example input tensors used for tracing the graph module.
        mode (Optional[str]): The compilation mode. Defaults to None.
        options (Dict[str, Any]): Additional options for the compilation. Defaults to None.

    Returns:
        Callable: a callable compiled function.

    """
    # nexfort backend is just compile_fx for now.
    out = compile_fx(gm, example_inputs, mode=mode, options=options)

    if nexfort_lib._nexfort_debug_level >= 1:
        logger.vinfo1(torch._dynamo.utils.compile_times(repr="str", aggregate=False))
    return out
