import difflib
import filecmp
import os
import shutil
import subprocess
import sys
from pathlib import Path

import git


class SyncError(Exception):
    pass


class Syncer:
    def __init__(self, work: Path, src: Path):
        self.work_dir = work
        self.src_dir = src
        self.work_dir.mkdir(exist_ok=True, parents=True)
        self.git = git.Git(root=self.work_dir)
        self.InitWork()

    def _copy_from_src(self) -> None:
        for src_files in self.src_dir.rglob("*"):
            dst = self.work_dir / src_files.relative_to(self.src_dir)
            if src_files.is_dir():
                dst.mkdir(exist_ok=True, parents=True)
                continue
            shutil.copy(src_files, dst)

    def InitWork(self) -> None:
        if not (self.work_dir / ".git").is_dir():
            self.git.cmd(["init"])
            self._copy_from_src()
            self.git.cmd(["add", "."])
            self.git.cmd(
                [
                    "-c",
                    "user.name=ankurv",
                    "-c",
                    "user.email=ankur@verma",
                    "commit",
                    "-a",
                    "-m",
                    "Init",
                ],
            )
            self.git.create_branch("work", "HEAD")

    def SyncWork(self) -> None:
        if self.git.current_branch() not in ("master", "work"):
            raise SyncError(f"Current branch is not work :{self.git.current_branch()}:")
        if self.git.dirty():
            raise SyncError("Current branch dirty")
        self.git.checkout("master")
        self._copy_from_src()
        if self.git.dirty():
            self.git.cmd(["commit", "-a", "-m", "Update"])
        self.git.checkout("work")
        self.git.merge_branch("master", rebase_squash=True)

    def SyncSource(self) -> None:
        if self.git.current_branch() != "work":
            raise SyncError("Current branch is not work")
        self.git.merge_branch("master", rebase_squash=True)
        patchfiles = [(self.work_dir / ptchf) for ptchf in self.git.cmd(["format-patch", "master"]).splitlines()]
        relative_src = self.src_dir.relative_to(self.git.toplevel(self.src_dir))
        try:
            for patchf in patchfiles:
                self.git.cmd(
                    [
                        "apply",
                        f"--directory={relative_src.as_posix()}",
                        "--ignore-whitespace",
                        "--ignore-space-change",
                        "--whitespace=fix",
                        "--summary",
                        "--stat",
                        "--apply",
                        "--verbose",
                        "--no-index",
                        patchf.as_posix(),
                    ],
                    root=self.src_dir,
                )
        finally:
            for patchf in patchfiles:
                os.unlink(patchf.as_posix())

    @staticmethod
    def sync_files(tgtfile: Path, reffile: Path, mode: str) -> None:
        sys.stderr.write(f"Files in sync {tgtfile} {reffile}\n")
        if filecmp.cmp(tgtfile, reffile):
            return
        fromlines = tgtfile.read_text().split("\n")
        tolines = reffile.read_text().split("\n")
        sys.stderr.write(str(difflib.unified_diff(fromlines, tolines, tgtfile.as_posix(), reffile.as_posix())))

        def safecopy(src: Path, dst: Path) -> None:
            rslt = subprocess.run(["git", "diff", "--quiet", dst.name], cwd=dst.parent, check=True)
            if rslt.returncode != 0:
                raise SyncError(f"File {dst} has has uncommitted changes: refusing to sync\n{rslt.stdout.decode()}")
            shutil.copyfile(src, dst)

        if mode == "back" or os.stat(tgtfile).st_mtime_ns > os.stat(reffile).st_mtime_ns:
            safecopy(tgtfile, reffile)
        else:
            safecopy(reffile, tgtfile)

    @staticmethod
    def sync_dirs(dir1: Path, dir2: Path) -> None:
        dir1 = dir1.absolute()
        dir2 = dir2.absolute()
        if not dir1.exists() or not dir2.exists():
            raise SyncError(f"Sync directories missing {dir1.as_posix()} <=> {dir2.as_posix()}")
        rslt = subprocess.run(["git", "diff", "--quiet", "."], cwd=dir1, check=True)
        if rslt.returncode != 0:
            raise SyncError(f"File {dir1.as_posix()} has has uncommitted changes: refusing to sync\n{rslt.stdout.decode()}")
        rslt = subprocess.run(["git", "diff", "--quiet", "."], cwd=dir2, check=True)
        if rslt.returncode != 0:
            raise SyncError(f"File {dir2.as_posix()} has has uncommitted changes: refusing to sync\n{rslt.stdout.decode()}")
        for dir1_file in dir1.rglob("*"):
            rel = dir1_file.relative_to(dir1)
            dir2_file = dir2 / rel
            if not dir2_file.exists():
                raise SyncError(f"Sync files missing {dir1_file.as_posix()} <=> {dir2_file.as_posix()}")
            if filecmp.cmp(dir1_file, dir2_file):
                return
            if os.stat(dir1_file).st_mtime_ns > os.stat(dir2_file).st_mtime_ns:
                shutil.copyfile(dir1_file, dir2_file)
            else:
                shutil.copyfile(dir2_file, dir1_file)
