import configparser
import datetime
import fnmatch
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Generator, Optional

import buildenv
import externaltools
import generator


class CMakeError(RuntimeError):
    pass


def json_merge_write(jsonf: Path, values: dict[str, any]) -> None:
    def _dumpdict(obj: dict[str, any]) -> str:
        return json.dumps(obj, cls=externaltools.CustomEncoder, indent=2)

    if jsonf.exists():
        origdict1 = json.load(jsonf.open("r", encoding="utf-8-sig"))
        origdict2 = json.load(jsonf.open("r", encoding="utf-8-sig"))

        def _merge_equal_list(lista: list[any], listb: list[any]) -> None:
            for i, v in enumerate(listb):
                oldval = lista[i]
                if isinstance(oldval, dict):
                    _merge_dict(oldval, v)
                elif isinstance(oldval, list):
                    _merge_list(oldval, v)
                else:
                    lista[i] = v

        def _merge_list(lista: list[any], listb: list[any]) -> None:
            if len(lista) == len(listb):
                return _merge_equal_list(lista, listb)
            lista.extend(listb)
            return None

        def _merge_dict(dicta: dict[str, any], dictb: dict[str, any]) -> None:
            for k, v in dictb.items():
                if k not in dicta:
                    dicta[k] = v
                else:
                    oldval = dicta[k]
                    if isinstance(oldval, dict):
                        _merge_dict(oldval, v)
                    elif isinstance(oldval, list):
                        _merge_list(dicta[k], v)
                    else:
                        dicta[k] = v

        _merge_dict(origdict1, values)
        if _dumpdict(origdict1) == _dumpdict(origdict2):
            return
        values = origdict1
    jsonf.write_text(json.dumps(values, cls=externaltools.CustomEncoder, indent=2), encoding="utf-8-sig")


LAUNCH_JSON_GDB = """{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Launch",
            "type": "cppdbg",
            "request": "launch",
            "program": "${command:cmake.launchTargetPath}",
            "args": [
            ],
            "stopAtEntry": false,
            "cwd": "${command:cmake.getLaunchTargetDirectory}",
            "environment": [
            ],
            "console": "integratedTerminal",
            "MIMode": "gdb",
            "setupCommands": [
                {
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                },
                {
                    "description": "Set Disassembly Flavor to Intel",
                    "text": "-gdb-set disassembly-flavor intel",
                    "ignoreFailures": true
                }
            ]
        }
    ]
}"""


LAUNCH_JSON_VS = """{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Launch",
      "type": "cppvsdbg",
      "request": "launch",
      "program": "${command:cmake.launchTargetPath}",
      "args": [],
      "stopAtEntry": false,
      "cwd": "${command:cmake.getLaunchTargetDirectory}",
      "environment": [],
      "console": "integratedTerminal",
      "logging": {
        "engineLogging": true,
        "exceptions": true,
        "moduleLoad": true,
        "programOutput": true,
        "threadExit": true,
        "processExit": true
      },
      "symbolOptions": {
        "enabled": true,
        "searchPaths": [""],
        "searchMicrosoftSymbolServer": true,
        "cachePath": "d:/symbolcache",
        "moduleFilter": {
          "mode": "loadAllButExcluded",
          "excludedModules": ["DoNotLookForThisOne*.dll"]
        }
      }
    }
  ]
}"""


class ActionRequest:
    configs: list[str]
    archs: list[str]


