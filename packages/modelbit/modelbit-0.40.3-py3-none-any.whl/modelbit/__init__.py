__version__ = "0.40.3"
__author__ = 'Modelbit'
from . import helpers as m_helpers

m_helpers.pkgVersion = __version__

import os, sys, yaml, pickle, logging
from typing import cast, Union, Callable, Any, Dict, List, Optional, TYPE_CHECKING

# aliasing since some of these overlap with functions we want to expose to users

from . import runtime as m_runtime
from . import utils as m_utils
from . import model_wrappers as m_model_wrappers
from . import jobs as m_jobs
from . import telemetry as m_telemetry

from modelbit.internal.auth import mbApi as _mbApi, mbApiReadOnly, isAuthenticated as isAuthenticated
from modelbit.internal.file_stubs import fileIsStub
from modelbit.error import ModelbitError as ModelbitError, UserFacingError as UserFacingError
from modelbit.internal import tracing

if TYPE_CHECKING:
  import pandas
  import modelbit.internal.datasets as m_datasets
  import modelbit.internal.warehouses as m_warehouses
  import modelbit.internal.deployments as m_deployments

m_telemetry.initLogging()
logger = logging.getLogger(__name__)


# Nicer UX for customers: from modelbit import Deployment
class Deployment(m_runtime.Deployment):
  ...


errorHandler = lambda msg: m_telemetry.eatErrorAndLog(mbApiReadOnly(), msg)  # type: ignore


def __str__():
  return "Modelbit Client"


def _repr_html_():  # type: ignore
  return ""


@errorHandler("Failed to add models.")
def add_models(models: Optional[Dict[str, Any]] = {},
               metrics: Optional[Dict[str, Optional[Dict[str, Any]]]] = None,
               files: Optional[Dict[str, str]] = None,
               serializer: Optional[str] = None,
               branch: Optional[str] = None):
  """
  https://doc.modelbit.com/api-reference/add_models
  """
  if m_utils.inDeployment() and not m_utils.inRuntimeJob():
    raise UserFacingError("mb.add_models is not supported within deployments")

  import modelbit.internal.registry as m_registry
  if models is not None:
    m_registry.set_many(_mbApi(branch=branch), models=models, metrics=metrics, serializer=serializer)
  elif files is not None:
    m_registry.setFiles(_mbApi(branch=branch), files=files, metrics=metrics)
  else:
    raise UserFacingError("One of models= or files= must be specified")


@errorHandler("Failed to add model.")
def add_model(name: str,
              model: Optional[Any] = None,
              metrics: Optional[Dict[str, Any]] = None,
              file: Optional[str] = None,
              serializer: Optional[str] = None,
              branch: Optional[str] = None):
  """
  https://doc.modelbit.com/api-reference/add_model
  """
  if m_utils.inDeployment() and not m_utils.inRuntimeJob():
    raise UserFacingError("mb.add_model is not supported within deployments")

  import modelbit.internal.registry as m_registry
  if file is None:
    m_registry.set(_mbApi(branch=branch), name, model=model, metrics=metrics, serializer=serializer)
  else:
    m_registry.setFiles(_mbApi(branch=branch), files={name: file}, metrics={name: metrics})


@errorHandler("Failed to add metrics.")
def add_metrics(name: str, metrics: Dict[str, Any], update: str = "merge"):
  """
  https://doc.modelbit.com/api-reference/add_metrics
  """
  if m_utils.inDeployment() and not m_utils.inRuntimeJob():
    raise UserFacingError("mb.add_metrics is not supported within deployments")

  if update not in ['merge', 'overwrite']:
    raise UserFacingError('update= must be either "merge" or "overwrite"')

  import modelbit.internal.registry as m_registry
  return m_registry.set_metrics(_mbApi(), name, metrics, update == "merge")


