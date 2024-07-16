import argparse
import ctypes
import functools
import lzma
import os
import platform
import re
import subprocess
import sys
import tarfile
import urllib.request
from ctypes import c_char_p, c_int, c_ulong, c_void_p
from ctypes.wintypes import DWORD, HANDLE, HINSTANCE, HKEY, HWND
from pathlib import Path

import externaltools

# LINK = "https://kojipkgs.fedoraproject.org/packages/Fedora-Container-Base/39/20231106.0/images/Fedora-Container-Base-39-20231106.0.x86_64.tar.xz"


# Compare version strings
def compare_version(version1: str, version2: str):
    version1 = version1.split(".")
    version2 = version2.split(".")
    for i in range(min(len(version1), len(version2))):
        if version1[i] < version2[i]:
            return -1
        elif version1[i] > version2[i]:
            return 1
    if len(version1) < len(version2):
        return -1
    elif len(version1) > len(version2):
        return 1
    else:
        return 0


def is_version(version: str):
    if re.fullmatch(r"^\d+(\.[n\d+])*$", version) is None:
        return False
    return True


def download_image(download_dir: Path) -> Path:
    download_dir.mkdir(parents=True, exist_ok=True)
    download_file = download_dir / "fedora.tar.xz"
    if download_file.exists():
        return download_file
    urls = externaltools.HTMLUrlExtractor("https://kojipkgs.fedoraproject.org/packages/Fedora-Container-Base/").urls
    urls = {version[0:-1]: url for url, version in urls.items() if version[-1] == "/" and is_version(version[0:-1])}
    max_version = sorted(urls.keys(), key=functools.cmp_to_key(compare_version))[-1]
    urls = externaltools.HTMLUrlExtractor(urls[max_version]).urls
    urls = {version[0:-1]: url for url, version in urls.items() if version[-1] == "/" and is_version(version[0:-1])}
    max_version = sorted(urls.keys(), key=functools.cmp_to_key(compare_version))[-1]
    urls = externaltools.HTMLUrlExtractor(urls[max_version] + "/images/").urls
    expression = ".*Fedora-Container-Base.*" + {"arm64": "aarch64"}[externaltools.DefaultArch] + ".*.tar.xz"
    url = next((url for url in urls.keys() if re.fullmatch(expression, url)), None)
    urllib.request.urlretrieve(url, download_file)
    return download_file


def extract_image(extracted_dir: Path) -> Path:
    if extracted_dir.is_dir():
        return extracted_dir
    archive_file = download_image(extracted_dir.parent)
    extracted_dir.mkdir(parents=True, exist_ok=True)
    with lzma.open(archive_file) as fd:
        with tarfile.open(fileobj=fd) as tar:
            tar.extractall(extracted_dir)
    return extracted_dir


def get_layer_tar(extracted_dir: Path) -> Path:
    return next(extract_image(extracted_dir).rglob("layer.tar"))


parser = argparse.ArgumentParser()
parser.add_argument("dir", type=Path, default=None, help="Setup directory")
parser.add_argument("--user", type=str, default=os.getlogin(), help="User name")
args = parser.parse_args()
layer_tar = get_layer_tar(args.dir / "fedora")
# coding:utf-8
# run as admin in Windows


def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin()


def encode_for_locale(s):
    if s is None:
        return
    return s.encode("mbcs")


class ShellExecuteInfo(ctypes.Structure):
    _fields_ = [
        ("cbSize", DWORD),
        ("fMask", c_ulong),
        ("hwnd", HWND),
        ("lpVerb", c_char_p),
        ("lpFile", c_char_p),
        ("lpParameters", c_char_p),
        ("lpDirectory", c_char_p),
        ("nShow", c_int),
        ("hInstApp", HINSTANCE),
        ("lpIDList", c_void_p),
        ("lpClass", c_char_p),
        ("hKeyClass", HKEY),
        ("dwHotKey", DWORD),
        ("hIcon", HANDLE),
        ("hProcess", HANDLE),
    ]


