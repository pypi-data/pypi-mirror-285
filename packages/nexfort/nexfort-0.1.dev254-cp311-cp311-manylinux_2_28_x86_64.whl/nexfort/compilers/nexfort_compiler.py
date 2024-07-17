import os

import torch

from nexfort.dynamo.backends.nexfort import nexfort
from nexfort.fx_compiler import apply_mode, apply_options


# This main API is same with torch.compile.
# Reference: https://pytorch.org/docs/stable/generated/torch.compile.html
def nexfort_compile(
    model,
    *,
    fullgraph=False,
    dynamic=None,
    mode="O2",  # default use O2 mode
    options=None,
    disable=False,
    backend="nexfort",
):
    """
    Compile a PyTorch model using NexFort backend.

    Args:
        model (torch.nn.Module): The PyTorch model to be compiled.
        fullgraph (bool, optional): If False (default), torch.compile attempts to discover compileable regions in the function that it will optimize. If True, then we require that the entire function be capturable into a single graph. If this is not possible (that is, if there are graph breaks), then this will raise an error. Defaults to False.
        dynamic (bool, optional): Whether to enable dynamic shape compilation. If None, it checks the environment variable NEXFORT_COMPILE_DYNAMIC. Defaults to None.
        mode (str, optional): The compilation mode. Defaults to "O2". option is the most detailed configuration for the compiler, and a mode is a group of options that are commonly used together.
        options (dict, optional): Additional compilation options. Defaults to None. The options are additional configurations that can be used to further customize the compilation process, ant it will override the options in mode.
        disable (bool, optional): Whether to disable compilation. Defaults to False.
        backend (str, optional): The backend to use for compilation. Defaults to "nexfort".

    Returns:
        Callable: a callable compiled function.
    """
    if dynamic is None:
        dynamic = os.environ.get("NEXFORT_COMPILE_DYNAMIC")
        if dynamic is not None:
            dynamic = dynamic == "1"

    cublaslt_workspace_size = os.environ.get("CUBLASLT_WORKSPACE_SIZE")
    if cublaslt_workspace_size is None:
        from nexfort.utils import checks

        # https://docs.nvidia.com/cuda/cublas/#cublassetworkspace
        if checks.cuda_capability_compare("lt", 9, 0):
            os.environ["CUBLASLT_WORKSPACE_SIZE"] = str(4 * 1024)
        elif checks.cuda_capability_compare("ge", 9, 0):
            os.environ["CUBLASLT_WORKSPACE_SIZE"] = str(32 * 1024)

    # Generate detailed options from mode and options.
    if backend == "nexfort":
        config = {}
        if dynamic is not None:
            config["inductor.dynamic"] = dynamic
        # Set config according to mode.
        apply_mode(config, mode, model=model)
        # Override config according to options.
        apply_options(config, options)
        mode = None
        options = config

    """
    When TorchDynamo compiles a function (or part of one), it makes certain
    assumptions about locals and globals in order to allow compiler
    optimizations, and expresses these assumptions as guards that check
    particular values at runtime. If any of these guards fail, Dynamo will
    recompile that function (or part) up to ``torch._dynamo.config.cache_size_limit`` times.

    To avoid hitting the cache limit, here disable it.
    """
    with torch._dynamo.utils.disable_cache_limit():
        # call torch.compile with nexfort backend.
        model = torch.compile(
            model,
            fullgraph=fullgraph,
            dynamic=dynamic,
            backend=nexfort if backend == "nexfort" else backend,
            mode=mode,
            options=options,
            disable=disable,
        )
    return model
