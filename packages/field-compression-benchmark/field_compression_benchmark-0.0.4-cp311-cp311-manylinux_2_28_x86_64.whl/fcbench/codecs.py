__all__ = ["preload", "WasmCodecTemplate"]

import sys as _sys

from ._fcbench.codecs import WasmCodecTemplate


def preload():
    import importlib.resources

    for codec in (
        importlib.resources.files("fcbench")
        .joinpath("data")
        .joinpath("codecs")
        .iterdir()
    ):
        if codec.suffix != ".wasm":
            continue

        codec_class = WasmCodecTemplate.import_codec_class(
            codec,
            _sys.modules[__name__],
        )

        print(
            f"Loaded the {codec_class.__module__}.{codec_class.__name__} "
            "codec ..."
        )


# polyfill for fcpy.codecs imports
_sys.modules["fcpy.codecs"] = _sys.modules[__name__]