SEE_MASK_NOCLOSEPROCESS = 0x00000040
ShellExecuteEx = ctypes.windll.Shell32.ShellExecuteEx
ShellExecuteEx.argtypes = (ctypes.POINTER(ShellExecuteInfo),)
WaitForSingleObject = ctypes.windll.kernel32.WaitForSingleObject
SE_ERR_CODES = {
    0: "Out of memory or resources",
    2: "File not found",
    3: "Path not found",
    5: "Access denied",
    8: "Out of memory",
    26: "Cannot share an open file",
    27: "File association information not complete",
    28: "DDE operation timed out",
    29: "DDE operation failed",
    30: "DDE operation is busy",
    31: "File association not available",
    32: "Dynamic-link library not found",
}


def runas():
    nShow = 1
    cwd = None
    err = None
    waitClose = True
    waitTimeout = -1
    args = sys.argv
    executable = sys.executable
    try:
        if args is not None and not isinstance(args, str):
            args = subprocess.list2cmdline(args)
        pExecInfo = ShellExecuteInfo()
        pExecInfo.cbSize = ctypes.sizeof(pExecInfo)
        pExecInfo.fMask |= SEE_MASK_NOCLOSEPROCESS
        pExecInfo.lpVerb = b"open" if is_admin() else b"runas"
        pExecInfo.lpFile = encode_for_locale(executable)
        pExecInfo.lpParameters = encode_for_locale(args)
        pExecInfo.lpDirectory = encode_for_locale(cwd)
        pExecInfo.nShow = nShow
        if ShellExecuteEx(pExecInfo):
            if waitClose:
                WaitForSingleObject(pExecInfo.hProcess, waitTimeout)
                return True
            else:
                return pExecInfo.hProcess
        else:
            err = SE_ERR_CODES.get(pExecInfo.hInstApp, "unknown")
    except Exception as e:
        err = e
    if err:
        print("runas failed! error: %r" % err)


def ensure_admin():
    if not is_admin():
        runas()
        sys.exit(0)


if not subprocess.run(["wsl", "--version"], check=False, capture_output=True).returncode == 0:
    ensure_admin()
    subprocess.check_call(["wsl", "--install", "--no-distribution", "--no-launch"])
if "fedora" not in subprocess.check_output(["wsl", "-l", "-q"]).decode(encoding="utf-16").splitlines():
    ensure_admin()
    subprocess.check_call(["wsl", "--import", "fedora", args.dir.as_posix(), layer_tar.as_posix()])
DNFLIST = [
    "vim passwd util-linux openssh-clients cmake gcc-c++ gdb git python-unversioned-command python3-pip procps-ng",
    #       vcpkg-core
    "zip tar xz bzip2",
    #       stencil
    "flex bison",
    #       openssl
    # "perl-FindBin perl-IPC-Cmd perl-File-Compare perl-File-Copy",
    #       freexl
    # autoconf automake libtool
    #       icu
    # autoconf-archive
    #       libusb
    # systemd-devel
    #       qtbase
    # "mesa-libGL-devel libxcb-devel libXrender-devel xcb-util-*-devel xcb-util-devel",
    # "libxkbcommon-devel libxkbcommon-x11-devel perl-English",
]
INIT_SCRIPT_ROOT = f"""#!/usr/bin/env bash
dnf install -y { ' '.join(DNFLIST)}
adduser {args.user}
usermod -aG wheel {args.user};
printf "[user]\ndefault = {args.user}\nsystemd=true\n" > /etc/wsl.conf
"""

INIT_SCRIPT_USER = f"""#!/usr/bin/env bash
git config --global user.name "{args.user}"
git config --global user.email "{args.user}@email"
"""

p = subprocess.Popen(["wsl", "-d", "fedora", "-u", "root", "bash"], stdin=subprocess.PIPE)
# Write to the subprocess's stdin
p.stdin.write(INIT_SCRIPT_ROOT.encode())
output, err = p.communicate()
p.stdin.close()

p = subprocess.Popen(["wsl", "-d", "fedora", "-u", args.user, "bash"], stdin=subprocess.PIPE)
# Write to the subprocess's stdin
p.stdin.write(INIT_SCRIPT_USER.encode())
output, err = p.communicate()
p.stdin.close()
