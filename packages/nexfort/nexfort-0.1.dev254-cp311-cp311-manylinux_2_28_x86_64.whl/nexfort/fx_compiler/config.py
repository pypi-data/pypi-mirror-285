import os  # noqa: C101
import sys

from nexfort.utils import checks


def optional_bool_from_env(name, default=None):
    val = os.environ.get(name, None)
    if val is None:
        return default
    if val == "1":
        return True
    return False


# default ignore all the waring in comiple
ignore_warnings = os.environ.get("NEXFORT_FX_IGNORE_WARNINGS", "1") == "1"

# add some debug printouts
# debug = os.environ.get("NEXFORT_FX_DEBUG") == "1"
dump_graph = os.environ.get("NEXFORT_FX_DUMP_GRAPH") == "1"

cudagraphs = os.environ.get("NEXFORT_FX_CUDAGRAPHS") == "1"

disable_custom_passes = os.environ.get("NEXFORT_FX_DISABLE_CUSTOM_PASSES") == "1"

pre_dispatch = os.environ.get("NEXFORT_FX_PRE_DISPATCH", "1") == "1"

yield_to_mixed_mm = os.environ.get("NEXFORT_FX_YIELD_TO_MIXED_MM") == "1"

# https://github.com/NVIDIA/cutlass/blob/033d9efd2db0bbbcf3b3b0650acde6c472f3948e/include/cutlass/gemm/collective/fp8_accumulation.hpp#L61
gemm_use_fast_accum = os.environ.get("NEXFORT_GEMM_USE_FAST_ACCUM") == "1"


# config from env var
class overrides:
    conv_benchmark = optional_bool_from_env("NEXFORT_FX_CONV_BENCHMARK")
    conv_allow_tf32 = optional_bool_from_env("NEXFORT_FX_CONV_ALLOW_TF32")
    matmul_allow_tf32 = optional_bool_from_env("NEXFORT_FX_MATMUL_ALLOW_TF32")
    matmul_allow_fp16_reduction = optional_bool_from_env("NEXFORT_FX_MATMUL_ALLOW_FP16_REDUCTION")
    matmul_allow_bf16_reduction = optional_bool_from_env("NEXFORT_FX_MATMUL_ALLOW_BF16_REDUCTION")


class pre_aot:
    # There are no real pre_aot passes in the current implementation
    disable = True


class common:
    disable = False
    freezing = False
    cse = True
    functionalize = False  # TODO: Enable this
    remove_dropout = False  # Done by decomps
    lower_conv = False  # Done by decomps
    remove_contiguous = True
    remove_clone_preserve_format = True
    transform_view_to_reshape = True
    remove_simple_arith = True
    optimize_gelu = True


class post:
    disable = False
    hotfix_native_group_norm = True


def init_inductor_options():
    options = {
        "aggressive_fusion": True,
        # "shape_padding": True,
        # "permute_fusion": True,
        "epilogue_fusion_first": True,
        "triton.unique_kernel_names": os.environ.get("TORCHINDUCTOR_UNIQUE_KERNEL_NAMES", "1")
        == "1",  # Better display in nsys
        # The 2 options do not exist in torch<2.2.0
        # "cuda.compile_opt_level": "-O3",
        # "cuda.use_fast_math": True,
    }
    if checks.is_inductor_supported():
        from torch._inductor import config as inductor_config

        if hasattr(inductor_config, "always_keep_tensor_constants"):
            # If the graph gets frozen they will be converted to float constants to be inlined in Triton kernels,
            # causing code cache misses in every layer, which makes the compilation and autotuning slow.
            options["always_keep_tensor_constants"] = True
    return options


class inductor:
    disable = not checks.is_inductor_supported()
    mode = None
    options = init_inductor_options()
    dynamic = None

    unquantized_linear_use_triton_template = False
    fp8_linear_use_triton_template = False

    max_autotune_cublaslt_algos = 2
    # cuBLASLt INT8 GEMM outputs int32
    # resulting in higher memory usage since an extra conversion is needed
    max_autotune_cublaslt_int8_gemm = True

    transform_linear_out_dtype_to_linear_epilogue = True
    remove_clone_contiguous_format = True
    optimize_geglu = True
    optimize_attention = True
    optimize_linear_epilogue = False
    optimize_scaled_linear = True

    enable_cudnn_sdpa = os.environ.get("NEXFORT_FX_ENABLE_CUDNN_SDPA", "1") == "1"
    force_cudnn_sdpa = os.environ.get("NEXFORT_FX_FORCE_CUDNN_SDPA") == "1"


class cuda:
    disable = False

    fuse_qkv_projections = True
    optimize_conv = True
    optimize_lowp_gemm = True
    optimize_scaled_gemm = True

    optimize_group_norm = True


class jit:
    disable = True

    check_trace = False
    strict = False

    freezing = False
    # This is experimental and only has benefit for some cases
    # Reference: https://pytorch.org/docs/stable/generated/torch.jit.optimize_for_inference.html#torch.jit.optimize_for_inference
    optimize_for_inference = False

    disable_optimized_execution = os.environ.get("NEXFORT_FX_JIT_DISABLE_OPTIMIZED_EXECUTION") == "1"


class triton:
    enable_fast_math = True
    fuse_attention_allow_fp16_reduction = True

    max_num_imprecise_acc = None  # 2**7  # 32 (instruction K) * 4 (mma per mainloop)


_save_config_ignore = {
    # workaround: "Can't pickle <function ...>"
}

try:
    from torch.utils._config_module import install_config_module
except ImportError:
    # torch<2.2.0
    from torch._dynamo.config_utils import install_config_module

# adds patch, save_config, etc
install_config_module(sys.modules[__name__])