class Handler:
    def __init__(self, system: str, srcdir: Path, builddir: Optional[Path]):
        self.system: str = system
        self._srcdir: Path = Path(srcdir).absolute()
        self._builddir: Path = builddir or Path(buildenv.BuildEnv(self.get_source_dir()).get_base_build_dir())

    def get_source_dir(self) -> Path:
        return Path(self._srcdir)

    def get_build_root_dir(self) -> Path:
        self._builddir.mkdir(exist_ok=True, parents=True)
        return self._builddir

    def pre_generate(self, request: ActionRequest) -> None:
        pass

    def generate(self, request: ActionRequest, extra_args: list[str]) -> None:
        pass

    def format(self, request: ActionRequest) -> None:
        pass

    def open(self, request: ActionRequest) -> None:
        pass

    def build(self, request: ActionRequest) -> None:
        pass

    def pack(self, request: ActionRequest) -> None:
        pass

    def get_permission_map(self) -> Dict[str, str]:
        return {}

    def run(self, request: ActionRequest, extra_args: list[str]) -> None:
        pass

    def generate_build_dir_for_manifest(
        self,
        _name: str,
        configfile: Path,
        gendir: Path,
        bindings: dict[str, Any] | None = None,
    ) -> tuple[Generator, dict[str, Any]]:
        config = self.load_config_as_dictionary(configfile)
        # outdir = os.path.join(self._buildenv.GetBaseBuildDir(), 'android_package')
        srcdir = configfile.parent
        self_st_time_ns = 0 if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS") else Path(__file__).stat().st_mtime_ns
        mtime_ns = max(self_st_time_ns, configfile.stat().st_mtime_ns)
        gen = generator.Generator(srcdir, gendir, mtime_ns=mtime_ns)
        appclass = config["application"]["class"]
        # config["build"].setdefault("MajorVersion", 0)
        # config["build"].setdefault("MinorVersion", 0)
        now = datetime.datetime.now()
        versiondate = f"{now.strftime('%y%j')}{int(now.hour/3)}"
        if int(versiondate[1:]) > 965535:  # noqa: PLR2004
            raise CMakeError("Version date too long. UWPs wont like that")
        config["build"].setdefault("VersionDate", versiondate)
        majorversion = int(config["build"]["majorversion"])
        minorversion = int(config["build"]["minorversion"])
        if minorversion > 10000 or majorversion > 10000:  # noqa: PLR2004
            raise CMakeError("version exceeded limit 10000")
        versiondate = config["build"]["VersionDate"]
        config["build"].setdefault("VersionFull", f"{majorversion}.{minorversion}.{versiondate[1:]}.0")
        config["build"].setdefault("VersionCode", f"{versiondate}")
        systmpldir = Path(__file__).parent / "templates" / self.system
        tmpldir = systmpldir / appclass
        if not tmpldir.is_dir():
            raise CMakeError(f"Cannot find templates for Class : {appclass} : dir : {tmpldir}")
        gen.LoadDictionary(config)
        gen.LoadDictionary(bindings or {})
        cmakeexe = externaltools.get_cmake()
        cmakeversion = subprocess.check_output([cmakeexe, "--version"]).decode().splitlines()[0].split(" ")[2].split("-")[0]
        gen.LoadDictionary(
            {
                "BuildDir": gendir.as_posix(),
                "ninjabin": externaltools.get_ninja().as_posix(),
                "cmakebin": cmakeexe.as_posix(),
                "pythonbin": Path(sys.executable).as_posix(),
                "cmakebuildtoolsdir": Path(__file__).parent.as_posix(),
                "cmakesourcedir": self.get_source_dir().as_posix(),
                "cmakeversion": cmakeversion,
            },
        )
        gen.GenerateFromTemplateDirectory(tmpldir)
        gen.GenerateImagesForManifest(self.load_config_as_dictionary(systmpldir / "images.ini"))
        gen.GenerateImagesForManifest(self.load_config_as_dictionary(systmpldir / f"{appclass}.images.ini"))
        return gen, config

    def get_app_manifests(self) -> Dict[str, Path]:
        manifests: Dict[str, Path] = {}
        quickcfgfiles = list(Path(self.get_source_dir()).glob("*config.ini"))
        if len(quickcfgfiles) == 0:
            for f in self.get_source_dir().rglob("*.manifest.ini"):
                manifests[f.name] = f
            return manifests
        quickcfg = configparser.ConfigParser()
        for quickcfgfile in quickcfgfiles:
            quickcfg.read(quickcfgfile)
            for sec in quickcfg.sections():
                quicksec = quickcfg[sec]
                if "appmanifest" not in quicksec:
                    continue
                configfile = self.get_source_dir() / quicksec["appmanifest"]
                config = self.load_config_as_dictionary(configfile)
                if self.system not in config:
                    continue
                manifests[sec] = configfile
        return manifests

    def load_config_as_dictionary(self, f: Path) -> dict[str, Any]:
        config = configparser.ConfigParser()
        if f.exists():
            config.read(str(f))
        return {s.lower(): dict(config.items(s)) for s in config.sections()}

    def rmtree(self, bdir: Path) -> None:
        def onerror(func: Callable[[Path], None], path: Path | str, _exc_info: Exception) -> None:
            path = Path(path)
            # Is the error an access error?
            if not os.access(path.as_posix(), os.W_OK):
                path.chmod(stat.S_IWUSR)
                func(path)
            else:
                raise CMakeError(f"Cannot delete {path}")

        shutil.rmtree(bdir, onexc=onerror)


