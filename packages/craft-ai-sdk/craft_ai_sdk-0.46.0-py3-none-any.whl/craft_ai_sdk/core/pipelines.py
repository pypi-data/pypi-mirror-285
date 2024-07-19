import warnings
import os
import requests

from ..exceptions import SdkException
from ..sdk import BaseCraftAiSdk
from ..utils import (
    log_action,
    log_func_result,
    multipartify,
    handle_data_store_response,
)
from .steps import (
    _add_inputs_outputs_in_message,
    _validate_create_step_parameters,
    _prepare_create_step_data,
    _prepare_create_step_files,
    _wait_create_until_ready,
)


def _create_pipeline_with_step(sdk: BaseCraftAiSdk, pipeline_name: str, step_name: str):
    url = f"{sdk.base_environment_api_url}/pipelines"
    body = {
        "pipeline_name": pipeline_name,
        "step_names": [step_name],
    }

    return sdk._post(url, json=body)


@log_func_result("Pipeline creation")
def create_pipeline(
    sdk: BaseCraftAiSdk,
    pipeline_name,
    function_path=None,
    function_name=None,
    description=None,
    container_config=None,
    inputs=None,
    outputs=None,
    timeout_s=None,
    **kwargs,
):
    """Create a pipeline from a function located on a remote repository or locally.

    Use :obj:`STEP_PARAMETER` to explicitly set a value to null or fall back on
    project information.
    You can also use :obj:`container_config.included_folders` to specify the files and
    folders required for the pipeline execution. This is useful if your repository
    contains large files that are not required for the pipeline execution, such as
    documentation or test files. Indeed there is a maximum limit of 5MB for the
    total size of the content specified with :obj:`included_folders`.

    Args:
        pipeline_name (:obj:`str`): Name of the pipeline to be created.
        function_path (:obj:`str`, optional): Path to the file that contains the
            function. This parameter is required if parameter "dockerfile_path"
            is not specified.
        function_name (:obj:`str`, optional): Name of the function in that file.
            This parameter is required if parameter "dockerfile_path" is not
            specified.
        description (:obj:`str`, optional): Description. Defaults to None.
        container_config (:obj:`dict[str, str]`, optional): Some pipeline configuration,
            with the following optional keys:

            * ``"language"`` (:obj:`str`): Language and version used for the pipeline.
              Defaults to falling back on project information. The accepted formats
              are "python:3.X-slim", where "3.X" is a supported version of Python,
              and "python-cuda:3.X-Y.Z" for GPU environments, where "Y.Z" is a
              supported version of CUDA. The list of supported versions is available
              on the official documentation website at
              https://mlops-platform-documentation.craft.ai.
            * ``"repository_url"`` (:obj:`str`): Remote repository url.
              Defaults to falling back on project information.
            * ``"repository_branch"`` (:obj:`str`): Branch name. Defaults to falling
              back on project information.
            * ``"repository_deploy_key"`` (:obj:`str`): Private SSH key of the
              repository.
              Defaults to falling back on project information, can be set to null.
              The key should retain the header/footer beacon with : "BEGIN/END RSA
              PRIVATE KEY".
            * ``"requirements_path"`` (:obj:`str`): Path to the requirements.txt
              file. Environment variables created through
              :func:`create_or_update_environment_variable` can be used
              in requirements.txt, as in ``"${ENV_VAR}"``.
              Defaults to falling back on project information, can be set to null.
            * ``"included_folders"`` (:obj:`list[str]`): List of folders and files
              in the repository required for the pipeline execution.
              Defaults to falling back on project information, can be set to null.
              Total size of included_folders must be less than 5MB.
            * ``"system_dependencies"`` (:obj:`list[str]`): List of system
              dependencies.
              Defaults to falling back on project information, can be set to null.
            * ``"dockerfile_path"`` (:obj:`str`): Path to the Dockerfile. This
              parameter should only be used as a last resort and for advanced use.
              When specified, the following parameters should be set to null:
              ``"function_path"``, ``"function_name"``, ``"language"``,
              ``"requirements_path"`` and ``"system_dependencies"``.
            * ``"local_folder`` (:obj:`str`): Path to local folder where the pipeline is
              stored.

        inputs(`list` of instances of :class:`Input`): List of inputs. Each
            parameter of the pipeline function should be specified as an instance of
            :class:`Input` via this parameter `inputs`.
            During the execution of the pipeline, the value of the inputs would be
            passed as function arguments.
        outputs(`list` of instances of :class:`Output`): List of the pipeline
            outputs. For the pipeline to have outputs, the function should return a
            :obj:`dict` with the name of the output as keys and the value of the
            output as values. Each output should be specified as an instance
            of :class:`Output` via this parameter `outputs`.
        timeout_s (:obj:`int`): Maximum time (in seconds) to wait for the pipeline to
            be created. 3min (180s) by default, and at least 2min (120s).

    Returns:
        :obj:`dict`: Created pipeline represented as :obj:`dict` with the following
        keys:

        * ``"pipeline_name"`` (:obj:`str`): Name of the pipeline.
        * ``"created_at"`` (:obj:`str`): Pipeline date of creation.
        * ``"inputs"`` (:obj:`list` of :obj:`dict`): List of open inputs
          of the pipeline. Each open input is represented as a :obj:`dict` with the
          following keys:

          * ``"input_name"`` (:obj:`str`): Name of the open input.
          * ``"step_name"`` (:obj:`str`): Name of the step that provides the open
            input.
          * ``"data_type"`` (:obj:`str`): Data type of the open input.
          * ``"description"`` (:obj:`str`): Description of the open input.
          * ``"default_value"`` (:obj:`str`): Default value of the open input.
          * ``"is_required"`` (:obj:`bool`): Whether the open input is required or
            not.

        * ``"outputs"`` (:obj:`list` of :obj:`dict`): List of open outputs
          of the pipeline. Each open output is represented as a :obj:`dict` with the
          following keys:

          * ``"output_name"`` (:obj:`str`): Name of the open output.
          * ``"step_name"`` (:obj:`str`): Name of the step that provides the open
            output.
          * ``"data_type"`` (:obj:`str`): Data type of the open output.
          * ``"description"`` (:obj:`str`): Description of the open output.

        * ``"container_config"`` (:obj:`dict[str, str]`): Some pipeline
          configuration, with the following optional keys:

          * ``"language"`` (:obj:`str`): Language and version used for the pipeline.
            The accepted formats are "python:3.X-slim", where "3.X" is a supported
            version of Python, and "python-cuda:3.X-Y.Z" for GPU environments,
            where "Y.Z" is a supported version of CUDA. The list of supported
            versions is available on the official documentation website at
            https://mlops-platform-documentation.craft.ai.
          * ``"repository_branch"`` (:obj:`str`): Branch name.
          * ``"repository_url"`` (:obj:`str`): Remote repository url.
          * ``"included_folders"`` (:obj:`list[str]`): List of folders and
            files in the repository required for the pipeline execution.
          * ``"system_dependencies"`` (:obj:`list[str]`): List of system
            dependencies.
          * ``"dockerfile_path"`` (:obj:`str`): Path to the Dockerfile.
          * ``"requirements_path"`` (:obj:`str`): Path to the requirements.txt
            file.

        * ``"creation_info"`` (:obj:`dict`): Information about the step creation (Note
          that this is only returned if the pipeline was created without a step):

          * ``"commit_id"`` (:obj:`str`): The commit id on which the pipeline was
            built.
          * ``"status"`` (:obj:`str`): The pipeline status, always ``"Ready"`` when
            this function returns.
          * ``"origin"`` (:obj:`str`): The origin of the step, can be
            ``"git_repository"`` or ``"local"``.
    """
    # For backward compatibility, a pipeline can be created with a single step:
    args_are_none = all(
        arg is None
        for arg in [
            function_name,
            description,
            container_config,
            inputs,
            outputs,
            timeout_s,
        ]
    )
    # with create_pipeline(:pipeline_name:, :step_name:),
    if args_are_none and function_path is not None and not kwargs:
        warnings.warn(
            "Providing the step name as a positional argument is deprecated and will "
            "be removed in a future version. Please use the step_name keyword argument instead.",  # noqa: E501
            FutureWarning,
        )
        return _create_pipeline_with_step(sdk, pipeline_name, function_path)

    # or with create_pipeline(:pipeline_name:, step_name=:step_name:).
    if args_are_none and function_path is None and kwargs.keys() == {"step_name"}:
        return _create_pipeline_with_step(sdk, pipeline_name, kwargs["step_name"])

    if len(kwargs) != 0:
        raise ValueError(
            f"create_pipeline() got an unexpected keyword argument {kwargs.keys()[0]}"
        )

    # Otherwise, the pipeline is created with a "hidden" step
    container_config = {} if container_config is None else container_config.copy()
    timeout_s = 3 * 60 if timeout_s is None else timeout_s
    _validate_create_step_parameters(inputs, outputs, timeout_s)

    url = f"{sdk.base_environment_api_url}/pipelines"
    data = _prepare_create_step_data(
        function_path,
        function_name,
        description,
        container_config,
        inputs,
        outputs,
        pipeline_name=pipeline_name,
    )
    files = _prepare_create_step_files(container_config, data, function_path)

    log_action(
        sdk,
        f'Please wait while pipeline "{pipeline_name}" is being created. '
        "This may take a while...",
    )

    start_time = sdk._get_time()
    created_pipeline, response = sdk._post(
        url, data=multipartify(data), files=files, get_response=True
    )

    if response.status_code != 206:
        message = _add_inputs_outputs_in_message(
            f'Pipeline "{pipeline_name}" created',
            created_pipeline.get("inputs", []),
            created_pipeline.get("outputs", []),
        )
        log_action(sdk, message)
        return created_pipeline

    # The pipeline is still building. Keep checking its status until it is ready
    return _wait_create_until_ready(
        sdk, pipeline_name, get_pipeline, timeout_s, start_time
    )