@errorHandler("Failed to get model.")
def get_model(name: str, file: Optional[str] = None, branch: Optional[str] = None):
  """
  https://doc.modelbit.com/api-reference/get_model
  """
  with tracing.trace(f"get_model('{name}')", False):
    import modelbit.internal.registry as m_registry
    if file is not None:
      return m_registry.getFiles(_mbApi(branch=branch), files={name: file})
    else:
      return m_registry.get(_mbApi(branch=branch), name=name)


@errorHandler("Failed to get models.")
def get_models(prefix: Optional[str] = None,
               names: Optional[List[str]] = None,
               files: Optional[Dict[str, str]] = None,
               branch: Optional[str] = None):
  """
  https://doc.modelbit.com/api-reference/get_models
  """
  with tracing.trace(f"get_models(...)", False):
    import modelbit.internal.registry as m_registry
    if files is not None:
      return m_registry.getFiles(_mbApi(branch=branch), files=files)
    else:
      return m_registry.getMany(_mbApi(branch=branch), prefix=prefix, names=names)


@errorHandler("Failed to get metrics.")
def get_metrics(nameOrNames: Union[str, List[str]]):
  """
  https://doc.modelbit.com/api-reference/get_metrics
  """
  import modelbit.internal.registry as m_registry
  return m_registry.getMetrics(_mbApi(), nameOrNames)


@errorHandler("Failed to list models.")
def models(prefix: Optional[str] = None):
  """
  https://doc.modelbit.com/api-reference/models
  """
  import modelbit.internal.registry as m_registry
  return m_registry.list_names(_mbApi(), prefix)


@errorHandler("Failed to delete model.")
def delete_models(names: Union[str, List[str]]):
  """
  https://doc.modelbit.com/api-reference/delete_models
  """
  if m_utils.inDeployment():
    raise UserFacingError("mb.delete_models is not supported within deployments")
  import modelbit.internal.registry as m_registry
  return m_registry.delete(_mbApi(), names)


@errorHandler("Failed to add job.")
def add_job(
    func: Callable[..., Any],
    deployment_name: str,
    name: Optional[str] = None,
    python_version: Optional[str] = None,
    python_packages: Optional[List[str]] = None,
    system_packages: Optional[List[str]] = None,
    extra_files: Union[str, List[str], Dict[str, str], None] = None,
    skip_extra_files_dependencies: bool = False,
    email_on_failure: Optional[str] = None,
    schedule: Optional[str] = None,
    refresh_datasets: Optional[List[str]] = None,
    size: Optional[str] = None,
    timeout_minutes: Optional[int] = None,
    default_arguments: Optional[List[Any]] = None,
):
  """
  https://doc.modelbit.com/api-reference/add_job
  """
  m_jobs.add_job(
      _mbApi(),
      func,
      deployment_name,
      name=name,
      python_version=python_version,
      python_packages=python_packages,
      system_packages=system_packages,
      extra_files=extra_files,
      skip_extra_files_dependencies=skip_extra_files_dependencies,
      email_on_failure=email_on_failure,
      schedule=schedule,
      refresh_datasets=refresh_datasets,
      size=size,
      timeout_minutes=timeout_minutes,
      default_arguments=default_arguments,
  )


@errorHandler("Failed to run job.")
def run_job(deployment_name: str,
            job_name: Optional[str] = None,
            arguments: Optional[List[Any]] = None,
            branch: Optional[str] = None) -> 'm_jobs.ModelbitJobRun':
  """
  https://doc.modelbit.com/api-reference/run_job
  """
  if type(deployment_name) is str and job_name is not None:
    return m_jobs.runJob(runtimeName=deployment_name,
                         jobName=job_name,
                         args=arguments,
                         mbApi=_mbApi(),
                         branch=branch or m_helpers.getCurrentBranch())
  else:
    raise TypeError("missing job_name")


@errorHandler("Failed to list datasets.")
def datasets() -> 'm_datasets.DatasetList':
  """
  https://doc.modelbit.com/api-reference/datasets
  """
  import modelbit.internal.datasets as m_datasets
  return m_datasets.list(_mbApi())


