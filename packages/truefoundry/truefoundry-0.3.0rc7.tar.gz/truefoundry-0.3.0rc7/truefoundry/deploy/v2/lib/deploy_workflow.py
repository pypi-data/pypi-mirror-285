import os
import sys
from pathlib import Path
from typing import List, Union

from flytekit.configuration import Image as FlytekitImage
from flytekit.configuration import ImageConfig, SerializationSettings
from flytekit.models.launch_plan import LaunchPlan as FlyteLaunchPlan
from flytekit.tools.repo import serialize as serialize_workflow
from flytekit.tools.translator import TaskSpec as FlyteTaskSpec
from flytekit.tools.translator import WorkflowSpec as FlyteWorkflowSpec
from google.protobuf.json_format import MessageToDict

from truefoundry.deploy.auto_gen import models as auto_gen_models
from truefoundry.deploy.lib.clients.servicefoundry_client import (
    ServiceFoundryServiceClient,
)
from truefoundry.deploy.lib.dao.workspace import get_workspace_by_fqn
from truefoundry.deploy.lib.model.entity import Deployment
from truefoundry.deploy.v2.lib.source import (
    local_source_to_remote_source,
)
from truefoundry.logger import logger
from truefoundry.pydantic_v1 import ValidationError


def _handle_code_upload_for_workflow(
    workflow: auto_gen_models.Workflow, workspace_fqn: str
) -> auto_gen_models.Workflow:
    new_workflow = workflow.copy(deep=True)
    new_workflow.source = local_source_to_remote_source(
        local_source=workflow.source,
        workspace_fqn=workspace_fqn,
        component_name=workflow.name,
    )
    return new_workflow


# this function does validation that num_workflows = 1, this also validates task_config is passed correctly.
# This is verified by pydantic but doing it here also as error messages are not clear in pydantic
def _validate_workflow_entities(
    workflow_entities: List[Union[FlyteWorkflowSpec, FlyteLaunchPlan, FlyteTaskSpec]],
):
    workflow_objs = []
    launch_plans = []
    tasks = []
    for entity in workflow_entities:
        if isinstance(entity, FlyteWorkflowSpec):
            workflow_objs.append(entity)
        elif isinstance(entity, FlyteLaunchPlan):
            launch_plans.append(entity)
        elif isinstance(entity, FlyteTaskSpec):
            tasks.append(entity)
        else:
            raise ValueError(f"Invalid entity found in workflow: {entity}")
    if len(workflow_objs) != 1:
        raise ValueError(
            f"Workflow file must have exactly one workflow object. Found {len(workflow_objs)}"
        )
    if len(launch_plans) != 1:
        raise ValueError(
            f"Workflow file must have exactly one launch plan. Found {len(launch_plans)}"
        )

    error_message_to_use_truefoundry_decorators = """Invalid task definition for task: {}, Please use valid truefoundry decorator/class and pass task_config for tasks.
        You can import truefoundry task decorators using:
        `from truefoundry.workflow import task, ContainerTask, map_task`
        You can pass task config using `task_config` parameter in the task definition. Task config should be one of the following:
        `PythonTaskConfig`, or  `ContainerTaskConfig`. You can import these using:
        `from truefoundry.workflow import PythonTaskConfig, ContainerTaskConfig`
         """
    for task in tasks:
        if not task.template.custom:
            raise ValueError(
                error_message_to_use_truefoundry_decorators.format(
                    task.template.id.name
                )
            )
        try:
            auto_gen_models.FlyteTaskCustom.validate(task.template.custom)
        except ValidationError:
            raise ValueError(
                error_message_to_use_truefoundry_decorators.format(
                    task.template.id.name
                )
            ) from None


def _get_relative_package_path_from_filepath(
    project_root_path: str, filepath: str
) -> str:
    """
    This function returns the relative package path from the project root path for a given file path.
    e.g. if project_root_path = /home/user/project and filepath = /home/user/project/src/module.py
    then the function will return src.module
    """
    relative_file_path = os.path.relpath(filepath, project_root_path)
    path = Path(relative_file_path)
    package_path = str(path.with_suffix("")).replace(os.path.sep, ".")

    return package_path


def _generate_manifest_for_workflow(
    workflow: auto_gen_models.Workflow,
):
    settings = SerializationSettings(
        # We are adding these defaults to avoid validation errors in flyte objects
        image_config=ImageConfig(default_image=FlytekitImage(name="", tag="", fqn="")),
        python_interpreter=sys.executable,
    )
    source_absolute_path = os.path.abspath(workflow.source.project_root_path)

    workflow_file_absolute_path = os.path.join(
        source_absolute_path, workflow.workflow_file_path
    )
    if not os.path.exists(workflow_file_absolute_path):
        raise FileNotFoundError(
            f"Workflow file not found at {workflow_file_absolute_path}. Workflow file path should be relative to project root path."
        )

    package_path = _get_relative_package_path_from_filepath(
        project_root_path=source_absolute_path, filepath=workflow_file_absolute_path
    )

    workflow_entities = serialize_workflow(
        pkgs=[package_path], settings=settings, local_source_root=source_absolute_path
    )
    _validate_workflow_entities(workflow_entities)

    workflow.flyte_entities = []
    for entity in workflow_entities:
        message_dict = MessageToDict(entity.to_flyte_idl())
        # proto message to dict conversion converts all int to float. so we need this hack
        if (
            message_dict.get("template")
            and message_dict["template"].get("custom")
            and message_dict["template"]["custom"].get("truefoundry")
        ):
            parsed_model = auto_gen_models.FlyteTaskCustom.parse_obj(
                message_dict["template"]["custom"]
            )
            message_dict["template"]["custom"]["truefoundry"] = parsed_model.truefoundry

        workflow.flyte_entities.append(message_dict)

    # this step is just to verify if pydantic model is still valid after adding flyte_entities
    auto_gen_models.Workflow.validate({**workflow.dict()})


def deploy_workflow(
    workflow: auto_gen_models.Workflow, workspace_fqn: str, wait: bool = True
) -> Deployment:
    _generate_manifest_for_workflow(workflow)
    workspace_id = get_workspace_by_fqn(workspace_fqn).id

    logger.info(
        f"Deploying workflow {workflow.name} to workspace {workspace_fqn} ({workspace_id})"
    )

    workflow = _handle_code_upload_for_workflow(
        workflow=workflow, workspace_fqn=workspace_fqn
    )

    client = ServiceFoundryServiceClient()
    response = client.deploy_application(
        workspace_id=workspace_id, application=workflow
    )
    logger.info(
        "🚀 Deployment started for application '%s'. Deployment FQN is '%s'.",
        workflow.name,
        response.fqn,
    )
