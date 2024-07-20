from typing import Any, Callable, Optional, Union

from flytekit.core.base_task import Task
from flytekit.core.workflow import (
    FuncOut,
    PythonFunctionWorkflow,
    WorkflowFailurePolicy,
)
from flytekit.core.workflow import workflow as flytekit_workflow


def workflow(
    _workflow_function: Optional[Callable[..., Any]] = None,
    failure_policy: Optional[WorkflowFailurePolicy] = None,
    on_failure: Optional[Task] = None,
) -> Union[
    Callable[[Callable[..., FuncOut]], PythonFunctionWorkflow],
    PythonFunctionWorkflow,
    Callable[..., FuncOut],
]:
    """
    This decorator declares a function to be a Flyte workflow. Workflows are declarative entities that construct a DAG
    of tasks using the data flow between tasks.

    Unlike a task, the function body of a workflow is evaluated at serialization-time (aka compile-time). This is
    because while we can determine the entire structure of a task by looking at the function's signature, workflows need
    to run through the function itself because the body of the function is what expresses the workflow structure. It's
    also important to note that, local execution notwithstanding, it is not evaluated again when the workflow runs on
    Flyte.
    That is, workflows should not call non-Flyte entities since they are only run once (again, this is with respect to
    the platform, local runs notwithstanding).

    Example:

    .. literalinclude:: ../../../tests/flytekit/unit/core/test_workflows.py
       :pyobject: my_wf_example

    Again, users should keep in mind that even though the body of the function looks like regular Python, it is
    actually not. When flytekit scans the workflow function, the objects being passed around between the tasks are not
    your typical Python values. So even though you may have a task ``t1() -> int``, when ``a = t1()`` is called, ``a``
    will not be an integer so if you try to ``range(a)`` you'll get an error.

    Please see the :ref:`user guide <cookbook:workflow>` for more usage examples.

    :param _workflow_function: This argument is implicitly passed and represents the decorated function.
    :param failure_policy: Use the options in flytekit.WorkflowFailurePolicy
    :param on_failure: Invoke this workflow or task on failure. The Workflow / task has to match the signature of
         the current workflow, with an additional parameter called `error` Error
    """
    return flytekit_workflow(
        _workflow_function,
        failure_policy=failure_policy,
        on_failure=on_failure,
    )
