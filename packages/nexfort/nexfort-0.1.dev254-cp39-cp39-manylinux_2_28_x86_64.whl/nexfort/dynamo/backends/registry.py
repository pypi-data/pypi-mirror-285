import functools


@functools.lru_cache(None)
def _lazy_import():
    from torch._dynamo.utils import import_submodule

    from .. import backends

    import_submodule(backends)
