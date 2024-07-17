from __future__ import annotations

import typing

from mlrun import build_function, run_function

if typing.TYPE_CHECKING:
    from mlrun.projects.operations import BuildStatus
    from mlrun.runtimes import BaseRuntime
    from mlrun.runtimes.base import RunObject


def run_job(function: BaseRuntime, exec_config: dict, function_args: dict) -> RunObject:
    """
    Run Mlrun job.

    Parameters
    ----------
    function : BaseRuntime
        Mlrun function.
    function_args : dict
        Function arguments.

    Returns
    -------
    dict
        Execution results.
    """
    function_args["local"] = True
    return run_function(function, **function_args)


def run_build(function: BaseRuntime, exec_config: dict, function_args: dict) -> BuildStatus:
    """
    Run Mlrun build.

    Parameters
    ----------
    kwargs : dict
        Function arguments. Expect function reference, force_build, commands, target_image

    Returns
    -------
    dict
        Execution results.
    """
    return build_function(
        function,
        force_build=exec_config.get("force_build", False),
        commands=exec_config.get("commands", None),
        image=exec_config.get("target_image", None),
        requirements=exec_config.get("requirements", None),
    )
