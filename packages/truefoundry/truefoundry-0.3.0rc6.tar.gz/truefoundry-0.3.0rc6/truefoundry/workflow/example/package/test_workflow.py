import os
from functools import partial
from pathlib import Path
from typing import List, Tuple

from truefoundry.deploy import Image, NvidiaGPU, Resources
from truefoundry.workflow import (
    ContainerTask,
    ContainerTaskConfig,
    FlyteDirectory,
    PythonTaskConfig,
    TaskPythonBuild,
    conditional,
    map_task,
    task,
    workflow,
)

cpu_task_config = PythonTaskConfig(
    image=TaskPythonBuild(
        python_version="3.9",
        pip_packages=["flytekit==1.10.3"],
    ),
    resources=Resources(cpu_request=0.45),
)


# figure out naming
@task(task_config=cpu_task_config)
def should_train_tokenizer(tokenizer: str) -> bool:
    return not bool(tokenizer)


@task(
    task_config=cpu_task_config,
    # currently we will not support the caching, but keeping here for now
    # cache=True,
    # cache_version="1.0",
)
def train_tokenizer() -> str:
    return "trained_tokenizer"


@task(
    task_config=PythonTaskConfig(
        image=TaskPythonBuild(
            python_version="3.9",
            pip_packages=["flytekit==1.10.3", "pynvml==11.5.0"],
            cuda_version="11.5-cudnn8",
        ),
        env={
            "NVIDIA_DRIVER_CAPABILITIES": "compute,utility",
            "NVIDIA_VISIBLE_DEVICES": "all",
        },
        resources=Resources(cpu_request=0.45, devices=[NvidiaGPU(name="T4", count=1)]),
    ),
)
def train_model(tokenizer: str) -> Tuple[FlyteDirectory, str]:
    import flytekit
    from package.test_workflow import random
    from pynvml import nvmlDeviceGetCount, nvmlInit

    nvmlInit()
    assert nvmlDeviceGetCount() > 0

    random.random()
    working_dir = flytekit.current_context().working_directory
    local_dir = Path(os.path.join(working_dir, "csv_files"))
    local_dir.mkdir(exist_ok=True)

    with open(os.path.join(local_dir, "model"), "w", encoding="utf-8") as f:
        f.write(tokenizer)

    return FlyteDirectory(path=str(local_dir)), "hello"


@task(task_config=cpu_task_config)
def get_validation_data() -> List[str]:
    return ["foo", "bar", "baz"]


@task(task_config=cpu_task_config)
def validate_model(model: FlyteDirectory, tokenizer: str, validation_data: str) -> bool:
    print(validation_data)
    model_path = os.path.join(model, "model")
    with open(model_path, "r", encoding="utf-8") as f:
        return f.read() == tokenizer


@task(task_config=cpu_task_config)
def all_good(validations: List[bool]) -> bool:
    return all(validations)


echo = ContainerTask(
    name="echo",
    task_config=ContainerTaskConfig(
        image=Image(
            image_uri="bash:4.1",
        )
    ),
)


@task(task_config=cpu_task_config)
def random(tokenizer: str) -> Tuple[FlyteDirectory, str]:
    return FlyteDirectory(path=""), "random"


@workflow
def train(tokenizer: str = "") -> bool:
    stt = should_train_tokenizer(tokenizer=tokenizer)
    model, t = (
        conditional("train_tokenizer")
        .if_(stt.is_true())
        .then(train_model(tokenizer=tokenizer))
        .else_()
        .then(random(tokenizer=tokenizer))
    )
    validation_task = partial(validate_model, model=model, tokenizer=t)
    validation_data = get_validation_data()
    validations = map_task(
        validation_task,
        concurrency=2,
    )(validation_data=validation_data)
    echo()
    return all_good(validations=validations)


if __name__ == "__main__":
    train()
