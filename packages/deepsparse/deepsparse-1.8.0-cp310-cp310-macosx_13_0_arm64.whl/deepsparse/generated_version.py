# neuralmagic: no copyright
# flake8: noqa
# fmt: off
# isort: skip_file
__all__ = ["__version__", "version", "version_major", "version_minor", "version_bug", "version_build", "version_major_minor", "optimized", "is_release", "revision", "splash", "is_nightly", "build_date"]
__version__ = "1.8.0"

version = __version__
version_major, version_minor, version_bug, version_build = version.split(".") + (
    [None] if len(version.split(".")) < 4 else []
) # handle conditional for version being 3 parts or 4 
version_major_minor = f"{version_major}.{version_minor}"
optimized = 1
is_release = 1
is_nightly = 0
is_enterprise = 0
revision = "e3778e93"
splash = "DeepSparse, Copyright 2021-present / Neuralmagic, Inc. version: 1.8.0 (e3778e93) (release) (optimized) (system=neon, binary=neon)"
build_date = "20240718"
