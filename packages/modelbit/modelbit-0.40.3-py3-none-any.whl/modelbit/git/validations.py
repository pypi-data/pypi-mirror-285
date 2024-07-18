import sys, os
from os import path
from typing import Dict, Optional, List, cast
import yaml
import traceback
import ast
import logging

from modelbit.ux import SHELL_FORMAT_FUNCS
from modelbit.api import MbApi
from modelbit.error import UserFacingError
from modelbit.api.metadata_api import MetadataApi, MetadataValidationResponse
import yaml.scanner
from .repo_helpers import getRepoRoot
from modelbit.telemetry import logEventToWeb

logger = logging.getLogger(__name__)


def writePreCommitHook():
  try:
    repoRoot = getRepoRoot()
    if repoRoot is None:
      raise Exception(f"Could not find repository near {os.getcwd()}")
    hookPath = os.path.join(repoRoot, ".git/hooks/pre-commit")
    with open(hookPath, "w") as f:
      f.write("""#!/bin/sh

exec modelbit validate
""")
    os.chmod(hookPath, 0o775)
  except Exception as err:
    print(f"Unable to write pre-commit hook: {err}", file=sys.stderr)


def show(message: str):
  print(message, file=sys.stderr)


def _red(message: str) -> str:
  return SHELL_FORMAT_FUNCS["red"](message)


def _purple(message: str) -> str:
  return SHELL_FORMAT_FUNCS["purple"](message)


def validateRepo(mbApi: MbApi, dir: str) -> bool:
  try:
    vDeps = validateDeployments(mbApi, dir)
    vRepo = validateRepoShape(dir)
    return vDeps and vRepo
  except UserFacingError as err:  # intentional errors to block shipping
    show(_red("Validation error: ") + str(err))
    return False
  except Exception as err:  # bugs that'll block deployments so let them through
    show(_red("Unexpected error: ") + str(err))
    show(traceback.format_exc())
    return True


def validateDeployments(mbApi: MbApi, dir: str) -> bool:
  depsPath = path.join(dir, "deployments")
  validationsPassed: bool = True

  if not path.exists(depsPath):
    raise ValueError(f"Unable to read deployments directory '{depsPath}'")

  allDeploymentNames = sorted(os.listdir(depsPath))
  if len(allDeploymentNames) == 0:
    return validationsPassed

  show("\nValidating deployments...")
  metadataValidations = validateMetadataFiles(mbApi, depsPath)
  failed: List[str] = []
  for d in allDeploymentNames:
    if not path.isdir(path.join(depsPath, d)):
      continue
    passed = validateOneDeployment(depsPath,
                                   d,
                                   metadataValidationError=metadataValidations.getError(
                                       path.join(depsPath, d, "metadata.yaml")))
    if not passed:
      failed.append(d)
    validationsPassed = validationsPassed and passed
  show("")
  logEventToWeb(api=mbApi,
                name="ValidateDeployments",
                details={
                    "failedNames": ",".join(failed),
                    "numFailed": len(failed),
                    "total": len(allDeploymentNames)
                })
  return validationsPassed


def validateOneDeployment(depsPath: str, depName: str, metadataValidationError: Optional[str]) -> bool:

  def pathExists(fileName: str):
    return path.exists(path.join(depsPath, depName, fileName))

  if pathExists(".archived"):
    return True  # don't validate archived deployments

  mainFuncError: Optional[str] = getMainFuncError(path.join(depsPath, depName))

  if not pathExists("source.py") and not pathExists("jobs.yaml"):
    show(f"  ❌ {_red(depName)}: Missing {_purple('source.py')}")
    return False
  elif not pathExists("metadata.yaml"):
    show(f"  ❌ {_red(depName)}: Missing {_purple('metadata.yaml')}")
    return False
  elif metadataValidationError:
    show(f"  ❌ {_red(depName)}: Error in {_purple('metadata.yaml')}:" + f" {metadataValidationError}")
    return False
  elif mainFuncError:
    show(f"  ❌ {_red(depName)}: Error in {_purple('metadata.yaml')}:" + f" {mainFuncError}")
    return False
  else:
    show(f"  ✅ {depName}")
    return True