def get_pipeline(sdk: BaseCraftAiSdk, pipeline_name):
    """Get a single pipeline if it exists.

    Args:
        pipeline_name (:obj:`str`): Name of the pipeline to get.

    Returns:
        None if the pipeline does not exist, otherwise pipeline information, with
        the following keys:

        * ``"pipeline_name"`` (:obj:`str`): Name of the pipeline.
        * ``"created_at"`` (:obj:`str`): Pipeline date of creation.
        * ``"created_by"`` (:obj:`str`): ID of the user who created the deployment.
        * ``"last_execution_id"`` (:obj:`str`): ID of the last execution of the
          pipeline.
        * ``"inputs"`` (:obj:`list` of :obj:`dict`): List of open inputs
          of the pipeline. Each open input is represented as a :obj:`dict` with the
          following keys:

          * ``"input_name"`` (:obj:`str`): Name of the open input.
          * ``"step_name"`` (:obj:`str`): Name of the step that provides the open
            input.
          * ``"data_type"`` (:obj:`str`): Data type of the open input.
          * ``"description"`` (:obj:`str`): Description of the open input.
          * ``"default_value"`` (:obj:`str`): Default value of the open input.
          * ``"is_required"`` (:obj:`bool`): Whether the open input is required or
            not.

        * ``"outputs"`` (:obj:`list` of :obj:`dict`): List of open outputs
          of the pipeline. Each open output is represented as a :obj:`dict` with the
          following keys:

          * ``"output_name"`` (:obj:`str`): Name of the open output.
          * ``"step_name"`` (:obj:`str`): Name of the step that provides the open
            output.
          * ``"data_type"`` (:obj:`str`): Data type of the open output.
          * ``"description"`` (:obj:`str`): Description of the open output.

        * ``"container_config"`` (:obj:`dict[str, str]`): Some pipeline
          configuration, with the following optional keys:

          * ``"language"`` (:obj:`str`): Language and version used for the pipeline.
            The accepted formats are "python:3.X-slim", where "3.X" is a supported
            version of Python, and "python-cuda:3.X-Y.Z" for GPU environments,
            where "Y.Z" is a supported version of CUDA. The list of supported
            versions is available on the official documentation website at
            https://mlops-platform-documentation.craft.ai.
          * ``"repository_branch"`` (:obj:`str`): Branch name.
          * ``"repository_url"`` (:obj:`str`): Remote repository url.
          * ``"included_folders"`` (:obj:`list[str]`): List of folders and
            files in the repository required for the pipeline execution.
          * ``"system_dependencies"`` (:obj:`list[str]`): List of system
            dependencies.
          * ``"dockerfile_path"`` (:obj:`str`): Path to the Dockerfile.
          * ``"requirements_path"`` (:obj:`str`): Path to the requirements.txt
            file.

        * ``"creation_info"`` (:obj:`dict`): Information about the step creation:

          * ``"commit_id"`` (:obj:`str`): The commit id on which the pipeline was
            built.
          * ``"status"`` (:obj:`str`): The pipeline status, always ``"Ready"`` when
            this function returns.
          * ``"origin"`` (:obj:`str`): The origin of the step, can be
            ``"git_repository"`` or ``"local"``.
    """
    try:
        url = f"{sdk.base_environment_api_url}/pipelines/{pipeline_name}"
        pipeline = sdk._get(url)
    except SdkException as error:
        if error.status_code == 404:
            return None
        raise error

    latest_execution = sdk._get(
        f"{sdk.base_environment_api_url}/pipelines/{pipeline_name}/executions/latest"
    )
    pipeline["last_execution_id"] = (
        latest_execution.get("execution_id", None)
        if latest_execution is not None
        else None
    )
    return pipeline


