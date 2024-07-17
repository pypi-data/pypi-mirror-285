import importlib

if importlib.util.find_spec("torchao") is None:
    raise ImportError("torchao not found. Please install it by `pip3 install torchao`")

from torch._inductor import utils as inductor_utils

if not hasattr(inductor_utils, "do_bench"):
    # ImportError: cannot import name 'do_bench' from 'torch._inductor.utils'
    try:
        from torch._inductor.runtime.runtime_utils import do_bench
    except ImportError:
        do_bench = None

    if do_bench is not None:
        inductor_utils.do_bench = do_bench

from .quant import is_quantized_module, quantize
