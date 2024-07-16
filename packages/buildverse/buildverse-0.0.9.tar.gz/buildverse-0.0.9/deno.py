import argparse
import configparser
import datetime
import os
import subprocess
import sys
from pathlib import Path

if Path(__file__).as_posix() not in sys.path:
    sys.path.append(Path(__file__).as_posix())

# pylint: disable=wrong-import-position
import buildenv
import externaltools
import generator


class DenoBuilderError(Exception):
    pass


class DenoBuilder:
    def __init__(
        self, subdir: Path, reporoot: Path | None = None, buildroot: Path | None = None, out_file_list: Path | None = None, **_kwargs
    ):
        self._reporoot = reporoot
        self._buildenv = buildenv.BuildEnv(reporoot or subdir)
        if not subdir.is_absolute() and not subdir.exists() and reporoot:
            subdir = subdir.relative_to(reporoot)
        self.deno_exe = externaltools.get_deno()
        self.deno_build_root = self._buildenv.get_base_build_dir() / f"deno_{self._buildenv.get_unique_name(subdir)}"
        self.deno_build_root.mkdir(exist_ok=True, parents=True)
        self.deno_build_root = self.deno_build_root.absolute()
        self.srcdir = subdir.absolute()
        self.out_file_list = out_file_list
        self.dist = self.deno_build_root / "dist"
        self.deno_src = self.deno_build_root / "src"
        self.env = os.environ.copy()
        self.env["DENO_DIR"] = self.deno_build_root.as_posix()

    def load_config_dictionary(self, f: Path) -> dict[str, dict[str, str]]:
        config = configparser.ConfigParser()
        if f.exists():
            config.read(str(f))
        return {s.lower(): dict(config.items(s)) for s in config.sections()}

    def generate(self) -> None:
        configfile = self.srcdir / "deno.config.ini"
        config = self.load_config_dictionary(configfile)
        self_st_time_ns = 0 if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS") else os.stat(__file__).st_mtime_ns
        mtime_ns = max(self_st_time_ns, configfile.stat().st_mtime_ns)
        gen = generator.Generator(self.srcdir, self.deno_build_root, mtime_ns=mtime_ns)

        now = datetime.datetime.now()
        versiondate = f"{now.strftime('%y%j')}{int(now.hour/3)}"
        if int(versiondate[1:]) > 965535:
            raise DenoBuilderError("Version date too long. UWPs wont like that")
        config.setdefault("build", {})
        config.setdefault("deno", {})
        config["build"].setdefault("VersionDate", versiondate)
        versiondate = config["build"]["VersionDate"]
        if self._buildenv.get_npm_cache_dir() is None:
            raise DenoBuilderError(f"No Deno ROOT specified: {self._buildenv.get_npm_cache_dir()}")
        config["deno"].setdefault("GlobalPackageRoot", self._buildenv.get_npm_cache_dir().as_posix())
        config["deno"].setdefault("Executable", self.deno_exe.as_posix())
        config["deno"].setdefault("basepath", "")
        packages = filter(len, config["deno"].get("packages", "").split(","))
        proxies = filter(len, config["deno"].get("proxies", "").split(","))
        # pylint: disable=C0209
        proxies = ",".join("'{}' : '{}'".format(*entry.split("::")) for entry in proxies)
        config["deno"].setdefault("Proxies", proxies)
        config["deno"].setdefault("Packages", "\n".join([f'"{pkgname}" : "latest",' for pkgname in packages]))
        systmpldir = Path(__file__).parent / "templates" / "deno"
        tmpldir = systmpldir / "svelte"
        if not systmpldir.is_dir():
            raise DenoBuilderError("Cannot find templates for deno")
        gen.LoadDictionary(config)
        gen.GenerateFromTemplateDirectory(tmpldir)
        gen.GenerateImagesForManifest(self.load_config_dictionary(systmpldir / "images.ini"))
        if not self.deno_src.exists():
            self.deno_src.symlink_to(self.srcdir.absolute())
        if not self.deno_src.is_symlink():
            raise DenoBuilderError(f"{self.deno_src.as_posix()} is not a symlink")

        self.prebuild()
        self.build()

    def prebuild(self) -> None:
        (self.deno_build_root / "build").mkdir(parents=True, exist_ok=True)
        self.dist.mkdir(parents=True, exist_ok=True)

    def build(self) -> list[Path]:
        self.prebuild()
        subprocess.check_output(
            [self.deno_exe.as_posix(), "task", "build"],
            cwd=self.deno_build_root,
            env=self.env,
        )
        out_list = list(filter(lambda x: x.is_file(), self.dist.rglob("*")))
        if self.out_file_list:
            out_list_text = "\n".join([f"{p.relative_to(self.dist).as_posix()}!{p.as_posix()}" for p in out_list])
            if not self.out_file_list.exists() or self.out_file_list.read_text() != out_list_text:
                self.out_file_list.write_text(out_list_text)
        return out_list

    def run(self) -> None:
        subprocess.check_call([self.deno_exe.as_posix(), "task", "dev"], cwd=self.deno_build_root, env=self.env)

    @staticmethod
    def create_arg_parser(argparser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        argparser.add_argument("--generate", action="store_true", default=False, help="Npm generate")
        argparser.add_argument("--compile", action="store_true", default=False, help="Npm build")
        argparser.add_argument("--subdir", type=Path, default=None, help="")
        argparser.add_argument("--buildroot", type=Path, default=None, help="")
        argparser.add_argument("--out-file-list", type=Path, default=None, help="")
        return argparser

    @staticmethod
    def arg_handler(args: argparse.Namespace, *_extra: list[str]) -> None:
        obj = DenoBuilder(**dict(args.__dict__))
        if args.generate:
            obj.generate()
        if args.compile:
            obj.build()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    DenoBuilder.create_arg_parser(parser)
    DenoBuilder.arg_handler(parser.parse_args())
