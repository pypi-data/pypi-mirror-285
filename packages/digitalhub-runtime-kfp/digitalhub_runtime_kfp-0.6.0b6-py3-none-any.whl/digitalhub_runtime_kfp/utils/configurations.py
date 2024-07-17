from __future__ import annotations

import importlib.util as imputil
import inspect
import sys
import typing
from importlib import import_module
from os import path
from pathlib import Path
from types import ModuleType

from digitalhub_core.entities.workflows.crud import get_workflow
from digitalhub_core.utils.generic_utils import (
    decode_string,
    extract_archive,
    get_bucket_and_key,
    get_s3_source,
    requests_chunk_download,
)
from digitalhub_core.utils.git_utils import clone_repository
from digitalhub_core.utils.logger import LOGGER

if typing.TYPE_CHECKING:
    from digitalhub_core.entities.workflows.entity import Workflow
    from digitalhub_runtime_kfp.entities.workflows.spec import WorkflowSpecKFP


def get_dhcore_workflow(workflow_string: str) -> Workflow:
    """
    Get DHCore workflow.

    Parameters
    ----------
    workflow_string : str
        Function string.

    Returns
    -------
    Workflow
        DHCore workflow.
    """
    splitted = workflow_string.split("://")[1].split("/")
    workflow_name, workflow_version = splitted[1].split(":")
    LOGGER.info(f"Getting workflow {workflow_name}:{workflow_version}.")
    try:
        return get_workflow(splitted[0], workflow_name, workflow_version)
    except Exception as e:
        msg = f"Error getting workflow {workflow_name}:{workflow_version}. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise RuntimeError(msg) from e


def save_workflow_source(path: Path, source_spec: dict) -> str:
    """
    Save workflow source.

    Parameters
    ----------
    path : Path
        Path where to save the workflow source.
    source_spec : dict
        Workflow source spec.

    Returns
    -------
    path
        Workflow code.
    """
    # Prepare path
    path.mkdir(parents=True, exist_ok=True)

    # Get relevant information
    code = source_spec.get("code")
    base64 = source_spec.get("base64")
    source = source_spec.get("source")
    handler = source_spec.get("handler")

    if code is not None:
        path = path / "source.py"
        path.write_text(code)
        return str(path)

    if base64 is not None:
        path = path / "source.py"
        path.write_text(decode_base64(base64))
        return str(path)

    if source is None or handler is None:
        raise RuntimeError("Workflow source and handler must be defined.")

    scheme = source.split("://")[0]

    # Http(s) or s3 presigned urls
    if scheme in ["http", "https"]:
        filename = path / "archive.zip"
        get_remote_source(source, filename)
        unzip(path, filename)
        return str(path / handler)

    # Git repo
    if scheme == "git+https":
        path = path / "repository"
        get_repository(path, source)
        return str(path / handler)

    # S3 path
    if scheme == "zip+s3":
        filename = path / "archive.zip"
        bucket, key = get_bucket_and_key(source)
        get_s3_source(bucket, key, filename)
        unzip(path, filename)
        return str(path / handler)

    # Unsupported scheme
    raise RuntimeError(f"Unsupported scheme: {scheme}")


def get_remote_source(source: str, filename: Path) -> None:
    """
    Get remote source.

    Parameters
    ----------
    source : str
        HTTP(S) or S3 presigned URL.
    filename : Path
        Path where to save the workflow source.

    Returns
    -------
    str
        Workflow code.
    """
    try:
        requests_chunk_download(source, filename)
    except Exception as e:
        msg = f"Some error occurred while downloading function source. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise RuntimeError(msg) from e


def unzip(path: Path, filename: Path) -> None:
    """
    Extract an archive.

    Parameters
    ----------
    path : Path
        Path where to extract the archive.
    filename : Path
        Path to the archive.

    Returns
    -------
    None
    """

    try:
        extract_archive(path, filename)
    except Exception as e:
        msg = f"Source must be a valid zipfile. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise RuntimeError(msg) from e


def get_repository(path: Path, source: str) -> str:
    """
    Get repository.

    Parameters
    ----------
    path : Path
        Path where to save the workflow source.
    source : str
        Git repository URL in format git://<url>.

    Returns
    -------
    None
    """
    try:
        clone_repository(path, source)
    except Exception as e:
        msg = f"Some error occurred while downloading workflow repo source. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise RuntimeError(msg) from e


def decode_base64(base64: str) -> str:
    """
    Decode base64 encoded code.

    Parameters
    ----------
    base64 : str
        The encoded code.

    Returns
    -------
    str
        The decoded code.

    Raises
    ------
    RuntimeError
        Error while decoding code.
    """
    try:
        return decode_string(base64)
    except Exception as e:
        msg = f"Some error occurred while decoding workflow source. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise RuntimeError(msg) from e


