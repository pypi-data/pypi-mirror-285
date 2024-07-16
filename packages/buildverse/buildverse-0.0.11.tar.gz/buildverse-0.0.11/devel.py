#!/usr/bin/python3
import argparse
import datetime
import logging
import os
import os.path
import subprocess
import sys
from pathlib import Path

import android
import buildenv
import cmake
import configenv
import deno
import externaltools
import packager
import quick
import svelte
import uwp
import vcpkg
import wasm


def normalize_path(fpath: str) -> Path:
    return Path(os.path.expandvars(str(fpath))).expanduser()


class Devel:
    def __init__(self, reporoot: str):
        self._buildenv = buildenv.BuildEnv(normalize_path(reporoot))


Toolchains = ["auto", "uwp", "msvc", "mingw", "wasm", "and"]
Archs = ["auto", "x86", "x64", "arm", "arm64"]
Configs = ["dbg", "rel"]
Actions = ["open", "build", "clean", "gen", "pack", "run", "test", "format"]


def acquire_tool(args, _extra: list[str]) -> None:
    toolpath = externaltools.acquire_tool(args.tools)
    print(toolpath.as_posix())  # noqa: T201


def config_sub_command_handler(args, _extra: list[str]) -> None:
    if args.queryparam == "fetchcontent_base_dir":
        print(buildenv.BuildEnv(args.reporoot).get_fetch_content_base_dir().as_posix())  # noqa: T201
    else:
        print(configenv.ConfigEnv(normalize_path(args.reporoot)).GetConfigStr(args.queryparam))  # noqa: T201


def quick_sub_command_handler(args, _extra: list[str]) -> None:
    configs = [normalize_path(configpath) for configpath in args.config]
    quick.Quick(normalize_path(args.reporoot), configs).generate(args.outtype, normalize_path(args.out))


def action_sub_command_handler(args, extraargs: list[str]) -> None:
    def parse_args(switches):
        groups = {"toolchains": [], "archs": [], "configs": [], "actions": []}
        for s in switches:
            if s in Archs:
                groups["archs"].append(s)
            if s in Toolchains:
                groups["toolchains"].append(s)
            if s in Configs:
                groups["configs"].append(s)
            if s in Actions:
                groups["actions"].append(s)

        if len(groups["actions"]) == 0:
            groups["actions"].append(Actions[0])
        if len(groups["archs"]) == 0:
            groups["archs"].append(Archs[0])
        if len(groups["configs"]) == 0:
            groups["configs"].append(Configs[0])
        if len(groups["toolchains"]) == 0:
            groups["toolchains"].append(Toolchains[0])
        return groups

    opts: dict[str, object] = {}
    if args.avoid_ninja:
        opts["avoid_ninja"] = True

    keywords = [*Toolchains, *Archs, *Configs, *Actions]
    switches = [arg for arg in extraargs if arg in keywords]
    extraargs = [arg for arg in extraargs if arg not in keywords]
    if args.sync != "no" or (args.sync == "auto" and (normalize_path(args.reporoot) / "quick.config.ini").exists()):
        buildenv.BuildEnv(normalize_path(args.reporoot)).sync_build_files(args.sync)
    groups = parse_args(switches)
    starttime = datetime.datetime.now()

    for s in groups["toolchains"]:
        toolchain = s
        if s == "auto":
            toolchain = externaltools.detect_toolchain()["toolchain"]
        if toolchain:
            externaltools.init_toolchain(toolchain)
        else:
            toolchain = "exe"
        handler: cmake.Handler = uwp.ExeHandler(normalize_path(args.reporoot), **opts)
        if toolchain == "uwp":
            handler = uwp.UWPHandler(normalize_path(args.reporoot), **opts)
        if toolchain == "wasm":
            handler = wasm.WasmHandler(normalize_path(args.reporoot), **opts)
        if toolchain == "and":
            handler = android.AndroidAppHandler(normalize_path(args.reporoot), **opts)
        if s == "andcli":
            handler = android.AndroidCLIHandler(normalize_path(args.reporoot), **opts)
        tasks = groups["actions"]
        if "test" in tasks:
            tasks.extend(["build"])
        if "run" in tasks:
            tasks.extend(["build"])
        if "pack" in tasks:
            tasks.extend(["gen"])
        if "build" in tasks:
            tasks.extend(["gen"])
        if "format" in tasks:
            tasks.extend(["gen"])
        if "open" in tasks:
            tasks.extend(["gen"])
        tasks = list(set(tasks))
        req = cmake.ActionRequest()
        req.archs = [externaltools.DefaultArch if arch == "auto" else arch for arch in groups["archs"]]
        req.configs = groups["configs"]
        genextraargs = [] if "run" in tasks else extraargs
        if "clean" in tasks:
            handler.clean(req)
        if "gen" in tasks:
            handler.pre_generate(req)
            handler.generate(req, genextraargs)
        if "format" in tasks:
            handler.format(req)
        if "build" in tasks:
            handler.build(req)
        if "open" in tasks:
            handler.open(req)
        if "run" in tasks:
            handler.run(req, extraargs)
        if "pack" in tasks:
            handler.package(req)
        if "test" in tasks:
            handler.test(req)

        endtime = datetime.datetime.now()
        logging.info(f"ElapsedTime:{endtime - starttime}")