@errorHandler("Failed to load dataset.")
def get_dataset(dsName: str,
                filters: Optional[Dict[str, Union[Any, Dict[str, Any]]]] = None,
                filter_column: Optional[str] = None,
                filter_values: Optional[List[Any]] = None,
                optimize: Optional[bool] = None,
                legacy: Optional[bool] = None,
                branch: Optional[str] = None) -> Optional['pandas.DataFrame']:
  """
  https://doc.modelbit.com/api-reference/get_dataset
  """
  if filter_column is not None and filter_values is not None:
    print("Deprecated: filter_column= & filter_values= will be removed soon. Use filters= instead.")
    if filters is None:
      filters = {}
    filters[filter_column] = filter_values
  if optimize is not None:
    print("Deprecated: optimize= will be removed soon.")

  with tracing.trace(f"get_dataset('{dsName}')", False):
    import modelbit.internal.feature_store as m_feature_store
    return m_feature_store.getDataFrame(_mbApi(),
                                        branch=branch or m_helpers.getCurrentBranch(),
                                        dsName=dsName,
                                        filters=filters)


@errorHandler("Failed to load warehouses.")
def warehouses() -> 'm_warehouses.WarehousesList':
  """
  https://doc.modelbit.com/api-reference/warehouses
  """
  import modelbit.internal.warehouses as m_warehouses
  return m_warehouses.list(_mbApi())


@errorHandler("Failed to load deployments.")
def deployments() -> 'm_deployments.DeploymentsList':
  import modelbit.internal.deployments as m_deployments
  return m_deployments.list(_mbApi())


@errorHandler("Failed to add files.")
def add_files(deployment: str,
              files: Union[str, List[str], Dict[str, str]],
              modelbit_file_prefix: Optional[str] = None,
              strip_input_path: Optional[bool] = False):
  """
  https://doc.modelbit.com/api-reference/add_files
  """
  return m_runtime.add_files(_mbApi(), deployment, files, modelbit_file_prefix, strip_input_path)


@errorHandler("Failed to add objects.")
def add_objects(deployment: str, values: Dict[str, Any]):
  return m_runtime.add_objects(_mbApi(), deployment, values)


@errorHandler("Failed to load secret.")
def get_secret(name: str,
               deployment: Optional[str] = None,
               branch: Optional[str] = None,
               encoding: str = "utf8",
               ignore_missing: bool = False) -> str:
  """
  https://doc.modelbit.com/api-reference/get_secret
  """
  with tracing.trace(f"get_secret('{name}')", False):
    import modelbit.internal.secrets as m_secrets
    return m_secrets.get_secret(mbApi=_mbApi(),
                                name=name,
                                deployment=deployment,
                                branch=branch,
                                encoding=encoding,
                                ignore_missing=ignore_missing)


@errorHandler("Failed to store secret.")
def set_secret(name: str,
               value: str,
               deployment_filter: Optional[str] = None,
               branch_filter: Optional[str] = None):
  """
  https://doc.modelbit.com/api-reference/set_secret
  """
  with tracing.trace(f"set_secret('{name}')", False):
    import modelbit.internal.secrets as m_secrets
    m_secrets.set_secret(mbApi=_mbApi(),
                         name=name,
                         value=value,
                         runtimeNameFilter=deployment_filter,
                         runtimeBranchFilter=branch_filter)


@errorHandler("Failed to add package.")
def add_package(path: str, force: bool = False, branch: Optional[str] = None):
  """
  https://doc.modelbit.com/api-reference/add_package
  """
  import modelbit.internal.package as m_package
  return m_package.add_package(path, force, _mbApi(branch=branch))


@errorHandler("Failed to delete package.")
def delete_package(name: str, version: str, branch: Optional[str] = None):
  """
  https://doc.modelbit.com/api-reference/delete_package
  """
  import modelbit.internal.package as m_package
  return m_package.delete_package(name, version, _mbApi(branch=branch))


