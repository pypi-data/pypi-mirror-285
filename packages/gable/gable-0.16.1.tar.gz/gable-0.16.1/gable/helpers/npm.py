import os
import subprocess
from typing import Optional, Union

import click
from gable.client import GableClient
from gable.helpers.auth import set_npm_config_credentials
from loguru import logger

BASE_NPX_CMD = [
    "npx",
    "-y",
    "-q",
    "@gable-eng/sca@<1.0.0",
]


def prepare_npm_environment(client: GableClient) -> None:
    # Verify node is installed
    check_node_installed()

    # Get temporary NPM credentials, set as environment variables
    npm_credentials = client.get_auth_npm()
    set_npm_config_credentials(npm_credentials)


def check_node_installed():
    try:
        result = subprocess.run(
            ["node", "--version"], check=True, stdout=subprocess.PIPE, text=True
        )
        version = result.stdout.strip().replace("v", "")
        if int(version.split(".")[0]) < 14:
            raise click.ClickException(
                f"Node.js version {version} is not supported. Please install Node.js 14 or later."
            )
    except FileNotFoundError:
        raise click.ClickException(
            "Node.js is not installed. Please install Node.js 18 or later."
        )


def run_sca_pyspark(
    project_root: str,
    python_executable_path: str,
    spark_job_entrypoint: str,
    connection_string: Optional[str],
    csv_schema_file: Optional[str],
    api_endpoint: Union[str, None] = None,
) -> str:
    try:
        commands = [
            "pyspark",
            project_root,
            "--python-executable-path",
            python_executable_path,
            "--spark-job-entrypoint",
            spark_job_entrypoint,
        ]
        if connection_string is not None:
            commands += ["--connection-string", connection_string]
        if csv_schema_file is not None:
            commands += ["--csv-schema-file", csv_schema_file]
        cmd = get_cmd(
            api_endpoint,
            commands,
        )
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            logger.debug(result.stderr)
            raise click.ClickException(f"Error running Gable SCA: {result.stderr}")
        logger.debug(result.stdout)
        logger.trace(result.stderr)
        # The sca CLI prints the results to stdout,and everything else to trace/warn/debug/error
        return result.stdout
    except Exception as e:
        logger.opt(exception=e).debug("Error running Gable SCA")
        raise click.ClickException(
            "Error running Gable SCA: Please ensure you have the @gable-eng/sca package installed."
        )


def run_sca_python(
    project_root: str,
    emitter_file_path: str,
    emitter_function: str,
    emitter_payload_parameter: str,
    event_name_key: str,
    exclude_paths: Optional[str],
    api_endpoint: Union[str, None] = None,
) -> str:
    try:
        excludes = ["--exclude", exclude_paths] if exclude_paths else []
        cmd = get_cmd(
            api_endpoint,
            [
                "python",
                project_root,
                "--emitter-file-path",
                emitter_file_path,
                "--emitter-function",
                emitter_function,
                "--emitter-payload-parameter",
                emitter_payload_parameter,
                "--event-name-key",
                event_name_key,
            ]
            + excludes,
        )

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            logger.debug(result.stderr)
            raise click.ClickException(f"Error running Gable SCA: {result.stderr}")
        logger.debug(result.stdout)
        logger.trace(result.stderr)
        # The sca CLI prints the results to stdout,and everything else to trace/warn/debug/error
        return result.stdout
    except Exception as e:
        logger.opt(exception=e).debug("Error running Gable SCA")
        raise click.ClickException(
            "Error running Gable SCA: Please ensure you have the @gable-eng/sca package installed."
        )


def run_sca_typescript(
    library: Optional[str],
    project_root: str,
    emitter_file_path: Optional[str],
    emitter_function: Optional[str],
    emitter_payload_parameter: Optional[str],
    event_name_key: Optional[str],
    event_name_parameter: Optional[str],
    api_endpoint: Union[str, None] = None,
):
    try:
        if library:
            options = ["--library", library]
        else:
            options = [
                "--emitter-file-path",
                emitter_file_path,
                "--emitter-function",
                emitter_function,
                "--emitter-payload-parameter",
                emitter_payload_parameter,
            ]
            if event_name_key:
                options += ["--event-name-key", event_name_key]
            else:
                options += ["--event-name-parameter", event_name_parameter]

        cmd = get_cmd(
            api_endpoint,
            ["typescript", project_root] + options,
        )
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            logger.debug(result.stderr)
            raise click.ClickException(f"Error running Gable SCA: {result.stderr}")
        logger.debug(result.stdout)
        logger.debug(result.stderr)
        # The sca CLI prints the results to stdout,and everything else to trace/warn/debug/error
        return result.stdout
    except Exception as e:
        logger.opt(exception=e).debug("Error running Gable SCA")
        raise click.ClickException(
            "Error running Gable SCA: Please ensure you have the @gable-eng/sca package installed."
        )


def get_cmd(gable_api_endpoint: Union[str, None], args: list[str]) -> list[str]:
    """Constructs the full command to run sca"""
    cmd = get_base_npx_cmd(gable_api_endpoint) + args
    logger.trace("sca cmd: " + " ".join(cmd))
    return cmd


def get_base_npx_cmd(gable_api_endpoint: Union[str, None]) -> list[str]:
    """Based on the endpoint and GABLE_LOCAL environment variable, decide if we should use the local package
    Returns: list[str] - The base command to run sca, either using npx + @gable-eng/sca or node + local path
    """
    gable_local = os.environ.get("GABLE_LOCAL")
    is_endpoint_localhost = (
        gable_api_endpoint is not None
        and gable_api_endpoint.startswith("http://localhost")
    )
    if gable_local == "false":
        return BASE_NPX_CMD
    if gable_local == "true" or is_endpoint_localhost:
        logger.trace("Configuring local settings")
        try:
            # Needs to be a dynamic import because this file is excluded from the bundled package
            from gable.local import config_local

            local_sca_path = config_local()
            return [
                "node",
                local_sca_path,
            ]
        except ImportError as e:
            logger.trace(
                f'Error importing local config, trying GABLE_LOCAL_SCA_PATH: {os.environ.get("GABLE_LOCAL_SCA_PATH")}'
            )
            local_sca_path = os.environ.get("GABLE_LOCAL_SCA_PATH")
            if local_sca_path is not None:
                return [
                    "node",
                    local_sca_path,
                ]

    return BASE_NPX_CMD
