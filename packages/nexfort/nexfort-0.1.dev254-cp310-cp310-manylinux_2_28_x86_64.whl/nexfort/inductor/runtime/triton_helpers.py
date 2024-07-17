try:
    import triton
    import triton.language as tl
except ImportError:

    class triton:  # type: ignore[no-redef]
        @triton.jit
        def jit(x):
            return x

    class tl:  # type: ignore[no-redef]
        constexpr = None  # type: ignore[var-annotated]
        math = None  # type: ignore[var-annotated]
        extra = None  # type: ignore[var-annotated]


# In the latest triton, math functions were shuffled around into different modules:
# https://github.com/openai/triton/pull/3172
if hasattr(tl.extra, "cuda") and hasattr(tl.extra.cuda, "libdevice"):
    libdevice = tl.extra.cuda.libdevice
    math = tl.math
elif hasattr(tl.extra, "intel") and hasattr(tl.extra.intel, "libdevice"):
    libdevice = tl.extra.intel.libdevice
    math = tl.math
else:
    libdevice = tl.math
    math = tl


@triton.jit
def promote_to_tensor(x):
    # Addition promotes to tensor for us
    return x + tl.zeros((1,), tl.int1)


@triton.jit
def is_floating(x):
    return promote_to_tensor(x).dtype.is_floating()


@triton.jit
def is_fp32(x):
    return promote_to_tensor(x).dtype.is_fp32()


@triton.jit
def is_fp16(x):
    return promote_to_tensor(x).dtype.is_fp16()


@triton.jit
def neg_ftz(x):
    if not is_fp32(x):
        return -x
    ret = tl.inline_asm_elementwise("neg.ftz.f32 $0, $1;", "=f, f", [x], dtype=tl.float32, is_pure=True, pack=1)
    return ret.to(x.dtype)


@triton.jit
def abs_ftz(x):
    if is_fp32(x):
        ret = tl.inline_asm_elementwise("abs.ftz.f32 $0, $1;", "=f, f", [x], dtype=tl.float32, is_pure=True, pack=1)
        return ret.to(x.dtype)
    return math.abs(x)


@triton.jit
def add_ftz(a, b):
    if is_fp32(a) and is_fp32(b):
        ret = tl.inline_asm_elementwise(
            "add.ftz.f32 $0, $1, $2;", "=f, f, f", [a, b], dtype=tl.float32, is_pure=True, pack=1
        )
        return ret.to(a.dtype)
    return a + b


@triton.jit
def sub_ftz(a, b):
    if is_fp32(a) and is_fp32(b):
        ret = tl.inline_asm_elementwise(
            "sub.ftz.f32 $0, $1, $2;", "=f, f, f", [a, b], dtype=tl.float32, is_pure=True, pack=1
        )
        return ret.to(a.dtype)
    return a - b


@triton.jit
def mul_ftz(a, b):
    if is_fp32(a) and is_fp32(b):
        ret = tl.inline_asm_elementwise(
            "mul.ftz.f32 $0, $1, $2;", "=f, f, f", [a, b], dtype=tl.float32, is_pure=True, pack=1
        )
        return ret.to(a.dtype)
    return a * b


@triton.jit
def truediv_approx_ftz(a, b):
    if is_fp32(a):
        ret = tl.inline_asm_elementwise(
            "div.approx.ftz.f32 $0, $1, $2;", "=f, f, f", [a, b], dtype=tl.float32, is_pure=True, pack=1
        )
        return ret.to(a.dtype)
    return a / b


@triton.jit
def minimum_ftz(a, b):
    if is_fp32(a) and is_fp32(b):
        ret = tl.inline_asm_elementwise(
            "min.ftz.f32 $0, $1, $2;", "=f, f, f", [a, b], dtype=tl.float32, is_pure=True, pack=1
        )
        return ret.to(a.dtype)
    mask = a < b
    if is_floating(a):
        mask |= a != a
    return tl.where(mask, a, b)


@triton.jit
def maximum_ftz(a, b):
    if is_fp32(a) and is_fp32(b):
        ret = tl.inline_asm_elementwise(
            "max.ftz.f32 $0, $1, $2;", "=f, f, f", [a, b], dtype=tl.float32, is_pure=True, pack=1
        )
        return ret.to(a.dtype)
    mask = a > b
    if is_floating(a):
        mask |= a != a
    return tl.where(mask, a, b)


@triton.jit
def minimum_ftz_fp16(a, b):
    if is_fp16(a) and is_fp16(b):
        ret = tl.inline_asm_elementwise(
            "min.ftz.f16x2 $0, $1, $2;", "=r, r, r", [a, b], dtype=tl.float16, is_pure=True, pack=2
        )
        return ret.to(a.dtype)
    return minimum_ftz(a, b)


@triton.jit
def maximum_ftz_fp16(a, b):
    if is_fp16(a) and is_fp16(b):
        ret = tl.inline_asm_elementwise(
            "max.ftz.f16x2 $0, $1, $2;", "=r, r, r", [a, b], dtype=tl.float16, is_pure=True, pack=2
        )
        return ret.to(a.dtype)
    return maximum_ftz(a, b)


@triton.jit
def tanh_approx(x):
    if is_fp32(x):
        return tl.inline_asm_elementwise(
            "tanh.approx.f32 $0, $1;", "=f, f", [x], dtype=tl.float32, is_pure=True, pack=1
        ).to(x.dtype)
    return libdevice.tanh(x)


@triton.jit
def sqrt_approx_ftz(x):
    if is_fp32(x):
        ret = tl.inline_asm_elementwise(
            "sqrt.approx.ftz.f32 $0, $1;", "=f, f", [x], dtype=tl.float32, is_pure=True, pack=1
        )
        return ret.to(x.dtype)
    return libdevice.sqrt(x)


@triton.jit
def rsqrt_approx_ftz(x):
    if is_fp32(x):
        ret = tl.inline_asm_elementwise(
            "rsqrt.approx.ftz.f32 $0, $1;", "=f, f", [x], dtype=tl.float32, is_pure=True, pack=1
        )
        return ret.to(x.dtype)
    return libdevice.rsqrt(x)


@triton.jit
def sin_approx_ftz(x):
    if is_fp32(x):
        ret = tl.inline_asm_elementwise(
            "cos.approx.ftz.f32 $0, $1;", "=f, f", [x], dtype=tl.float32, is_pure=True, pack=1
        )
        return ret.to(x.dtype)
    return math.sin(x)


@triton.jit
def cos_approx_ftz(x):
    if is_fp32(x):
        ret = tl.inline_asm_elementwise(
            "cos.approx.ftz.f32 $0, $1;", "=f, f", [x], dtype=tl.float32, is_pure=True, pack=1
        )
        return ret.to(x.dtype)
    return math.cos(x)