@errorHandler("Failed to add common files.")
def add_common_files(files: Union[List[str], Dict[str, str], str]):
  """
  https://doc.modelbit.com/api-reference/add_common_files
  """
  import modelbit.internal.common_files as m_common_files
  m_common_files.addFiles(_mbApi(), files)


@errorHandler("Failed to delete common files.")
def delete_common_files(names: Union[List[str], str]):
  """
  https://doc.modelbit.com/api-reference/delete_common_files
  """
  import modelbit.internal.common_files as m_common_files
  m_common_files.deleteFiles(_mbApi(), names)


@errorHandler("Failed to list common files.")
def common_files(prefix: Optional[str] = None):
  """
  https://doc.modelbit.com/api-reference/common_files
  """
  import modelbit.internal.common_files as m_common_files
  return m_common_files.listFiles(_mbApi(), prefix)


@errorHandler("Failed to deploy.")
def deploy(deployableObj: Union[Callable[..., Any], 'm_runtime.Deployment'],
           name: Optional[str] = None,
           python_version: Optional[str] = None,
           python_packages: Optional[List[str]] = None,
           system_packages: Optional[List[str]] = None,
           dataframe_mode: bool = False,
           example_dataframe: Optional['pandas.DataFrame'] = None,
           common_files: Union[str, List[str], Dict[str, str], None] = None,
           extra_files: Union[str, List[str], Dict[str, str], None] = None,
           skip_extra_files_dependencies: bool = False,
           snowflake_max_rows: Optional[int] = None,
           snowflake_mock_return_value: Optional[Any] = None,
           require_gpu: Union[bool, str] = False,
           setup: Optional[Union[str, List[str]]] = None):
  """
  https://doc.modelbit.com/api-reference/deploy
  """
  if type(deployableObj) is m_jobs.ModelbitJobWrapper:
    raise UserFacingError("Cannot deploy a job. Use modelbit.add_job()")

  if type(require_gpu) not in [str, bool] or require_gpu not in ["T4", "A10G", True, False]:
    raise UserFacingError(f"require_gpu= must be a bool or 'T4' or 'A10G'. It is currently {require_gpu}")

  if _objIsDeployment(deployableObj):
    deployableObj = cast(Deployment, deployableObj)
    return deployableObj.deploy()
  elif callable(deployableObj) and deployableObj.__name__ == "<lambda>":
    if isinstance(common_files, str):
      common_files = [common_files]
    if isinstance(extra_files, str):
      extra_files = [extra_files]
    return m_model_wrappers.LambdaWrapper(
        deployableObj,
        name=name,
        python_version=python_version,
        python_packages=python_packages,
        system_packages=system_packages,
        dataframe_mode=dataframe_mode,
        example_dataframe=example_dataframe,
        common_files=common_files,
        extra_files=extra_files,
        skip_extra_files_dependencies=skip_extra_files_dependencies,
        snowflake_max_rows=snowflake_max_rows,
        snowflake_mock_return_value=snowflake_mock_return_value,
        require_gpu=require_gpu,
        setup=setup,
    ).makeDeployment(_mbApi()).deploy()
  elif callable(deployableObj):
    return Deployment(
        api=_mbApi(),
        name=name,
        deploy_function=deployableObj,
        python_version=python_version,
        python_packages=python_packages,
        system_packages=system_packages,
        dataframe_mode=dataframe_mode,
        example_dataframe=example_dataframe,
        common_files=common_files,
        extra_files=extra_files,
        skip_extra_files_dependencies=skip_extra_files_dependencies,
        snowflake_max_rows=snowflake_max_rows,
        snowflake_mock_return_value=snowflake_mock_return_value,
        require_gpu=require_gpu,
        setup=setup,
    ).deploy()
  else:
    raise Exception("First argument must be a function or Deployment object.")


