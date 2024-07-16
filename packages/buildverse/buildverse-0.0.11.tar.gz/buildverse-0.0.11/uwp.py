import pathlib
import shutil
import subprocess
import sys
from typing import Mapping, Optional

import cmake
import externaltools

# import generator


class ExeHandler(cmake.CMakeHandler):
    def __init__(self, srcdir: pathlib.Path, builddir: Optional[pathlib.Path] = None, **kargs: any):
        super().__init__("exe", srcdir, builddir, **kargs)

    def get_generator_args(self, arch: str, config: str) -> list[str]:
        if self.generator_ is not None and "Visual" in self.generator_:
            archstr = {"x86": "Win32"}.get(arch) or arch
            return ["-T", f"host={externaltools.DefaultArch}", "-A", archstr]
        return super().get_generator_args(arch, config)

    def package_all_archs(self, _request: cmake.ActionRequest) -> None:
        return
        # pylint: disable=pointless-string-statement, unreachable
        """
        for fp in os.scandir(packageroot):
            d = fp.path
            manifest = None
            if os.path.exists(os.path.join(d, "manifestpath.txt")):
                with open(os.path.join(d, "manifestpath.txt")) as fd:
                    manifest = fd.read()
            if not manifest:
                continue
            manifest = manifest if os.path.isabs(manifest) else os.path.join(self._reporoot, manifest)
            if not os.path.exists(manifest):
                raise Exception("cannot find manifest", manifest)
            for arch in archs:
                d = os.path.join(fp.path, arch)
                config = configparser.ConfigParser()
                config.read(manifest)
                appxdir = d
                os.makedirs(os.path.expanduser(appxdir), exist_ok=True)
                g = generator.Generator(config, appxdir, os.path.dirname(manifest))
                g.GenerateFiles({"AppxManifest.xml": Win32AppxManifestTemplate})
                g.GenerateImagesFromSpec("Icon", IMAGES)
                cert = os.path.join(os.path.dirname(manifest), "cert.pfx")
                if not os.path.exists(cert):
                    raise Exception("cannot find cert:", cert)
                packfile = os.path.join(packageroot,  config["Microsoft"]["Name"] + "_" + arch + ".msix")
                if os.path.exists(packfile):
                    os.unlink(packfile)
                cmake.run_command(["makeappx", "pack", "/o", "/p", packfile, "/d", appxdir], vsdevshellarch=arch, cwd=appxdir)
                cmake.run_command(["signtool", "sign", "/fd", "SHA256", "/f", cert, "/p",
                                 "<password>", packfile], vsdevshellarch=arch, cwd=appxdir)"""


class UWPCMakeHandler(cmake.CMakeHandler):
    def __init__(self, srcdir: pathlib.Path, builddir: Optional[pathlib.Path] = None, **kargs: Mapping[str, any]):
        super().__init__("uwp", srcdir, builddir, **kargs)

    def get_generator_args(self, arch: str, _config: str) -> list[str]:
        return [
            "-DCMAKE_SYSTEM_NAME=WindowsStore",
            "-DCMAKE_SYSTEM_VERSION=10.0",
            "-T",
            f"host={externaltools.DefaultArch}",
            "-A",
            {"x86": "Win32"}.get(arch) or arch,
        ]


