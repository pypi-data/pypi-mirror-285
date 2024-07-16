import argparse
import datetime
import fnmatch
import itertools
import json
import multiprocessing
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence

import configenv
import externaltools
import git


class VcpkgLock:
    def __init__(self):
        self.lock = multiprocessing.Lock()
        self.lock.acquire()

    def __del__(self):
        self.lock.release()


# test Mode
# Production Mode
# Checkout and build https://github.com/ankurvdev/vcpkg lkg_patched

# Scenario 1
# vcpkg.py --test default
#   * Reuses config:VCPKG_ROOT if environment defined
#   * uses vcpkg.test<date> if no config:VCPKG_ROOT defined
# vcpkg.py ~/build/vcpkg.py --test default --marklkg --commit a267ab118c09f56f3dae96c9a4b3410820ad2f0b
#   * Reuses config:VCPKG_ROOT
#   * does not create a fresh


VCPKG_KNOWN_FAILURES = {
    "osgearth:*-android",
    "osgearth:*-mingw*",
    "osgearth:*-uwp*",
    "curses:*-uwp*",
    "rtlsdr:*-uwp*",
    "rtlsdr:*-emscripten*",
    "libspatialite:*-emscripten*",
}

TEST_PORTS_ALL_TRIPLETS = {
    "qtbase",
    "curses",
    "stencil",
    "rtlsdr",
    "libspatialite",
    "asio",
    "re2c",
    "avcpp",
    "boost-beast",
}

TEST_PORT_TRIPLET = {
        "llvm:x64-linux"
}
TEST_TRIPLETS = {
    "arm-neon-android",
    "arm64-android",
    "x86-android",
    "x64-android",
    "wasm32-emscripten",
    "x64-windows-static-md",
    "x64-linux",
}


class VcpkgError(Exception):
    pass