@errorHandler("Unable to log in.")
def login(branch: Optional[str] = None, region: Optional[str] = None):
  """
  https://doc.modelbit.com/api-reference/login
  """
  _mbApi(branch=branch, region=region)
  return sys.modules['modelbit']


@errorHandler("Could not switch branch.")
def switch_branch(branch: str):
  """
  https://doc.modelbit.com/api-reference/switch_branch
  """
  # See if new branch exists, but not from deployments
  from modelbit.internal import branch as m_branch
  if not m_branch.checkBranchExists(mbApi=_mbApi(), branchName=branch):
    raise UserFacingError(f"Branch {branch} not found.")
  m_helpers.setCurrentBranch(branch)


def get_branch() -> str:
  """
  https://doc.modelbit.com/api-reference/get_branch
  """
  return m_helpers.getCurrentBranch()


@errorHandler("Unable to create the branch.")
def create_branch(name: str, from_branch: Optional[str] = None) -> None:
  """
  https://doc.modelbit.com/api-reference/create_branch
  """
  from modelbit.internal import branch as m_branch
  m_branch.createBranch(mbApi=_mbApi(), branchName=name, baseName=from_branch)
  switch_branch(name)


def in_modelbit() -> bool:
  """
  https://doc.modelbit.com/api-reference/in_modelbit
  """
  return m_utils.inDeployment()


def get_deployment_info() -> Dict[str, Any]:
  """
  https://doc.modelbit.com/api-reference/get_deployment_info
  """
  if not in_modelbit():
    print("get_deployment_info: Warning, not currently running in a deployment.")
  return {
      "branch": m_helpers.getCurrentBranch(),
      "name": m_helpers.getDeploymentName(),
      "version": m_helpers.getDeploymentVersion()
  }


@errorHandler("Unable get mock return value.")
def get_snowflake_mock_return_value(deployment_name: str,
                                    version: Optional[int] = None,
                                    branch: Optional[str] = None):
  """
  https://doc.modelbit.com/api-reference/get_snowflake_mock_return_value
  """
  import modelbit.internal.metadata as m_metadata
  return m_metadata.getSnowflakeMockReturnValue(api=_mbApi(),
                                                branch=(branch or m_helpers.getCurrentBranch()),
                                                deploymentName=deployment_name,
                                                deploymentVersion=version)


@errorHandler("Unable set mock return value.")
def set_snowflake_mock_return_value(deployment_name: str,
                                    mock_return_value: Optional[Any],
                                    branch: Optional[str] = None):
  """
  https://doc.modelbit.com/api-reference/set_snowflake_mock_return_value
  """
  import modelbit.internal.metadata as m_metadata
  return m_metadata.setSnowflakeMockReturnValue(api=_mbApi(),
                                                branch=(branch or m_helpers.getCurrentBranch()),
                                                deploymentName=deployment_name,
                                                mockReturnValue=mock_return_value)


def log_image(obj: Any):
  """
  https://doc.modelbit.com/api-reference/log_image
  """
  with tracing.trace(f"log_image(...)", False):
    import modelbit.file_logging as m_file_logging
    m_file_logging.logImage(obj)


@errorHandler("Unable to merge deployment.")
def merge_deployment(deployment_name: str, to_branch: str, from_branch: Optional[str] = None):
  """
  https://doc.modelbit.com/api-reference/merge_deployment
  """
  return m_runtime.copy_deployment(api=_mbApi(),
                                   fromBranch=(from_branch or m_helpers.getCurrentBranch()),
                                   toBranch=to_branch,
                                   runtimeName=deployment_name,
                                   runtimeVersion="latest")