def main() -> None:  # noqa: PLR0915
    parser = argparse.ArgumentParser(description="Loading Script")

    parser.add_argument("reporoot", type=str, default=None, help="Repository")
    parser.add_argument("--nostdin", action="store_true", default=False, help="Do not prompt")
    parser.add_argument("--sync", type=str, default="auto", choices=["no", "fwd", "back", "auto"], help="Do not prompt")
    parser.add_argument("--pull", action="store_true", default=False)
    parser.add_argument("--self-update", action="store_true", default=False)
    parser.add_argument("--avoid-ninja", action="store_true", default=False, help="Prefer Ninja")

    vcpkg_parser = vcpkg.Vcpkg.create_arg_parser(argparse.ArgumentParser(description="Vcpkg interactions"))
    vcpkg_parser.set_defaults(func=vcpkg.Vcpkg.arg_handler)

    npm_parser = svelte.SvelteBuilder.create_arg_parser(argparse.ArgumentParser(description="NPM interactions"))
    npm_parser.set_defaults(func=svelte.SvelteBuilder.arg_handler)

    deno_parser = deno.DenoBuilder.create_arg_parser(argparse.ArgumentParser(description="Deno interactions"))
    deno_parser.set_defaults(func=deno.DenoBuilder.arg_handler)
    acquire_tool_parser = argparse.ArgumentParser(description="Acquire build Tools")
    acquire_tool_parser.add_argument("tools", type=str, default=None, help="Tools to acquire")
    acquire_tool_parser.set_defaults(func=acquire_tool)

    config_parser = argparse.ArgumentParser(description="Config Query Set")
    config_parser.add_argument("--queryparam", type=str, default=None, help="Query Value for Parameter")
    config_parser.set_defaults(func=config_sub_command_handler)

    quick_parser = argparse.ArgumentParser(description="Quick")
    quick_parser.add_argument("config", type=str, nargs="+", default=None, help="Config File")
    quick_parser.add_argument("out", type=str, default=None, help="Output directory")
    quick_parser.add_argument("--outtype", type=str, default=None, help="Type")
    quick_parser.set_defaults(func=quick_sub_command_handler)

    packager_parser = packager.Packager.create_arg_parser(argparse.ArgumentParser(description="Packaging"))
    packager_parser.set_defaults(func=packager.Packager.arg_handler)
    subparsers = {
        "vcpkg": vcpkg_parser,
        "npm": npm_parser,
        "deno": deno_parser,
        "config": config_parser,
        "quick": quick_parser,
        "acquiretool": acquire_tool_parser,
    }

    args, extra = parser.parse_known_args()

    if args.self_update:
        self_path = Path(__file__)
        before_pull = self_path.stat().st_mtime_ns
        subprocess.check_call([externaltools.get_git().as_posix(), "-c", "http.sslVerify=false", "-C", self_path.parent.absolute().as_posix(), "pull"])
        if self_path.stat().st_mtime_ns != before_pull:
            subprocess.run([sys.executable, *sys.argv], check=True)
            return

    if args.pull:
        subprocess.check_call([externaltools.get_git().as_posix(), "-c", "http.sslVerify=false", "-C", args.reporoot, "pull"])

    if not args.nostdin:
        configenv.ConfigEnv.StartMonitor()
    try:
        if Path(__file__).is_symlink():
            sys.path.append(Path(__file__).readlink().parent)
        else:
            sys.path.append(Path(__file__).parent)

        if sys.prefix == sys.base_prefix and not getattr(sys, "frozen", False):
            sys.stderr.write(f"Creating Virtual Environment and Relaunching {sys.argv}\n")
            venv = configenv.ConfigEnv("").GetConfigPath("DEVEL_BUILDPATH", make=True) / "python_venv"
            if not venv.exists():
                subprocess.check_output([sys.executable, "-m", "venv", venv.as_posix()])
            pyexe = venv / "Scripts" / "python.exe" if sys.platform == "win32" else (venv / "bin" / "python3")
            pips = subprocess.check_output([pyexe, "-m", "pip", "list", "--format", "freeze"], text=True).splitlines()
            installedpips = {pip.split("==")[0] for pip in pips}
            requiredpips = []  # ["PyQt6"]
            installpips = [pip for pip in requiredpips if pip not in installedpips]
            subprocess.check_output([pyexe, "-m", "pip", "install", "--upgrade", "pip", *installpips])
            configenv.ConfigEnv.StopMonitor()
            subprocess.run([pyexe, *sys.argv], check=True)
            sys.exit(0)
        sys.stderr.write(f"Prefix: {sys.prefix}\nBase: {sys.base_prefix}\nExe : {sys.executable} {getattr(sys, 'frozen', False)}\n")
        if len(extra) and extra[0] in subparsers:
            subargs, extra = subparsers[extra[0]].parse_known_args(extra[1:])
            subargs = argparse.Namespace(**vars(subargs), **vars(args))
            subargs.func(subargs, extra)
        else:
            action_sub_command_handler(args, extra)
    finally:
        configenv.ConfigEnv.StopMonitor()


if __name__ == "__main__":
    main()