cmakeconfig = {"dbg": "Debug", "rel": "RelWithDebInfo"}


class CMakeHandler(Handler):
    def __init__(
        self,
        system: str,
        srcdir: Path,
        builddir: Optional[Path] = None,
        **kargs: any,
    ):
        super().__init__(system, srcdir, builddir)
        self.toolchain_info = externaltools.detect_toolchain()
        avoid_ninja = kargs.get("avoid_ninja") or self.toolchain_info["toolchain"] == "visualstudio"
        self.generator_: Optional[str] = "Ninja" if not avoid_ninja and externaltools.get_ninja() else None

    def get_generator(self) -> str:
        return self.generator_

    def get_generator_args(self, _arch: str, _config: str) -> list[str]:
        if self.generator_ == "Ninja" and os.name == "nt" and self.toolchain_info["toolchain"] == "msvc":
            return [
                f"-DCMAKE_MAKE_PROGRAM:FILEPATH='{externaltools.get_ninja().as_posix()}'",
                f"-DCMAKE_MT:FILEPATH='{self.toolchain_info["mt"].as_posix()}'",
                f"-DCMAKE_RC_COMPILER:FILEPATH='{self.toolchain_info["rc"].as_posix()}'",
            ]
        return []

    def get_cmake_generator_args_(self, _arch: str, config: str) -> list[str]:
        return (
            [
                f"-DPython3_EXECUTABLE:FILEPATH='{Path(sys.executable).as_posix()}'",
                f"-DQuick_DIR:PATH='{(Path(__file__).parent / 'cmake').as_posix()}'",
                f"-DCMAKE_BUILD_TYPE:STR={cmakeconfig[config]}"
            ] + ( [f"-DCMAKE_MAKE_PROGRAM:FILEPATH='{externaltools.get_ninja().as_posix()}'"]
            if self.generator_ == "Ninja"
            else []))

    def _env(self):
        env = os.environ.copy()
        for k, v in self.toolchain_info["environ"].items():
            env[k] = v
        return env

    def get_build_dir_(self, arch: str, config: str) -> Path:
        bdir = self.get_build_root_dir() / f"{self.system}_{arch}_{config}"
        bdir.mkdir(exist_ok=True)
        return bdir

    def pre_generate(self, request: ActionRequest) -> None:
        super().pre_generate(request)
        srcdir = self.get_source_dir()

        def generate_vscode_workspace_settings(_arch: str, _config: str) -> None:
            (srcdir / ".vscode").mkdir(exist_ok=True)
            launch_json = json.loads(LAUNCH_JSON_VS if self.toolchain_info["toolchain"] in {"msvc", "visualstudio"} else LAUNCH_JSON_GDB)
            envvars = dict(self.toolchain_info.get("env", {}).items())

            def envvarvalue(k: str, v: list[str] | str) -> str:
                prevenvvarvalue = f"${{env:{{{k}}}}}" if sys.platform == "win32" else f"${k}"
                return f"{os.pathsep.join([Path(vv).as_posix() for vv in v])}{os.pathsep}{prevenvvarvalue}" if isinstance(v, list) else v

            envvars.setdefault("PATH", []).extend(externaltools.TOOL_PATH)
            environlist = [{"name": k, "value": envvarvalue(k, v)} for k, v in envvars.items()]
            for config in launch_json["configurations"]:
                config["environment"] = environlist
            json_merge_write(srcdir / ".vscode" / "launch.json", launch_json)
            newcontentjson: Dict[str, Any] = {}
            newcontentjson["python.defaultInterpreterPath"] = Path(sys.executable).as_posix()
            newcontentjson["terminal.integrated.env.windows"] = {
                "PATH": os.pathsep.join([*(fpath.as_posix() for fpath in envvars["PATH"]) ,"${env:PATH}"]),
            }
            settingskeymap = {"cmake": "cmake.cmakePath", "deno": "deno.path", "ninja": None, "clang-format": "C_Cpp.clang_format_path"}
            for k, v in externaltools.TOOL_PATHS.items():
                if k in settingskeymap:
                    if settingskeymap[k]:
                        newcontentjson[settingskeymap[k]] = v.as_posix()
                else:
                    raise CMakeError(f"Unknown configuration for tool {k}")
            json_merge_write(srcdir / ".vscode" / "settings.json",newcontentjson )

        def generate_vs_cmake_presets(arch: str, config: str) -> None:
            bdir = self.get_build_dir_(arch, config)
            file = srcdir / "CMakeUserPresets.json"
            origcontentjson: Dict[str, Any] = json.loads(file.open(mode="r", encoding="utf-8-sig").read()) if file.exists() else {}
            newcontentjson: Dict[str, Any] = json.loads(file.open(mode="r", encoding="utf-8-sig").read()) if file.exists() else {}
            newcontentjson.setdefault("version", 6)
            newcontentjson.setdefault("configurePresets", [])
            configname = arch + "-" + config
            sobj = next(
                (entry for entry in newcontentjson["configurePresets"] if entry.get("name", "") == configname),
                None,
            )
            obj = sobj or {}
            obj["name"] = configname
            if self.generator_:
                obj["generator"] = self.generator_  # Only ninja is supported self.get_generator()
            obj["binaryDir"] = str(bdir)
            obj.setdefault("cacheVariables", {})
            genargs = self.get_cmake_generator_args_(arch, config) + self.get_generator_args(arch, config)
            for arg in genargs:
                k, v = arg.split("=", 1)
                if not k.startswith("-D"):
                    raise CMakeError(f"Invalid generator argument {arg}")
                obj["cacheVariables"][k[2:].split(":", 1)[0]] = v
            # obj["cacheVariables"]["Python3_EXECUTABLE"] = Path(sys.executable).as_posix()
            # obj["cacheVariables"]["Quick_DIR"] = (Path(__file__).parent / "cmake").as_posix()
            envvars = dict(self.toolchain_info.get("env", {}).items())
            envvars.setdefault("PATH", []).extend(externaltools.TOOL_PATH)
            obj.setdefault("environment", {})
            for k, v in envvars.items():
                if isinstance(v, str):
                    obj["environment"][k] = v
                elif isinstance(v, list):
                    obj["environment"][k] = f"{os.pathsep.join([Path(vv).as_posix() for vv in v])}{os.pathsep}$penv{{{k}}}"
            if sobj is None:
                newcontentjson["configurePresets"].append(obj)
            newcontentjsonstr = json.dumps(newcontentjson, cls=externaltools.CustomEncoder, indent=2)
            origcontentjsonstr = json.dumps(origcontentjson, cls=externaltools.CustomEncoder, indent=2)
            if newcontentjsonstr != origcontentjsonstr:
                file.write_text(newcontentjsonstr, encoding="utf-8-sig")

        for arch in request.archs:
            for config in request.configs:
                generate_vscode_workspace_settings(arch, config)
                generate_vs_cmake_presets(arch, config)

    def generate(self, request: ActionRequest, extra_args: list[str]) -> None:
        for arch in request.archs:
            for config in request.configs:
                command = [externaltools.get_cmake().as_posix()]
                cmakegen = self.get_generator()
                if cmakegen:
                    command.extend(["-G", cmakegen])
                command = command + self.get_cmake_generator_args_(arch, config) + self.get_generator_args(arch, config) + extra_args
                command.append(str(self.get_source_dir()))
                subprocess.check_call(command, cwd=self.get_build_dir_(arch, config), env=self._env())

    def open(self, _request: ActionRequest) -> None:
        codeexe = shutil.which("code")
        if codeexe is not None:
            subprocess.check_call([codeexe, self.get_source_dir()], env=self._env())
        elif sys.platform == "win32":
            subprocess.check_call(["start", "devenv", self.get_source_dir()], shell=True, env=self._env())  # noqa: S607, S602
        else:
            raise CMakeError("Cannot open the project")

    def format(self, _request: ActionRequest) -> None:
        subprocess.check_call(
            [
                sys.executable,
                (Path(__file__).parent / "format.cmake/git-clang-format.py").as_posix(),
                f"--binary={externaltools.get_clang_format().as_posix()}",
                "--extensions=cpp,h,cxx",
            ],
            cwd=self.get_source_dir(),
            env=self._env(),
        )

    def build(self, request: ActionRequest) -> None:
        for arch in request.archs:
            for config in request.configs:
                subprocess.check_call(
                    [
                        externaltools.get_cmake().as_posix(),
                        "--build",
                        ".",
                        "-j8",
                        "--config",
                        cmakeconfig[config],
                    ],
                    cwd=self.get_build_dir_(arch, config),
                    env=self._env(),
                )

    def package(self, request: ActionRequest) -> None:
        for arch in request.archs:
            for config in request.configs:
                subprocess.check_call(
                    [
                        externaltools.get_cmake().as_posix(),
                        "--build",
                        ".",
                        "--target",
                        "package",
                    ],
                    cwd=self.get_build_dir_(arch, config),
                    env=self._env(),
                )

        for arch in request.archs:
            for config in request.configs:
                for fp in os.scandir(self.get_build_dir_(arch, config)):
                    if fnmatch.fnmatch(fp.name, "*.zip"):
                        m = re.search(r"(.*)_(.*)-([0-9\.]+)-(.*)-(.*)\.zip", fp.name)
                        if m:
                            garchroot = self.get_build_root_dir() / m.group(5) / arch
                            garchroot.mkdir(parents=True, exist_ok=True)
                            shutil.unpack_archive(fp.path, extract_dir=garchroot)
                            if (garchroot / "manifestpath.txt").exists():
                                shutil.move(
                                    (garchroot / "manifestpath.txt"),
                                    self.get_build_root_dir() / m.group(5) / "manifestpath.txt",
                                )
        self.package_all_archs(request)

    def package_all_archs(self, request: ActionRequest) -> None:
        pass

    def run(self, request: ActionRequest, extraargs: list[str]) -> None:
        for arch in request.archs:
            for config in request.configs:
                subprocess.check_call(extraargs, cwd=self.get_build_dir_(arch, config), env=self._env())

    def test(self, request: ActionRequest) -> None:
        for arch in request.archs:
            for config in request.configs:
                subprocess.check_call(
                    [
                        externaltools.get_ctest().as_posix(),
                        "-C",
                        cmakeconfig[config],
                        "--verbose",
                    ],
                    cwd=self.get_build_dir_(arch, config),
                    env=self._env(),
                )

    def clean(self, request: ActionRequest) -> None:
        for arch in request.archs:
            for config in request.configs:
                bdir = self.get_build_dir_(arch, config)
                if bdir.is_dir():
                    self.rmtree(bdir)
