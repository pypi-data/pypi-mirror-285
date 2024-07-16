#!/usr/bin/python3
import hashlib
from pathlib import Path
from typing import Optional

import configenv
import quick
import sync


class BuildEnv:
    def __init__(self, reporoot: Path | str):
        self._reporoot: Path = Path(reporoot)
        self._configenv = configenv.ConfigEnv(self._reporoot.as_posix())

    def sync_build_files(self, mode: str) -> None:
        curfiledir = Path(__file__).parent
        synclist = {
            "ci": None,
            "cmake": None,
            "include/CommonMacros.h": None,
            "include/TestUtils.h": None,
            "externaltools.py": None,
            "clang-format": ".clang-format",
            "gitignore": ".gitignore",
            "gitattributes": ".gitattributes",
            "pyproject.toml": "pyproject.toml",
        }

        tgtfiles: dict[str, Path] = {}
        rootleveldirs: list[Path] = [d for d in self._reporoot.iterdir() if d.is_dir() and d.name != ".git"] + [
            Path(),
        ]
        for d in rootleveldirs:
            scandir = self._reporoot / d
            if not scandir.exists():
                continue
            if scandir.name in synclist:
                for fpath in scandir.rglob("*"):
                    if not fpath.is_dir():
                        tgtfiles[fpath.relative_to(self._reporoot).as_posix()] = fpath
                        tgtfiles[fpath.name] = fpath
            else:
                for f in scandir.iterdir():
                    if f.is_file():
                        tgtfiles[f.as_posix()] = f
                        tgtfiles[f.name] = f
        for k, v in synclist.items():
            srcfs = [curfiledir / k]

            def expand_dirs(srcf: Path) -> list[Path]:
                return [fpath for fpath in srcf.rglob("*") if not fpath.is_dir()] if srcf.is_dir() else [srcf]

            # flatten array of arrays
            srcfs = [file for srcf in srcfs for file in expand_dirs(srcf)]
            for srcf in srcfs:
                vname = Path(v or srcf.as_posix()).name
                if vname in tgtfiles:
                    sync.Syncer.sync_files(srcf, tgtfiles[vname], mode)

        file_quickdecl = self._reporoot / "quickload.config.ini"
        if file_quickdecl.exists():
            _quickbuild = quick.Quick(self._reporoot, [file_quickdecl])

    @staticmethod
    def find_git_root(reporoot: Path) -> Path:
        curdir: Path = reporoot
        while curdir.absolute() != curdir.parent.absolute():
            if (curdir / ".git").exists():
                return curdir
            curdir = curdir.parent
        return reporoot

    @staticmethod
    def get_project_name(reporoot: Path) -> str:
        projectname = reporoot.relative_to(BuildEnv.find_git_root(reporoot).parent).as_posix()
        return projectname.replace("/", "_")

    def get_bin_path(self) -> Path:
        return Path(self._configenv.GetConfigPath("DEVEL_BINPATH", make=True))

    def _validate_dir(self, path: Path) -> Path:
        path.mkdir(exist_ok=True)
        return path

    def get_unique_name(self, sdir: Optional[Path] = None) -> str:
        srcdir: Path = sdir or self._reporoot
        hashstr: str = hashlib.md5(srcdir.as_posix().lower().encode("utf-8")).hexdigest()[0:8]
        return f"{srcdir.name}_{hashstr}"

    def get_base_build_dir(self) -> Path:
        return self._configenv.GetConfigPath("DEVEL_BUILDPATH", make=True) / self.get_unique_name()

    def get_build_dir(self, mode: str, arch: str) -> Path:
        return self._validate_dir(self.get_base_build_dir() / f"{mode}_{arch}")

    def get_fetch_content_base_dir(self) -> Path:
        return self._configenv.GetConfigPath("DEVEL_BUILDPATH", make=True) / "externalsrcs"

    def get_npm_cache_dir(self) -> Path:
        return self._configenv.GetConfigPath("NPM_BUILD_ROOT", make=True)
