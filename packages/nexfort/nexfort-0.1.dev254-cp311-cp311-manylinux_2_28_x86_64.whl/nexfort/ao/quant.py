import functools
import importlib
import os

import torch
from torchao.quantization.subclass import QuantizedLinearWeightBase

from .quantization import (
    apply_fp8_dynamic_quant,
    apply_fp8_weightonly_quant,
    apply_int8_dynamic_quant,
    change_linear_weights_to_int4_woqtensors,
    change_linear_weights_to_int8_woqtensors,
)
from .quantization.subclass import (
    Float8DynamicallyQuantizedLinearWeight,
    Float8WeightOnlyQuantizedLinearWeight,
    OptimizedInt4WeightOnlyQuantizedLinearWeight,
    OptimizedInt8DynamicallyQuantizedLinearWeight,
    OptimizedInt8WeightOnlyQuantizedLinearWeight,
)

NEXFORT_AO_QUANT_TYPE = os.environ.get("NEXFORT_AO_QUANT_TYPE", "int8_dynamic")


def quantize(module, *, quant_type=NEXFORT_AO_QUANT_TYPE, filter_fn=None, filter_fn_kwargs=None):
    supported_quant_types = (
        "int8_dynamic",
        "int4_weightonly",
        "int8_weightonly",
        "fp8_e4m3_e4m3_dynamic",
        "fp8_e4m3_e5m2_dynamic",
        "fp8_e5m2_e5m2_dynamic",
        "fp8_e5m2_e4m3_dynamic",
        "fp8_e4m3_e4m3_weightonly",
        "fp8_e4m3_e5m2_weightonly",
        "fp8_e5m2_e5m2_weightonly",
        "fp8_e5m2_e4m3_weightonly",
        "fp8_e4m3_weightonly",
        "fp8_e5m2_weightonly",
        "fp8_e4m3_e4m3_dynamic_per_tensor",
        "fp8_e4m3_e5m2_dynamic_per_tensor",
        "fp8_e5m2_e5m2_dynamic_per_tensor",
        "fp8_e5m2_e4m3_dynamic_per_tensor",
        "fp8_e4m3_e4m3_weightonly_per_tensor",
        "fp8_e4m3_e5m2_weightonly_per_tensor",
        "fp8_e5m2_e5m2_weightonly_per_tensor",
        "fp8_e5m2_e4m3_weightonly_per_tensor",
    )
    assert quant_type in supported_quant_types, f"Unsupported quant_type: {quant_type}"

    if isinstance(filter_fn, str):
        if "." in filter_fn:
            module_name, attr_name = filter_fn.rsplit(".", 1)
        else:
            module_name, attr_name = "nexfort.ao.quantization.filter_functions", filter_fn
        filter_fn = getattr(importlib.import_module(module_name), attr_name)
    if filter_fn is not None and filter_fn_kwargs is not None:
        filter_fn = functools.partial(filter_fn, **filter_fn_kwargs)

    if quant_type == "int4_weightonly":
        change_linear_weights_to_int4_woqtensors(module, filter_fn=filter_fn)
    elif quant_type == "int8_weightonly":
        change_linear_weights_to_int8_woqtensors(module, filter_fn=filter_fn)
    elif quant_type == "int8_dynamic":
        # apply_dynamic_quant(module, filter_fn=filter_fn)
        apply_int8_dynamic_quant(module, filter_fn=filter_fn)
    elif quant_type == "fp8_e4m3_e4m3_dynamic":
        apply_fp8_dynamic_quant(
            module, act_dtype=torch.float8_e4m3fn, weight_dtype=torch.float8_e4m3fn, filter_fn=filter_fn
        )
    elif quant_type == "fp8_e4m3_e5m2_dynamic":
        apply_fp8_dynamic_quant(
            module, act_dtype=torch.float8_e4m3fn, weight_dtype=torch.float8_e5m2, filter_fn=filter_fn
        )
    elif quant_type == "fp8_e5m2_e5m2_dynamic":
        apply_fp8_dynamic_quant(
            module, act_dtype=torch.float8_e5m2, weight_dtype=torch.float8_e5m2, filter_fn=filter_fn
        )
    elif quant_type == "fp8_e5m2_e4m3_dynamic":
        apply_fp8_dynamic_quant(
            module, act_dtype=torch.float8_e5m2, weight_dtype=torch.float8_e4m3fn, filter_fn=filter_fn
        )
    elif quant_type == "fp8_e4m3_e4m3_weightonly":
        apply_fp8_weightonly_quant(
            module, act_dtype=torch.float8_e4m3fn, weight_dtype=torch.float8_e4m3fn, filter_fn=filter_fn
        )
    elif quant_type == "fp8_e4m3_e5m2_weightonly":
        apply_fp8_weightonly_quant(
            module, act_dtype=torch.float8_e4m3fn, weight_dtype=torch.float8_e5m2, filter_fn=filter_fn
        )
    elif quant_type == "fp8_e5m2_e5m2_weightonly":
        apply_fp8_weightonly_quant(
            module, act_dtype=torch.float8_e5m2, weight_dtype=torch.float8_e5m2, filter_fn=filter_fn
        )
    elif quant_type == "fp8_e5m2_e4m3_weightonly":
        apply_fp8_weightonly_quant(
            module, act_dtype=torch.float8_e5m2, weight_dtype=torch.float8_e4m3fn, filter_fn=filter_fn
        )
    elif quant_type == "fp8_e4m3_weightonly":
        apply_fp8_weightonly_quant(module, weight_dtype=torch.float8_e4m3fn, filter_fn=filter_fn)
    elif quant_type == "fp8_e5m2_weightonly":
        apply_fp8_weightonly_quant(module, weight_dtype=torch.float8_e5m2, filter_fn=filter_fn)
    elif quant_type == "fp8_e4m3_e4m3_dynamic_per_tensor":
        apply_fp8_dynamic_quant(
            module,
            act_dtype=torch.float8_e4m3fn,
            weight_dtype=torch.float8_e4m3fn,
            per_tensor=True,
            filter_fn=filter_fn,
        )
    elif quant_type == "fp8_e4m3_e5m2_dynamic_per_tensor":
        apply_fp8_dynamic_quant(
            module, act_dtype=torch.float8_e4m3fn, weight_dtype=torch.float8_e5m2, per_tensor=True, filter_fn=filter_fn
        )
    elif quant_type == "fp8_e5m2_e5m2_dynamic_per_tensor":
        apply_fp8_dynamic_quant(
            module, act_dtype=torch.float8_e5m2, weight_dtype=torch.float8_e5m2, per_tensor=True, filter_fn=filter_fn
        )
    elif quant_type == "fp8_e5m2_e4m3_dynamic_per_tensor":
        apply_fp8_dynamic_quant(
            module, act_dtype=torch.float8_e5m2, weight_dtype=torch.float8_e4m3fn, per_tensor=True, filter_fn=filter_fn
        )
    elif quant_type == "fp8_e4m3_e4m3_weightonly_per_tensor":
        apply_fp8_weightonly_quant(
            module,
            act_dtype=torch.float8_e4m3fn,
            weight_dtype=torch.float8_e4m3fn,
            per_tensor=True,
            filter_fn=filter_fn,
        )
    elif quant_type == "fp8_e4m3_e4m3_weightonly_per_tensor":
        apply_fp8_weightonly_quant(
            module, act_dtype=torch.float8_e4m3fn, weight_dtype=torch.float8_e5m2, per_tensor=True, filter_fn=filter_fn
        )
    elif quant_type == "fp8_e4m3_e4m3_weightonly_per_tensor":
        apply_fp8_weightonly_quant(
            module, act_dtype=torch.float8_e5m2, weight_dtype=torch.float8_e5m2, per_tensor=True, filter_fn=filter_fn
        )
    elif quant_type == "fp8_e4m3_e4m3_weightonly_per_tensor":
        apply_fp8_weightonly_quant(
            module, act_dtype=torch.float8_e5m2, weight_dtype=torch.float8_e4m3fn, per_tensor=True, filter_fn=filter_fn
        )
    else:
        raise ValueError(f"Unsupported quant_type: {quant_type}")
    return module