# returns filePath -> fileContents. Getting them all so they can be in one web request
def collectMetadataFiles(depsPath: str) -> Dict[str, str]:
  files: Dict[str, str] = {}
  for d in os.listdir(depsPath):
    filePath = path.join(depsPath, d, "metadata.yaml")
    if path.exists(filePath):
      with open(filePath) as f:
        files[filePath] = f.read()
  return files


# returns path -> Optional[errorMessage]
def validateMetadataFiles(mbApi: MbApi, depsPath: str) -> MetadataValidationResponse:
  files = collectMetadataFiles(depsPath)
  return MetadataApi(mbApi).validateMetadataFiles(files)


def getMainFuncError(depPath: str) -> Optional[str]:
  try:
    metadataPath = path.join(depPath, "metadata.yaml")
    if not os.path.exists(metadataPath):
      return None
    with open(metadataPath) as f:
      obj = yaml.safe_load(f)
      mainFunc = obj["runtimeInfo"].get("mainFunction")
      mainFuncArgs = obj["runtimeInfo"].get("mainFunctionArgs")
    with open(path.join(depPath, "source.py")) as f:
      sourceCode = f.read()
      if mainFunc is None:
        return f"The mainFunction parameter is missing from metadata.yaml"
      if type(mainFunc) is not str:
        return f"The mainFunction parameter must be a string"
      if type(mainFuncArgs) is not list and mainFuncArgs is not None:
        return f"The mainFunctionArgs parameter must be a list of strings"
      if mainFunc not in sourceCode:
        return f"The mainFunction '{mainFunc}' was not found in source.py"

      mainArgsErr = getMainFunctionArgsError(source=sourceCode,
                                             mainFunctionName=mainFunc,
                                             expectedArgs=cast(Optional[List[str]], mainFuncArgs))
      if mainArgsErr is not None:
        return mainArgsErr
  except yaml.scanner.ScannerError as err:
    return err.problem
  except:
    pass  # if something goes wrong in the parsing other validators would have caught it

  return None


def getMainFunctionArgsError(source: str, mainFunctionName: str,
                             expectedArgs: Optional[List[str]]) -> Optional[str]:

  parsedArgNames = parseMainFunctionArgs(source=source, mainFunctionName=mainFunctionName)
  if parsedArgNames is None:
    return None
  if len(parsedArgNames) != 0 and (expectedArgs is None or len(expectedArgs) == 0):
    return "The mainFunctionArgs parameter is missing"
  if expectedArgs is None:
    return None
  for a in expectedArgs:
    if type(a) is not str:
      return f"The mainFunctionArgs parameter should be a list of strings. '{a}' is a '{type(a)}'"

  expectedArgNames = [a.split(":")[0] for a in expectedArgs]
  for eName in expectedArgNames:
    if eName == "return":
      continue
    if eName not in parsedArgNames:
      return f"Unexpected mainFunctionArgs argument named '{eName}'. It wasn't found in function '{mainFunctionName}'"
  for pName in parsedArgNames:
    if pName not in expectedArgNames:
      return f"The argument '{pName}' of function '{mainFunctionName}' is missing from mainFunctionArgs"

  return None


def parseMainFunctionArgs(source: str, mainFunctionName: str) -> Optional[List[str]]:
  try:
    for a in ast.parse(source).body:
      if type(a) is ast.FunctionDef:
        if a.name == mainFunctionName:
          return [a.arg for a in a.args.args]
    return None
  except Exception as err:
    logger.error("ErrorParsingSource.py", exc_info=err)
    return None  # other tests should have caught this, so we can drop the error


def validateRepoShape(repoRoot: str) -> bool:
  allowedInRoot = [
      ".git",
      ".gitignore",
      ".gitattributes",
      ".workspace",
      "bin",
      "README.md",
      "deployments",
      "datasets",
      "endpoints",
      "notebooks",
      "common",
      "registry",
      "packages",
  ]
  disallowed = [f for f in list(os.listdir(repoRoot)) if f not in allowedInRoot]

  if len(disallowed) == 0:
    return True

  show("\nValidating repository...")
  show(
      f"  ❌ Extra files and directories are not allowed in the root of the Modelbit repository. Please remove: "
      + ", ".join(disallowed))
  show("")
  return False