def list_pipelines(sdk: BaseCraftAiSdk):
    """Get the list of all pipelines.

    Returns:
        :obj:`list` of :obj:`dict`: List of pipelines represented as :obj:`dict`
        with the following keys:

        * ``"pipeline_name"`` (:obj:`str`): Name of the pipeline.
        * ``"created_at"`` (:obj:`str`): Pipeline date of creation.
        * ``"status"`` (:obj:`str`): Status of the pipeline.
    """
    url = f"{sdk.base_environment_api_url}/pipelines"

    return sdk._get(url)


@log_func_result("Pipeline deletion")
def delete_pipeline(
    sdk: BaseCraftAiSdk, pipeline_name, force_deployments_deletion=False
):
    """Delete a pipeline identified by its name.

    Args:
        pipeline_name (:obj:`str`): Name of the pipeline.
        force_deployments_deletion (:obj:`bool`, optional): if True the associated
            endpoints will be deleted too. Defaults to False.

    Returns:
        :obj:`dict`: The deleted pipeline and its associated deleted deployments
        represented as a :obj:`dict` with the following keys:

            * ``"pipeline"`` (:obj:`dict`): Deleted pipeline represented as
              :obj:`dict` with the following keys:

              * ``"name"`` (:obj:`str`): Name of the deleted pipeline.

            * ``"deployments"`` (:obj:`list`): List of deleted deployments
              represented as :obj:`dict` with the following keys:

              * ``"name"`` (:obj:`str`): Name of the deleted deployments.
              * ``"execution_rule"`` (:obj:`str`): Execution rule of the deleted
                deployments.
    """
    url = f"{sdk.base_environment_api_url}/pipelines/{pipeline_name}"
    params = {
        "force_deployments_deletion": force_deployments_deletion,
    }
    return sdk._delete(url, params=params)


def _get_download_presigned_url(sdk: BaseCraftAiSdk, pipeline_name):
    url = f"{sdk.base_environment_api_url}/pipelines/{pipeline_name}/download"
    presigned_url = sdk._get(url)["signed_url"]
    return presigned_url


@log_func_result("pipeline download")
def download_pipeline_local_folder(sdk: BaseCraftAiSdk, pipeline_name, folder):
    """Download a pipeline's local folder as a `.tgz` archive.

    Only available if the pipeline's ``origin`` is ``"local_folder"``. This archive
    contains the files that were in the ``local_folder`` parameter provided during
    pipeline creation, and that were included based on the pipeline's
    ``container_config`` property.

    Args:
        pipeline_name (:obj:`str`): Name of the pipline to be downloaded.
        folder (:obj:`str`): Path to the folder where the file will be saved.

    Returns:
        None
    """
    presigned_url = _get_download_presigned_url(sdk, pipeline_name)
    resp = requests.get(presigned_url)
    object_content = handle_data_store_response(resp)

    if isinstance(folder, str):
        path = os.path.join(os.path.abspath(folder), f"{pipeline_name}.tgz")
        with open(path, "wb") as f:
            f.write(object_content)
    else:
        raise ValueError("'folder' must be a string")