def is_quantized_module(module, *, quant_type=None):
    if quant_type is None:
        choices = QuantizedLinearWeightBase
    elif quant_type == "int8_dynamic":
        choices = OptimizedInt8DynamicallyQuantizedLinearWeight
    elif quant_type == "int4_weightonly":
        choices = OptimizedInt4WeightOnlyQuantizedLinearWeight
    elif quant_type == "int8_weightonly":
        choices = OptimizedInt8WeightOnlyQuantizedLinearWeight
    elif quant_type in (
        "fp8_e4m3_e4m3_dynamic",
        "fp8_e4m3_e5m2_dynamic",
        "fp8_e5m2_e5m2_dynamic",
        "fp8_e5m2_e4m3_dynamic",
        "fp8_e4m3_e4m3_dynamic_per_tensor",
        "fp8_e4m3_e5m2_dynamic_per_tensor",
        "fp8_e5m2_e5m2_dynamic_per_tensor",
        "fp8_e5m2_e4m3_dynamic_per_tensor",
    ):
        choices = Float8DynamicallyQuantizedLinearWeight
    elif quant_type in (
        "fp8_e4m3_e4m3_weightonly",
        "fp8_e4m3_e5m2_weightonly",
        "fp8_e5m2_e5m2_weightonly",
        "fp8_e5m2_e4m3_weightonly",
        "fp8_e4m3_weightonly",
        "fp8_e5m2_weightonly",
        "fp8_e4m3_e4m3_weightonly_per_tensor",
        "fp8_e4m3_e5m2_weightonly_per_tensor",
        "fp8_e5m2_e5m2_weightonly_per_tensor",
        "fp8_e5m2_e4m3_weightonly_per_tensor",
    ):
        choices = Float8WeightOnlyQuantizedLinearWeight
    elif "weightonly" in quant_type:
        choices = (
            OptimizedInt4WeightOnlyQuantizedLinearWeight,
            OptimizedInt8WeightOnlyQuantizedLinearWeight,
            Float8WeightOnlyQuantizedLinearWeight,
        )
    elif "dynamic" in quant_type:
        choices = (OptimizedInt8DynamicallyQuantizedLinearWeight, Float8DynamicallyQuantizedLinearWeight)
    else:
        raise ValueError(f"Unsupported quant_type: {quant_type}")
    for param in module.parameters():
        if isinstance(param, choices):
            return True
    return False