def parse_workflow_specs(spec: WorkflowSpecKFP) -> dict:
    """
    Parse workflow specs.

    Parameters
    ----------
    spec : WorkflowSpecKFP
        DHCore workflow spec.

    Returns
    -------
    dict
        Workflow specs.
    """
    try:
        return {
            "image": spec.image,
            "tag": spec.tag,
            "handler": spec.handler,
        }
    except AttributeError as e:
        msg = f"Error parsing workflow specs. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.error(msg)
        raise RuntimeError(msg)


def get_kfp_pipeline(name: str, workflow_source: str, workflow_specs: dict) -> dict:
    """
    Get KFP pipeline.

    Parameters
    ----------
    name : str
        Name of the KFP pipeline.
    workflow_source : str
        Source of the workflow.
    workflow_specs : dict
        Specifications of the workflow.

    Returns
    -------
    dict
        KFP pipeline.
    """
    try:
        if not path.isfile(workflow_source):
            raise OSError(f"source file {workflow_source} not found")
        abspath = path.abspath(workflow_source)
        if abspath not in sys.path:
            sys.path.append(abspath)
        handler = _load_module(workflow_source, workflow_specs.get("handler"))

        return handler
    except Exception as e:
        msg = f"Error getting KFP pipeline. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise RuntimeError(msg) from e


def _load_module(file_name, handler):
    """Load module from file name"""
    module = None
    if file_name:
        path = Path(file_name)
        mod_name = path.name
        if path.suffix:
            mod_name = mod_name[: -len(path.suffix)]
        spec = imputil.spec_from_file_location(mod_name, file_name)
        if spec is None:
            msg = "Error loading KFP pipeline source."
            LOGGER.exception(msg)
            raise RuntimeError(msg)

        module = imputil.module_from_spec(spec)
        spec.loader.exec_module(module)

    class_args = {}

    return _get_handler_extended(handler, class_args, namespaces=module)


def _get_handler_extended(handler_path: str, class_args: dict = {}, namespaces=None):
    """get function handler from [class_name::]handler string

    :param handler_path:  path to the function ([class_name::]handler)
    :param class_args:    optional dict of class init kwargs
    :param namespaces:    one or list of namespaces/modules to search the handler in
    :return: function handler (callable)
    """
    if "::" not in handler_path:
        return _get_function_to_exec(handler_path, namespaces)

    splitted = handler_path.split("::")
    class_path = splitted[0].strip()
    handler_path = splitted[1].strip()

    class_object = _get_class(class_path, namespaces)
    try:
        instance = class_object(**class_args)
    except TypeError as e:
        raise TypeError(f"failed to init class {class_path}\n args={class_args}") from e

    if not hasattr(instance, handler_path):
        raise ValueError(f"handler ({handler_path}) specified but doesnt exist in class {class_path}")
    return getattr(instance, handler_path)


def _module_to_namespace(namespace):
    if isinstance(namespace, ModuleType):
        members = inspect.getmembers(namespace, lambda o: inspect.isfunction(o) or isinstance(o, type))
        return {key: mod for key, mod in members}
    return namespace


def _search_in_namespaces(name, namespaces):
    """search the class/function in a list of modules"""
    if not namespaces:
        return None
    if not isinstance(namespaces, list):
        namespaces = [namespaces]
    for namespace in namespaces:
        namespace = _module_to_namespace(namespace)
        if name in namespace:
            return namespace[name]
    return None


def _get_class(class_name, namespace=None):
    """return class object from class name string"""
    if isinstance(class_name, type):
        return class_name
    class_object = _search_in_namespaces(class_name, namespace)
    if class_object is not None:
        return class_object

    try:
        class_object = _create_class(class_name)
    except (ImportError, ValueError) as e:
        raise ImportError(f"Failed to import {class_name}") from e
    return class_object


def _create_class(pkg_class: str):
    """Create a class from a package.module.class string

    :param pkg_class:  full class location,
                       e.g. "sklearn.model_selection.GroupKFold"
    """
    splits = pkg_class.split(".")
    clfclass = splits[-1]
    pkg_module = splits[:-1]
    class_ = getattr(import_module(".".join(pkg_module)), clfclass)
    return class_


def _get_function_to_exec(function, namespace):
    """return function callable object from function name string"""
    if callable(function):
        return function

    function = function.strip()
    if function.startswith("("):
        if not function.endswith(")"):
            raise ValueError('function expression must start with "(" and end with ")"')
        return eval("lambda event: " + function[1:-1], {}, {})
    function_object = _search_in_namespaces(function, namespace)
    if function_object is not None:
        return function_object

    try:
        function_object = _create_function(function)
    except (ImportError, ValueError) as e:
        raise ImportError(f"state/function init failed, handler '{function}' not found") from e
    return function_object


def _create_function(pkg_func: str):
    """Create a function from a package.module.function string

    :param pkg_func:  full function location"
    """
    splits = pkg_func.split(".")
    pkg_module = ".".join(splits[:-1])
    cb_fname = splits[-1]
    pkg_module = __import__(pkg_module, fromlist=[cb_fname])
    function_ = getattr(pkg_module, cb_fname)
    return function_