class UWPHandler(cmake.Handler):
    def __init__(self, srcdir: pathlib.Path, builddir: Optional[pathlib.Path] = None, **_kargs: Mapping[str, any]):
        super().__init__("uwp", srcdir, builddir)
        self._rootbuilddir = (builddir or self.get_build_root_dir()) / "uwp"
        self._pregendir = self._rootbuilddir / "app"
        self._basebuilddir = self._rootbuilddir / "build"
        self.cmakehandlers: dict[str, UWPCMakeHandler] = {}

    def get_permission_map(self) -> dict[str, str]:
        return {
            "internet": '<Capability Name="internetClient" /><Capability Name="internetClientServer"/>',
            "bluetooth": '<DeviceCapability Name="bluetooth"/>',
            "ble-server": "",
            "location": '<DeviceCapability Name="location"/>',
            "gyroscope": "",
            "usb": '<DeviceCapability Name="lowLevel"/>',
            "in-app-purchases": "",
            "extended-execution": "",  # 1TODO(ankurv):  - Add extended execution capability
        }

    def pre_generate(self, _request: cmake.ActionRequest) -> None:
        for name, configfile in self.get_app_manifests().items():
            appsrcdir = self._pregendir / name
            self.cmakehandlers[name] = UWPCMakeHandler(self.get_source_dir(), self._rootbuilddir)
            self.generate_build_dir_for_manifest(name, configfile, appsrcdir)
            cert = appsrcdir / f"{name}.pfx"
            winmd = appsrcdir / "App.winmd"
            shutil.copyfile(configfile.parent / "cert.pfx", cert)
            shutil.copyfile(pathlib.Path(__file__).parent / "templates" / "uwp" / "App.winmd", winmd)

    def generate(self, request: cmake.ActionRequest, extra_args: list[str]) -> None:
        for handler in self.cmakehandlers.values():
            handler.generate(request, extra_args)

    def format(self, request: cmake.ActionRequest) -> None:
        for handler in self.cmakehandlers.values():
            handler.format(request)

    def open(self, request: cmake.ActionRequest) -> None:
        for handler in self.cmakehandlers.values():
            handler.open(request)

    def build(self, request: cmake.ActionRequest) -> None:
        for name, handler in self.cmakehandlers.items():
            handler.build(request)
            configmapping = {"dbg": "Debug", "rel": "Release"}
            subprocess.check_call(
                [
                    str(externaltools.detect_vspath("msbuild")),
                    "-t:restore",
                    "-p:RestorePackagesConfig=true",
                ],
                cwd=(self._pregendir / name),
            )
            for config in request.configs:
                for arch in request.archs:
                    subprocess.check_call(
                        [
                            str(externaltools.detect_vspath("msbuild")),
                            "/p:Configuration=" + configmapping[config],
                            "/p:Platform=" + arch,
                            "App.sln",
                        ],
                        cwd=(self._pregendir / name),
                    )

    def clean(self, _request: cmake.ActionRequest) -> None:
        if self._rootbuilddir.exists():
            self.rmtree(self._rootbuilddir)

    def package(self, request: cmake.ActionRequest) -> None:
        self.pre_generate(request)
        outdir = self._rootbuilddir
        for name, handler in self.cmakehandlers.items():
            handler.build(request)
            subprocess.check_call(
                [
                    str(externaltools.detect_vspath("msbuild")),
                    "-t:restore",
                    "-p:RestorePackagesConfig=true",
                ],
                cwd=(self._pregendir / name),
            )
            subprocess.check_call(
                [
                    str(externaltools.detect_vspath("msbuild")),
                    "/p:Configuration=Release",
                    "/p:AppxBundlePlatforms=" + "|".join(list(request.archs)),
                    "/p:AppxPackageDir=MyPackages",
                    "/p:AppxBundle=Always",
                    "/p:UapAppxPackageBuildMode=StoreUpload",
                    "/p:AppxPackageSigningEnabled=true",
                    "/p:PackageCertificateKeyFile=" + f"{name}.pfx",
                    "App.sln",
                ],
                cwd=(self._pregendir / name),
            )
            appblddir = self._basebuilddir / name
            appsrcdir = self._pregendir / name
            cert = appsrcdir / f"{name}.pfx"
            for msix in list(appblddir.rglob(f"{name}UWP*.msix")):
                command = [
                    str(externaltools.detect_vspath("signtool")),
                    "sign",
                    "/fd",
                    "SHA256",
                    "/p",
                    "<password>",
                    "/f",
                    str(cert),
                    str(msix),
                ]
                subprocess.check_call(command, cwd=outdir)
                # subprocess.check_call([self.MAKEAPPX_BINARY, "pack", "/o", "/p", packfile, "/d", os.path.dirname(f)], cwd=appxdir)
                shutil.copyfile(msix, outdir)