@errorHandler("Unable to restart deployment.")
def restart_deployment(deployment_name: str,
                       version: Optional[Union[str, int]] = None,
                       branch: Optional[str] = None):
  """
  https://doc.modelbit.com/api-reference/restart_deployment
  """
  import modelbit.internal.runtime_slots as m_runtime_slots
  m_runtime_slots.restartRuntime(api=_mbApi(),
                                 branch=(branch or m_helpers.getCurrentBranch()),
                                 runtimeName=deployment_name,
                                 runtimeVersion=(version or "latest"))


def load_value(name: str, restoreClass: Optional[type] = None):
  with tracing.trace(f"load_value('{name}')", False):
    if name.endswith(".pkl"):
      import __main__ as main_package
      # Support finding files relative to source location
      # This doesn't work from lambda, so only use when not in a deployment
      if not os.path.exists(name):
        name = os.path.join(os.path.dirname(main_package.__file__), name)

      if fileIsStub(name):
        raise UserFacingError(f"Use `modelbit clone` to check out this repo. This file is a stub: {name}")

      with open(name, "rb") as f:
        value = pickle.load(f)
        if restoreClass is not None and isinstance(value, m_helpers.InstancePickleWrapper):
          return value.restore(restoreClass)
        else:
          return value
    extractPath = os.environ['MB_EXTRACT_PATH']
    objPath = os.environ['MB_RUNTIME_OBJ_DIR']
    if not extractPath or not objPath:
      raise Exception("Missing extractPath/objPath")
    with open(f"{extractPath}/metadata.yaml", "r") as f:
      yamlData = cast(Dict[str, Any], yaml.load(f, Loader=yaml.SafeLoader))  # type: ignore
    data: Dict[str, Dict[str, str]] = yamlData["data"]
    contentHash = data[name]["contentHash"]
    with open(f"{objPath}/{contentHash}.pkl.gz", "rb") as f:
      return m_utils.deserializeGzip(contentHash, f.read)


def save_value(obj: Any, filepath: str):
  if not os.path.exists(os.path.dirname(filepath)):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

  if (hasattr(obj, "__module__") and obj.__module__ == "__main__"):
    # If the object is in __main__, move it so we can load it from a source file.
    # This allows objects saved from jobs to be loaded by inference functions.
    import inspect
    callerFrame = inspect.stack()[1]
    module = inspect.getmodule(callerFrame[0])
    if module is not None and module.__file__ is not None:
      obj = m_utils.repickleFromMain(obj, module)

  with open(filepath, "wb") as f:
    pickle.dump(obj, f)


def trace(name: str):
  return tracing.trace(name, True)


def _objIsDeployment(obj: Any):
  try:
    if type(obj) in [Deployment, m_runtime.Deployment]:
      return True
    # catch modelbit._reload() class differences
    if obj.__class__.__name__ in ['Deployment']:
      return True
  except:
    return False
  return False


def parseArg(s: str) -> Any:
  import json
  try:
    return json.loads(s)
  except json.decoder.JSONDecodeError:
    return s


@errorHandler("Failed to get the inference.")
def get_inference(deployment: str,
                  data: Any,
                  region: str = "app",
                  outpost: Optional[str] = None,
                  workspace: Optional[str] = None,
                  branch: Optional[str] = None,
                  version: Optional[Union[str, int]] = None,
                  api_key: Optional[str] = None,
                  timeout_seconds: Optional[int] = None,
                  batch_size: Optional[int] = None) -> Dict[str, Any]:
  """
  https://doc.modelbit.com/api-reference/get_inference
  """
  from modelbit.api.inference_api import callDeployment
  return callDeployment(
      region=region,
      workspace=workspace or os.environ.get("MB_WORKSPACE_NAME"),
      outpost=outpost,
      branch=branch or m_helpers.getCurrentBranch(),
      deployment=deployment,
      version=version or "latest",
      data=data,
      apiKey=api_key or os.environ.get("MB_API_KEY"),
      timeoutSeconds=timeout_seconds,
      batchChunkSize=batch_size,
  )


def setup(name: str):
  from . import setup_manager as m_setup_manager
  return m_setup_manager.setupManager(name)
