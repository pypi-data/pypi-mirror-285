import os
import shutil
import sys
from pathlib import Path

import cmake
import externaltools


class WasmHandler(cmake.CMakeHandler):
    def __init__(self, srcdir: Path, builddir: Path | None = None, **kargs: any):
        super().__init__("wasm", srcdir, builddir, **kargs)
        envvar = externaltools.init_toolchain("emscripten", os.environ)
        self.toolchain = Path(envvar["EMSDK_CMAKE_TOOLCHAIN_FILE"])

    def get_generator(self) -> str:
        if sys.platform == "win32" and shutil.which("make") is not None:
            return "Unix Makefiles"
        return self.generator_

    def get_generator_args(self, _arch: str, _config: str) -> list[str]:
        return ["-DCMAKE_TOOLCHAIN_FILE=" + self.toolchain.as_posix()]
