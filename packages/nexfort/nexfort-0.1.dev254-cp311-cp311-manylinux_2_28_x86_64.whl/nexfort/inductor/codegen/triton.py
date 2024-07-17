import contextlib
import unittest

from nexfort.utils import checks
from nexfort.utils.logging import logger

from torch._inductor.codegen.triton import TritonOverrides

from ..utils import has_triton_language


@staticmethod
def neg_ftz(x):
    return f"nexfort_triton_helpers.neg_ftz({x})"


@staticmethod
def abs_ftz(x):
    return f"nexfort_triton_helpers.abs_ftz({x})"


@staticmethod
def add_ftz(a, b):
    return f"nexfort_triton_helpers.add_ftz({a}, {b})"


@staticmethod
def sub_ftz(a, b):
    return f"nexfort_triton_helpers.sub_ftz({a}, {b})"


@staticmethod
def mul_ftz(a, b):
    return f"nexfort_triton_helpers.mul_ftz({a}, {b})"


@staticmethod
def truediv_approx_ftz(a, b):
    return f"nexfort_triton_helpers.truediv_approx_ftz({a}, {b})"


@staticmethod
def minimum_ftz(a, b):
    return f"nexfort_triton_helpers.minimum_ftz({a}, {b})"


@staticmethod
def maximum_ftz(a, b):
    return f"nexfort_triton_helpers.maximum_ftz({a}, {b})"


@staticmethod
def tanh_approx(x):
    return f"nexfort_triton_helpers.tanh_approx({x})"


@staticmethod
def sqrt_approx_ftz(x):
    return f"nexfort_triton_helpers.sqrt_approx_ftz({x})"


@staticmethod
def rsqrt_approx_ftz(x):
    return f"nexfort_triton_helpers.rsqrt_approx_ftz({x})"


@staticmethod
def sin_approx_ftz(x):
    return f"nexfort_triton_helpers.sin_approx_ftz({x})"


@staticmethod
def cos_approx_ftz(x):
    return f"nexfort_triton_helpers.cos_approx_ftz({x})"


@contextlib.contextmanager
def patch_triton_overrides(method_name, replacement):
    if isinstance(replacement, str):
        replacement = eval(replacement)
    with unittest.mock.patch.object(TritonOverrides, method_name, replacement, create=True):
        yield


@contextlib.contextmanager
def patch_multiple_triton_overrides(replacements):
    with contextlib.ExitStack() as stack:
        for method_name, replacement in replacements.items():
            stack.enter_context(patch_triton_overrides(method_name, replacement))
        yield


@contextlib.contextmanager
def patch_fast_math_triton_overrides(enabled=True):
    if not enabled:
        yield
        return
    from torch._inductor import select_algorithm
    from torch._inductor.codegen import triton as codegen_triton

    if not hasattr(codegen_triton, "gen_common_triton_imports"):
        logger.warning(
            "Fast math is enabled but codegen_triton.gen_common_triton_imports is not available, consider switching to PyTorch>=2.3.0 for better performance"
        )
        yield
        return
    if not hasattr(select_algorithm, "gen_common_triton_imports"):
        logger.warning(
            "Fast math is enabled but select_algorithm.gen_common_triton_imports is not available, consider switching to PyTorch>=2.3.0 for better performance"
        )
        yield
        return

    gen_common_triton_imports = codegen_triton.gen_common_triton_imports

    def gen_common_triton_imports_(*args, **kwargs):
        return """
import nexfort.inductor.runtime.triton_helpers as nexfort_triton_helpers
""" + gen_common_triton_imports(
            *args, **kwargs
        )

    replacements = {}
    if has_triton_language("inline_asm_elementwise"):
        if checks.is_nvidia_cuda():
            if checks.cuda_capability_compare("ge", 7, 5) and checks.torch_cuda_version_compare("ge", 11, 0):
                replacements["tanh"] = tanh_approx
            # They are not really faster
            # replacements["neg"] = neg_ftz
            # replacements["abs"] = abs_ftz
            # replacements["add"] = add_ftz
            # replacements["sub"] = sub_ftz
            # replacements["mul"] = mul_ftz
            # replacements["truediv"] = truediv_approx_ftz
            replacements["minimum"] = minimum_ftz
            replacements["maximum"] = maximum_ftz
            replacements["sqrt"] = sqrt_approx_ftz
            replacements["rsqrt"] = rsqrt_approx_ftz
            # They have accuracy issues
            # replacements["sin"] = sin_approx_ftz
            # replacements["cos"] = cos_approx_ftz
    with unittest.mock.patch.object(
        codegen_triton, "gen_common_triton_imports", gen_common_triton_imports_
    ), unittest.mock.patch.object(
        select_algorithm, "gen_common_triton_imports", gen_common_triton_imports_
    ), patch_multiple_triton_overrides(
        replacements
    ):
        yield
