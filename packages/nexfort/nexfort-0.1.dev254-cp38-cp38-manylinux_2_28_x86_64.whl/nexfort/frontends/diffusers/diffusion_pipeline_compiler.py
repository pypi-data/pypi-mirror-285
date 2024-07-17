import functools

import torch

from nexfort.compilers import nexfort_compile
from nexfort.utils.attributes import multi_recursive_apply
from nexfort.utils.memory_format import apply_memory_format


def compile_pipe(
    pipe,
    *,
    ignores=(),
    config=None,
    fuse_qkv_projections=False,
    memory_format=torch.preserve_format,
    quantize=False,
    quantize_config=None,
):
    if fuse_qkv_projections:
        pipe = fuse_qkv_projections_in_pipe(pipe)

    pipe = convert_pipe_to_memory_format(pipe, ignores=ignores, memory_format=memory_format)

    if quantize:
        if quantize_config is None:
            quantize_config = {}
        pipe = quantize_pipe(pipe, ignores=ignores, **quantize_config)

    if config is None:
        config = {}

    pipe = pure_compile_pipe(pipe, ignores=ignores, **config)
    return pipe


def pure_compile_pipe(pipe, *, ignores=(), **config):
    parts = [
        "text_encoder",
        "text_encoder_2",
        "image_encoder",
        "unet",
        "controlnet",
        "fast_unet",  # for deepcache
        "prior",  # for StableCascadePriorPipeline
        "decoder",  # for StableCascadeDecoderPipeline
        "transformer",  # for Transformer-based DiffusionPipeline such as DiTPipeline and PixArtAlphaPipeline
        "vqgan.down_blocks",  # for StableCascadeDecoderPipeline
        "vqgan.up_blocks",  # for StableCascadeDecoderPipeline
        "vae.decoder",
        "vae.encoder",
    ]
    multi_recursive_apply(pipe, parts, functools.partial(nexfort_compile, **config), ignores=ignores, verbose=True)
    return pipe


def fuse_qkv_projections_in_pipe(pipe):
    if hasattr(pipe, "fuse_qkv_projections"):
        pipe.fuse_qkv_projections()
    return pipe


def convert_pipe_to_memory_format(pipe, *, ignores=(), memory_format=torch.preserve_format):
    if memory_format == torch.preserve_format:
        return pipe

    parts = [
        "unet",
        "controlnet",
        "fast_unet",  # for deepcache
        "prior",  # for StableCascadePriorPipeline
        "decoder",  # for StableCascadeDecoderPipeline
        "transformer",  # for Transformer-based DiffusionPipeline such as DiTPipeline and PixArtAlphaPipeline
        "vqgan",  # for StableCascadeDecoderPipeline
        "vae",
    ]
    multi_recursive_apply(
        pipe, parts, functools.partial(apply_memory_format, memory_format=memory_format), ignores=ignores, verbose=True
    )
    return pipe


# def dynamic_quant_filter_fn(mod, *args):
#     return (isinstance(mod, torch.nn.Linear) and mod.in_features > 16
#             and (mod.in_features, mod.out_features) not in [
#                 (1280, 640),
#                 (1920, 1280),
#                 (1920, 640),
#                 (2048, 1280),
#                 (2048, 2560),
#                 (2560, 1280),
#                 (256, 128),
#                 (2816, 1280),
#                 (320, 640),
#                 (512, 1536),
#                 (512, 256),
#                 (512, 512),
#                 (640, 1280),
#                 (640, 1920),
#                 (640, 320),
#                 (640, 5120),
#                 (640, 640),
#                 (960, 320),
#                 (960, 640),
#             ])


def quantize_pipe(pipe, *, ignores=(), **kwargs):
    from nexfort.ao import quantize

    # if "dynamic_quant_filter_fn" not in kwargs:
    #     kwargs["dynamic_quant_filter_fn"] = dynamic_quant_filter_fn

    parts = [
        "unet",
        "controlnet",
        "fast_unet",  # for deepcache
        "prior",  # for StableCascadePriorPipeline
        "decoder",  # for StableCascadeDecoderPipeline
        "transformer",  # for Transformer-based DiffusionPipeline such as DiTPipeline and PixArtAlphaPipeline
    ]
    multi_recursive_apply(pipe, parts, functools.partial(quantize, **kwargs), ignores=ignores, verbose=True)
    return pipe