class Vcpkg:
    def __init__(
        self,
        vcpkg_root: str | None,
        triplet: str | None = None,
        host_triplet: str | None = None,
        commit: str | None = None,
    ):
        # Try to clone from upstream
        # Add myfork as a remote
        # Do not want to make root for scenario 1
        self.triplet = triplet
        self.host_triplet = host_triplet or "auto"
        self.commit = commit
        self.rourl = "https://github.com/ankurvdev/vcpkg.git"
        self.rwurl = "git@github.com:ankurvdev/vcpkg"
        self.lock = VcpkgLock()
        self.mode = "unknown"  # Could be git or buildcache
        self.vcpkg_root = Path(vcpkg_root) if vcpkg_root else None
        self.envvars: dict[str, str] = {"VCPKG_BINARY_SOURCES": "clear"}
        self._git = git.Git(root=self.vcpkg_root)
        if os.environ.get("VCTOOLSINSTALLDIR", None) and shutil.which("cl"):
            vsvars = [
                "VCTOOLSINSTALLDIR",
                "PATH",
                "CL",
                "LIB",
                "INCLUDE",
                "SDK_ARCH",
                "SDK_INCLUDE",
                "SDK_LIBS",
                "SDK_VERSION",
                "MSVC_VERSION",
            ]
            self.envvars["VCPKG_KEEP_ENV_VARS"] = ";".join(vsvars)
            for vsvar in vsvars:
                if os.environ.get(vsvar, None):
                    self.envvars[vsvar] = os.environ[vsvar]
        self._init_pass_2_done = False
        if sys.platform == "linux" and os.uname().machine in ("armv7l", "aarch64"):  # pylint: disable=E1101
            self.envvars["VCPKG_FORCE_SYSTEM_BINARIES"] = "1"

    def _head_has_all_patches(self) -> bool:
        for branch in self._get_patch_branches():
            if self._git.cmd(["merge-base", "HEAD", branch]).strip() != self._git.commit_hash(branch):
                sys.stderr.write(f"HEAD does not contain Branch {branch} ")
                return False
        return True

    def _create_work_branch_with_all_patches(self) -> None:
        i = 0
        while True:
            workbranch = datetime.datetime.now().strftime("%Y%m%d") + "_" + str(i)
            if workbranch not in self._git.cmd(["branch"]):
                break
            i = i + 1

        self._git.cmd(["fetch", "--all", "--prune"])
        if self.commit is None:
            self._git.cmd(["checkout", "--", "."])
            self._git.cmd(["clean", "-f", "-d"])
            if workbranch not in self._git.cmd(["branch"]):
                self._git.cmd(["checkout", "origin/lkg_patched", "-b", workbranch])
            self._git.cmd(["checkout", workbranch])
            for b in self._get_patch_branches():
                self._git.cmd(["merge", b])
        else:
            currenthead = self._git.commit_hash("HEAD")
            expectedhead = self._git.commit_hash(self.commit)
            if currenthead != expectedhead:
                self._git.cmd(["checkout", self.commit, "-b", workbranch])
        # Merge in both cases bacause we really dont want to run without these patches.
        # They're usually no-op if already merged
        for b in self._get_patch_branches():
            self._git.cmd(["merge", b])

    def _make_all_triplets_release_only(self) -> None:
        tripletdir = self._git.root / "triplets"
        for tripletfile in tripletdir.rglob("*.cmake"):
            sys.stderr.write(f"Patching {tripletfile} for Release only builds\n")
            with tripletfile.open("a") as tripletfd:
                tripletfd.write("set(VCPKG_BUILD_TYPE release)\n")

    def _validate_repo(self) -> Path:
        vcpkg_root = self.locate_vcpkg_root()

        if self.commit is not None and self._git.commit_hash("HEAD") == self._git.commit_hash(self.commit):
            # Quick validation . Complete
            return vcpkg_root
        self._git.sync()
        if not self._head_has_all_patches():
            self._create_work_branch_with_all_patches()
        is_vcpkg_build_type_release_only = os.environ.get("VCPKG_BUILD_TYPE_RELEASE_ONLY", "0")
        boolmap = {
            "true": True,
            "false": False,
            "y": True,
            "n": False,
            "1": True,
            "0": False,
            "yes": True,
            "no": False,
            "t": True,
            "f": False,
        }
        if boolmap[is_vcpkg_build_type_release_only]:
            self._make_all_triplets_release_only()

        if not vcpkg_root:
            raise VcpkgError("Cannot initialize vcpkg exe")
        subprocess.check_output(
            [
                str(self._vcpkgexe()),
                "--disable-metrics",
                "remove",
                "--outdated",
                "--recurse",
            ],
            env=os.environ.copy() | self.envvars,
            cwd=vcpkg_root,
        )

        return vcpkg_root

    def _get_patch_branches(self) -> list[str]:
        return self._git.query_branches(r"remotes/((myfork|origin)/ankurv/(.+))$")

    def _get_patch_topics(self) -> list[str]:
        branches: list[str] = []
        for b in self._git.cmd(["branch", "-a"]).splitlines():
            bstripped = b.strip()
            rematch = re.search(r"remotes/((myfork|origin)/ankurv/(.+))$", bstripped)
            if not rematch:
                continue
            branches.append(rematch.group(3))
        return branches

    def _vcpkgexe(self) -> Path:
        path = shutil.which("vcpkg", path=self.locate_vcpkg_root())
        if path is None:
            raise VcpkgError(f"Cannot find vcpkg exe in {self.locate_vcpkg_root()}")
        return Path(path).resolve()

    def apply_patches(self) -> Path:
        return self._validate_repo()

    def _clear_logs(self, pkgs: list[str]) -> None:
        for p in pkgs:
            for f in self._get_logs(p):
                f.unlink()

    def _get_logs(self, name: str) -> list[Path]:
        return list((Path(self.locate_vcpkg_root()) / "buildtrees" / name).rglob("*.log"))

    def locate_vcpkg_root(self) -> Path:
        vcpkg_root = self.vcpkg_root
        if not vcpkg_root or vcpkg_root == Path():
            vcpkg_root = Path(configenv.ConfigEnv(None).GetConfigPath("VCPKG_ROOT", make=True))
        if not self._init_pass_2_done:
            self._git.set_root(vcpkg_root)
            if not vcpkg_root.is_dir() and not vcpkg_root.is_absolute():
                raise VcpkgError(f"Refusing to initial non-absolute vcpkg-root dir: {vcpkg_root}")
            if not (vcpkg_root / ".git").is_dir():
                if vcpkg_root.exists() and len(list(os.scandir(str(vcpkg_root)))) != 0:
                    raise VcpkgError(f"Refusing to initial non-empy vcpkg-root dir: {vcpkg_root}")
                subprocess.check_call([self._git.git, "clone", "-b", "lkg_patched", self.rourl, vcpkg_root.name], cwd=vcpkg_root.parent)
            if not (vcpkg_root / "scripts/buildsystems/vcpkg.cmake").exists():
                raise VcpkgError(f"Invalid vcpkg_root : {vcpkg_root}")
            self._git.sync()

            self.mode = "git"
            if shutil.which("vcpkg", path=vcpkg_root) is None:
                bootstrap = "bootstrap-vcpkg.bat" if sys.platform == "win32" else "./bootstrap-vcpkg.sh"
                subprocess.check_call([bootstrap], shell=True, cwd=vcpkg_root, env=os.environ.copy() | self.envvars)  # noqa: S602
            self._init_pass_2_done = True
        return vcpkg_root

    def detect_host_triplet(self) -> str:
        if sys.platform == "win32":
            info = externaltools.detect_toolchain()
            if info["toolchain"] == "msvc":
                return f"{info['host_arch']}-msvc-static-md"
            if info["toolchain"] == "mingw":
                return f"{info['host_arch']}-mingw-static"
            if info["toolchain"] == "visualstudio":
                return f"{info['host_arch']}-windows-static-md"
        elif sys.platform == "linux":
            if os.uname().machine == "x86_64":
                return "x64-linux"
            if os.uname().machine == "aarch64":
                return "arm64-linux"
        raise VcpkgError(f"Unknown Platform {sys.platform}")

    def _download_ports_with_triplets(
        self,
        ports: list[str],
        runtime_triplet: str,
        host_triplet: str,
        keep_going: bool,
        editable: bool,
    ) -> subprocess.CompletedProcess[any]:
        envvars: dict[str, str] = self.envvars
        paths: set[Path] = set()
        environ = os.environ.copy()

        if "android" in runtime_triplet:
            externaltools.init_toolchain("android", environ)
        if "wasm32" in runtime_triplet:
            environ.pop("PKG_CONFIG_LIBDIR", "")  # Interferes with vcpkg
            externaltools.init_toolchain("emscripten", environ)
        if "mingw" in runtime_triplet:
            externaltools.init_toolchain("mingw", environ)

        self._clear_logs(ports)
        if paths:
            environ = externaltools.add_to_path(paths, environ)
        if envvars:
            for envvarname, envvarval in envvars.items():
                sys.stderr.write(f"{envvarname} = {envvarval}\n")
                environ[envvarname] = envvarval
        command = [
            self._vcpkgexe().as_posix(),
            f"--host-triplet={host_triplet}",
            f"--triplet={runtime_triplet}",
            "--disable-metrics",
            "--allow-unsupported",
            "install",
            *ports,
            "--recurse",
        ]
        if keep_going:
            command.append("--keep-going")
        if editable:  # Dependency ports arent editable
            command.append("--editable")
        sys.stderr.write(f'Command: {" ".join(command)}')
        return subprocess.run(
            command,
            env=environ,
            capture_output=True,
            cwd=self.locate_vcpkg_root(),
            check=False,
        )

    def _download(self, ports: str | list[str], keep_going: bool = False, editable: bool = False) -> None:  # noqa: C901, PLR0912
        installports: list[str] = []
        if isinstance(ports, str):
            ports = filter(len, ports.split(","))
        requested_triplets = {(p + ":").split(":")[1] for p in ports}

        # Try to match host_triplet with runtime_triplet
        host_triplet = self.host_triplet
        if host_triplet == "auto" and sys.platform == "win32":
            if "mingw" in requested_triplets:
                host_triplet = f"{externaltools.DefaultArch}-mingw-static"
            if "msvc" in requested_triplets:
                host_triplet = f"{externaltools.DefaultArch}-msvc-static-md"
            if "windows" in requested_triplets:
                host_triplet = f"{externaltools.DefaultArch}-windows-static-md"

        if host_triplet == "auto":
            host_triplet = self.detect_host_triplet()

        default_triplet = self.triplet or host_triplet

        def is_known_failure(port: str) -> bool:
            return any(fnmatch.fnmatch(port, knownfailures) for knownfailures in VCPKG_KNOWN_FAILURES)

        installports = [p.split(":") for p in [f"{p}:{default_triplet}" if ":" not in p else p for p in ports] if not is_known_failure(p)]
        requests = {host_triplet: []}  # So the host triplet executes first
        for port in installports:
            requests.setdefault(port[1], []).append(port[0])
        results = {
            triplet: self._download_ports_with_triplets(triplet_ports, triplet, host_triplet, keep_going, editable)
            for triplet, triplet_ports in requests.items()
            if len(triplet_ports) > 0
        }
        errresults = {triplet: r for triplet, r in results.items() if r.returncode != 0}
        errortriplets: list[str] = []
        for rslt in errresults.values():
            errors = rslt.stdout.decode()
            for line in errors.splitlines():
                m = re.match(r"Error: Building package (.*) failed with: BUILD_FAILED", line)
                if not m:
                    continue
                errortriplets += [m.group(1)]
            for t in errortriplets:
                name, _arch = t.split(":")
                logfiles: list[Path] = self._get_logs(name)
                logfiles.sort(key=lambda x: x.stat().st_mtime_ns)
                for p in logfiles:
                    sys.stderr.write(f"\nFailed {t}: Log: {p!s}\n\n")
                    with p.open("r") as f:
                        shutil.copyfileobj(f, sys.stderr)
            if len(errortriplets) == 0:
                sys.stderr.write(rslt.stdout.decode())
                sys.stderr.write(rslt.stderr.decode())

        if len(errresults):
            raise VcpkgError(f"Error Triplets: {errresults.keys()}")

    def download(self, ports: str | list[str]) -> None:
        self.locate_vcpkg_root()
        if self.mode == "buildcache":
            sys.stderr.write("Skipping Download in Cached Mode")
            return
        self._download(ports)

    def _update_topic_branch(self, tag: str, mastercommit: str, topic: str) -> str | None:
        current_commit = self._git.commit_hash("HEAD")
        mastercommit = self._git.commit_hash(mastercommit)
        oldbranch = f"origin/ankurv/{topic}"
        newbranch = f"{tag}/ankurv/{topic}"
        if self._git.branch_has(newbranch, mastercommit):
            return None
        if self._git.try_get_commit_hash(newbranch) is not None:
            self._git.checkout(newbranch)
        self._git.checkout(self._git.commit_hash("HEAD"))
        self._git.merge_branch(oldbranch)
        self._git.merge_branch(mastercommit, rebase_squash=False)
        self._git.delete_branch(newbranch)
        self._git.create_branch(newbranch, self._git.commit_hash("HEAD"))
        self._git.checkout(current_commit)
        return newbranch

    def test(  # noqa: PLR0913
        self,
        tag: str,
        ports: list[str],
        commit: str = "origin/master",
        keep_going: bool = False,
        editable: bool = False,
        push: str = "confirm",
        skip_patches:str|None = None
    ) -> None:
        skip_patches = skip_patches.split(',') if skip_patches is not None else []
        portlist: list[str] = []
        if len(ports) == 0 or ports == ["default"]:
            defaultlist = TEST_PORTS_ALL_TRIPLETS
            defaulttriplets = TEST_TRIPLETS
            filterout = "linux" if sys.platform == "win32" else "windows"
            defaulttriplets = list(filter(lambda x: filterout not in x, TEST_TRIPLETS))
            portlist = [":".join(t) for t in itertools.product(defaultlist, defaulttriplets)] + list(TEST_PORT_TRIPLET)
            sys.stderr.write(" ".join(portlist))
        self.vcpkg_root = self.vcpkg_root or Path("vcpkg.test" + datetime.datetime.now().strftime("%Y%m%d")).absolute()
        self.vcpkg_root = self.locate_vcpkg_root()
        self._git.set_root(self.vcpkg_root)
        self._git.sync()
        if not self._git.has(commit):
            self._git.checkout(commit)
        # Check if we're on some branch or just a orphaned commit
        currentbranch = self._git.branch_name_for_commit("HEAD")
        if currentbranch == "HEAD":
            currentbranch = self._git.commit_hash(currentbranch)

        lkgcommitbranch = f"{tag}/lkg_commit"
        if self._git.try_get_commit_hash(lkgcommitbranch) is None:
            self._git.create_branch(lkgcommitbranch, commit)
        lkgcommit = self._git.commit_hash(lkgcommitbranch)

        topics = [topic for topic in self._get_patch_topics() if topic not in skip_patches]
        topicbranches = [self._update_topic_branch(tag, lkgcommit, topic) for topic in topics]
        topicbranches = self._git.query_branches(f"{tag}/ankurv/(.+)$")
        for branch in topicbranches:
            self._git.merge_branch(branch)
        self._download(portlist, keep_going=keep_going, editable=editable)
        if push == "confirm" and input("Do you want to push the changes?").lower() in {"y", "yes", "t", "true", "1"}:
            self.test(tag, ports, commit, keep_going, editable, "yes")
            return
        if push != "yes":
            return
        self._git.cmd(["config", "remote.origin.url", self.rwurl])

        for topic in topics:
            newbranch = f"{tag}/ankurv/{topic}"
            self._git.checkout(newbranch)
            self._git.merge_branch(lkgcommit, rebase_squash=True)

        lkgpatchedbranch = f"{tag}/lkg_patched"
        self._git.delete_branch(lkgpatchedbranch)
        self._git.create_branch(lkgpatchedbranch, lkgcommit)
        for topic in topics:
            self._git.merge_branch(f"{tag}/ankurv/{topic}", rebase_squash=False)

        branches = ["lkg_commit", "lkg_patched", *[f"ankurv/{topic}" for topic in topics]]
        for branch in branches:
            self._git.delete_branch(branch)
            self._git.create_branch(
                branch,
                f"{tag}/{branch}",
            )

        self._git.cmd(["push", "origin", "--force", "--set-upstream", *branches, *[f"{tag}/ankurv/{topic}" for topic in topics]])

    def remove(self, patterns: list[str]) -> None:
        ports: list[str] = [p for p in self.query() for pattern in patterns if fnmatch.fnmatch(p, pattern)]
        sys.stderr.write(f"Removing ports {ports}\n")
        subprocess.check_call(
            [self._vcpkgexe(), "--disable-metrics", "remove", *ports, "--recurse"],
            cwd=self.locate_vcpkg_root(),
        )

    def clean(self, tripletname: str) -> None:
        pass

    def query(self) -> list[str]:
        self.locate_vcpkg_root()
        if self.mode == "buildcache":
            return []
        listjson = subprocess.check_output(
            [str(self._vcpkgexe()), "--disable-metrics", "list", "--x-json"],
            cwd=self.locate_vcpkg_root(),
            env=os.environ.copy() | self.envvars,
        )
        listobj = json.loads(listjson)
        return listobj.keys()

    @staticmethod
    def create_arg_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        parser.add_argument("--host-triplet", type=str, default=None, help="Host Triplet")
        parser.add_argument("--triplet", type=str, default=None, help="Triplet")
        parser.add_argument("--root", type=str, default=None, help="Root")
        parser.add_argument("--commit", type=str, default=None, help="Commit")
        parser.add_argument("--apply-patches", action="store_true", default=False, help="Apply patches")
        parser.add_argument("--keep-going", action="store_true", default=False, help="Keep Going")
        parser.add_argument("--editable", action="store_true", default=False, help="Editable")
        parser.add_argument("--download", type=str, default=None, help="Ports")
        parser.add_argument("--test", type=str, default=None, help="Ports")
        parser.add_argument("--skip-patches", type=str, default=None, help="Ports")
        parser.add_argument("--marklkg", type=str, default=None, help="Install")
        parser.add_argument("--export", type=str, default=None, help="Ports")
        parser.add_argument("--remove", type=str, default=None, help="Ports to remove")
        parser.add_argument("--list", type=str, default=None, help="Where to list the ports")
        return parser

    @staticmethod
    def arg_handler(args: Sequence[str] | None, _extra: list[str]) -> None:
        args.root = Path(os.path.expandvars(args.root)).expanduser() if args.root else None
        vcpkger = Vcpkg(args.root, args.triplet, host_triplet=args.host_triplet, commit=args.commit)

        def portsplit(ports: str | list[str]) -> list[str]:
            if ports is None:
                return []
            if isinstance(ports, str):
                return str(ports).split(",")
            return list(ports)

        if args.apply_patches:
            vcpkger.apply_patches()
            sys.stdout.write(vcpkger.locate_vcpkg_root().as_posix() + "\n")

        if args.remove:
            vcpkger.remove(portsplit(args.remove))

        if args.test:
            vcpkger.test(
                args.test,
                portsplit(args.download or "default"),
                commit=(args.commit or "origin/master"),
                keep_going=args.keep_going,
                editable=args.editable,
                skip_patches=args.skip_patches
            )
            return

        if args.download:
            vcpkger.download(portsplit(args.download))

        if args.list is not None:
            if args.list == "-":
                sys.stderr.write("\n".join(vcpkger.query()) + "\n")
            else:
                Path(args.list).write_text("\n".join(vcpkger.query()), encoding="utf-8")


if __name__ == "__main__":
    # Use Cases
    # 1. New machine vcpkg_cache : python Vcpkg.py --download "port" --buildcache <name>
    # 2. New machine vcpkg_root : python Vcpkg.py --download "port"
    # 3. test new build python Vcpkg.py --test
    # 4. Rebase python Vcpkg.py --test --marklkg --commit=<>

    Vcpkg.arg_handler(
        Vcpkg.create_arg_parser(argparse.ArgumentParser(description="Loading Script")).parse_args(),
        [],
    )
