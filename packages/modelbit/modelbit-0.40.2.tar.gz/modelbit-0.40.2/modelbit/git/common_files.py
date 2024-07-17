from typing import Optional, List
from .repo_helpers import getRepoRoot
from modelbit.error import UserFacingError
from modelbit.ux import SHELL_FORMAT_FUNCS
import os, shutil
from fnmatch import fnmatch
from os import path
from pathlib import Path

DepDirName = "deployments"
ComDirName = "common"


def getCurrentDepName(repoRoot: str) -> str:
  cwd = os.getcwd()
  if not cwd.startswith(repoRoot):
    raise UserFacingError(f"Expecting {cwd} to be under {repoRoot}")

  current = Path(cwd).name
  for parent in Path(cwd).parents:
    if path.basename(parent) == DepDirName:
      return current
    current = parent.name
  raise UserFacingError(f"Could not find current deployment in {cwd}. Specify it with --deployment")


def fullPathToDeployment(repoRoot: str, depName: str):
  depPath = path.join(repoRoot, DepDirName, depName)
  if not path.exists(depPath):
    raise UserFacingError(f"Deployment {depName} not found under {depPath}")
  return depPath


def enumerateCommonFiles(repoRoot: str, pattern: Optional[str], relCommonPath: str = "") -> List[str]:
  common: List[str] = []
  searchRoot = path.join(repoRoot, "common", relCommonPath)
  for name in os.listdir(searchRoot):
    if name.startswith(".") or name == "settings.yaml":
      continue
    relName = path.join(relCommonPath, name)
    matches = fnmatch(relName, pattern or "*")
    fullPath = path.join(searchRoot, name)
    if path.islink(fullPath):
      continue  # ignore links within common to avoid loops
    elif matches:
      common.append(relName)
    elif path.isdir(fullPath):
      common += enumerateCommonFiles(
          repoRoot=repoRoot,
          pattern=pattern,
          relCommonPath=path.join(relCommonPath, name),
      )
  return sorted(common)


def addSymlinks(depPath: str, repoRoot: str, common: List[str]):
  for c in common:

    pathInDep = path.join(depPath, c)
    os.makedirs(path.dirname(pathInDep), exist_ok=True)

    pathInCommon = path.join(repoRoot, ComDirName, c)

    if path.exists(pathInDep):
      if path.isdir(pathInDep) and not path.islink(pathInDep):
        shutil.rmtree(pathInDep)
      else:
        os.unlink(pathInDep)

    relLinkToCommon = path.relpath(pathInCommon, path.dirname(pathInDep))
    relLinkInDep = path.relpath(pathInDep, path.join(repoRoot, DepDirName))
    purple = SHELL_FORMAT_FUNCS['purple']
    print(f"{purple('Linking')} {relLinkInDep} {purple('-->')} {path.join(ComDirName, c)}")
    os.symlink(relLinkToCommon, pathInDep)


def linkCommonFiles(depName: Optional[str], pattern: Optional[str]):
  repoRoot = getRepoRoot()
  if repoRoot is None:
    raise UserFacingError(f"Could not find repository near {os.getcwd()}")

  cFilePaths = enumerateCommonFiles(repoRoot=repoRoot, pattern=pattern)
  if len(cFilePaths) == 0:
    raise UserFacingError(f"No common files matched the pattern {pattern}")

  depPath = fullPathToDeployment(repoRoot, depName or getCurrentDepName(repoRoot))
  addSymlinks(depPath=depPath, repoRoot=repoRoot, common=cFilePaths)
