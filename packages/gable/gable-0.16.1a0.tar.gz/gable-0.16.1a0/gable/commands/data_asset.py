import base64
import json
import os
from typing import List, Optional, Union, cast
from urllib.parse import quote

import click
import yaml
from click.core import Context as ClickContext
from gable.client import GableClient
from gable.helpers.check import post_data_assets_check_requests
from gable.helpers.data_asset import (
    determine_should_block,
    format_check_data_assets_json_output,
    format_check_data_assets_text_output,
    gather_python_asset_data,
    get_abs_project_root_path,
    get_schema_contents,
    get_source_names,
    is_empty_schema_contents,
)
from gable.helpers.data_asset_pyspark import (
    check_compliance_pyspark_data_asset,
    read_config_file,
    register_pyspark_data_assets,
)
from gable.helpers.data_asset_typescript import (
    check_compliance_typescript_data_asset,
    register_typescript_data_assets,
)
from gable.helpers.emoji import EMOJI
from gable.helpers.shell_output import shell_linkify_if_not_in_ci
from gable.openapi import (
    CheckDataAssetCommentMarkdownResponse,
    CheckDataAssetDetailedResponse,
    CheckDataAssetErrorResponse,
    CheckDataAssetMissingAssetResponse,
    CheckDataAssetNoContractResponse,
    ErrorResponse,
    ResponseType,
)
from gable.options import (
    ALL_SOURCE_TYPE_VALUES,
    DATABASE_SOURCE_TYPE_VALUES,
    FILE_SOURCE_TYPE_VALUES,
    SCHEMA_SOURCE_TYPE_VALUES,
    STATIC_CODE_ANALYSIS_SOURCE_TYPE_VALUES,
    SourceType,
    file_source_type_options,
    global_options,
    proxy_database_options,
    pyspark_project_options,
    python_project_options,
    required_option_callback,
    s3_project_options,
    typescript_project_options,
)
from loguru import logger
from rich.console import Console
from rich.table import Table

console = Console()


@click.group(name="data-asset")
@global_options()
def data_asset():
    """Commands for data assets"""


@data_asset.command(
    # Disable help, we re-add it in global_options()
    add_help_option=False,
    name="list",
)
@click.option(
    "-o",
    "--output",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Format of the output. Options are: table (default) or json",
)
@click.option(
    "--full",
    is_flag=True,
    help="Return full data asset details including domain and path",
)
@global_options()
@click.pass_context
def list_data_assets(ctx: ClickContext, output: str, full: bool) -> None:
    """List all data assets"""
    # Get the data
    response, success, status_code = ctx.obj.client.get_data_assets()

    # Format the output
    if output == "json":
        data_asset_list = []
        for data_asset in response:
            domain: str = data_asset.get("namespace") or data_asset.get("domain")
            path: str = data_asset.get("name") or data_asset.get("path")
            row = {"resourceName": f"{domain}:{path}"}
            if full:
                # Filter out invalid data assets...
                if "://" in domain:
                    row["type"] = domain.split("://", 1)[0]
                    row["dataSource"] = domain.split("://", 1)[1]
                    row["path"] = path
            data_asset_list.append(row)
        logger.info(json.dumps(data_asset_list))
    else:
        table = Table(show_header=True, title="Data Assets")
        table.add_column("resourceName")
        if full:
            table.add_column("type")
            table.add_column("dataSource")
            table.add_column("path")
        for data_asset in response:
            domain: str = data_asset.get("namespace") or data_asset.get("domain")
            path: str = data_asset.get("name") or data_asset.get("path")
            if not full:
                table.add_row(f"{domain}:{path}")
            else:
                # Filter out invalid data assets...
                if "://" in domain:
                    table.add_row(
                        f"{domain}:{path}",
                        domain.split("://", 1)[0],
                        domain.split("://", 1)[1],
                        path,
                    )
        console.print(table)


@data_asset.command(
    # Disable help, we re-add it in global_options()
    add_help_option=False,
    name="register",
    epilog="""Example:

gable data-asset register --source-type postgres \\
    --host prod.pg.db.host --port 5432 --db transit --schema public --table routes \\
    --proxy-host localhost --proxy-port 5432 --proxy-user root --proxy-password password""",
)
@click.option(
    "--source-type",
    callback=required_option_callback,
    is_eager=True,
    type=click.Choice(list(ALL_SOURCE_TYPE_VALUES), case_sensitive=True),
    help="""The type of data asset.
    
    For databases (postgres, mysql, mssql) a data asset is a table within the database.

    For protobuf/avro/json_schema a data asset is message/record/schema within a file.
    """,
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a dry run without actually registering the data asset.",
    default=False,
)
@proxy_database_options(
    option_group_help_text="""Options for registering database tables as data assets. Gable relies on having a proxy database that mirrors your 
    production database, and will connect to the proxy database to register tables as data assets. This is to ensure that 
    Gable does not have access to your production data, or impact the performance of your production database in any way. 
    The proxy database can be a local Docker container, a Docker container that is spun up in your CI/CD workflow, or a
    database instance in a test/staging environment. The tables in the proxy database must have the same schema as your 
    production database for all tables to be correctly registered. The proxy database must be accessible from the 
    machine that you are running the gable CLI from.

    If you're registering tables in your CI/CD workflow, it's important to only register from the main branch, otherwise 
    you may end up registering tables that do not end up in production.
    """,
    action="register",
)
@file_source_type_options(
    option_group_help_text="""Options for registering a Protobuf message, Avro record, or JSON schema object as data assets. These objects 
    represent data your production services produce, regardless of the transport mechanism. 

    If you're registering Protobuf messages, Avro records, or JSON schema objects in your CI/CD workflow, it's important 
    to only register from the main branch, otherwise you may end up registering records that do not end up in production.
    """,
    action="register",
)
@python_project_options(
    option_group_help_text="""
    Options for registering Python projects as data assets. This set of options is designed to handle the registration of Python-based projects, 
    enabling Gable to track and manage Python codebases as part of its data asset inventory.

    When registering a Python project, it's important to specify the project's entry point, which is the root directory of your project. 
    This allows Gable to correctly identify the project for analysis. Additionally, specifying the emitter function and event name key 
    helps Gable understand how your project interacts with and emits data, ensuring accurate tracking and management.

    The Python project options include:
    - Specifying the project's entry point.
    - Identifying the emitter function to track how the project emits data.
    - Defining the event name key for targeted event handling and listening.

    It's crucial to ensure that the information provided reflects the actual state of your project in your production environment. 
    When using these options as part of your CI/CD workflow, make sure to register your Python projects from the main branch. 
    Registering from feature or development branches may lead to inconsistencies and inaccuracies in the data asset registry, 
    as these branches may contain code that is not yet, or may never be, deployed to production.
    """,
    action="register",
)
@pyspark_project_options(
    option_group_help_text="""
    Options for registering Pyspark tables as data assets. This set of options is designed to handle the registration of Pyspark-based projects, 
    enabling Gable to track and manage Pyspark scripts as part of its data asset inventory.

    When registering a Pyspark table, it's important to specify the project root and the entrypoint of the job. This allows Gable to correctly
    identify the project for analysis. Additionally, .....

    The Pyspark project options include:
    - Specifying the project's entrypoint along with necessary arguments.
    - Identifying the path to the Python executable to be able to run the Pyspark script.

    It's crucial to ensure that the information provided reflects the actual state of your project in your production environment. 
    When using these options as part of your CI/CD workflow, make sure to register your Pyspark scripts from the main branch. 
    Registering from feature or development branches may lead to inconsistencies and inaccuracies in the data asset registry, 
    as these branches may contain code that is not yet, or may never be, deployed to production.
    """,
    action="register",
)
@typescript_project_options(
    option_group_help_text="""
    Options for registering Typescript projects as data assets. This set of options is designed to handle the registration of Typescript-based projects, 
    enabling Gable to track and manage Typescript codebases as part of its data asset inventory.

    When registering a Typescript project, it's important to specify the library emitting the events that are intended to be registered as data assets.

    It's crucial to ensure that the information provided reflects the actual state of your project in your production environment. 
    When using these options as part of your CI/CD workflow, make sure to register your Typescript projects from the main branch. 
    Registering from feature or development branches may lead to inconsistencies and inaccuracies in the data asset registry, 
    as these branches may contain code that is not yet, or may never be, deployed to production.
    """,
    action="register",
)
@s3_project_options(
    option_group_help_text="""
    Options for registering S3 files as data assets. This set of options is designed to handle the registration of S3 files, 
    enabling Gable to track and manage them as part of its data asset inventory.

    When registering S3 files, it's important to specify the AWS bucket containing the files that are intended to be registered as data assets.
    """,
    action="register",
)
@global_options()
@click.pass_context
def register_data_asset(
    ctx: ClickContext,
    source_type: str,
    dry_run: bool,
    host: str,
    port: int,
    db: str,
    schema: str,
    table: Union[str, None],
    proxy_host: str,
    proxy_port: int,
    proxy_db: str,
    proxy_schema: str,
    proxy_user: str,
    proxy_password: str,
    files: tuple,
    project_root: Optional[str],
    emitter_function: Optional[str],
    emitter_payload_parameter: Optional[str],
    emitter_name_parameter: Optional[str],
    event_name_key: Optional[str],
    emitter_file_path: Optional[str],
    spark_job_entrypoint: Optional[str],
    connection_string: Optional[str],
    csv_schema_file: Optional[str],
    library: Optional[str],
    exclude: Optional[str],
    bucket: Optional[str],
    include_prefix: Optional[tuple[str, ...]],
    exclude_prefix: Optional[tuple[str, ...]],
    lookback_days: int,
    history: Optional[bool],
    skip_profiling: bool,
    row_sample_count: Optional[int],
    config_file: Optional[click.File],
    config_entrypoint_path: Optional[str],
    config_args_path: Optional[str],
) -> None:
    """Registers a data asset with Gable"""
    tables: Union[list[str], None] = (
        [t.strip() for t in table.split(",")] if table else None
    )
    if source_type in DATABASE_SOURCE_TYPE_VALUES:
        proxy_db = proxy_db if proxy_db else db
        proxy_schema = proxy_schema if proxy_schema else schema
        files_list: list[str] = []
        database_schema = f"{db}.{schema}"
    elif source_type in STATIC_CODE_ANALYSIS_SOURCE_TYPE_VALUES:
        files_list: list[str] = []
        database_schema = ""
    else:
        # Turn the files tuple into a list
        files_list: list[str] = list(files)
        # This won't be set for file-based data assets, but we need to pass through
        # the real db.schema value in case the proxy database has different names
        database_schema = ""

    source_names: list[str] = []
    schema_contents: list[str] = []
    client: GableClient = ctx.obj.client
    check_response_pydantic = None
    if source_type in SCHEMA_SOURCE_TYPE_VALUES:
        schema_contents = get_schema_contents(
            source_type=source_type,
            dbuser=proxy_user,
            dbpassword=proxy_password,
            db=proxy_db,
            dbhost=proxy_host,
            dbport=proxy_port,
            schema=proxy_schema if proxy_schema else schema,
            tables=tables,
            files=files_list,
        )
        source_names = get_source_names(
            ctx=ctx,
            source_type=source_type,
            dbhost=host,
            dbport=port,
            files=files_list,
        )
        if is_empty_schema_contents(source_type, schema_contents):
            raise click.ClickException(
                f"{EMOJI.RED_X.value} No data assets found to register! You can use the --debug or --trace flags for more details.",
            )
        if dry_run:
            logger.info("Dry run mode. Data asset registration not performed.")
        request = {
            "sourceType": source_type,
            "sourceNames": source_names,
            "databaseSchema": database_schema,
            "schema": schema_contents,
            "dryRun": dry_run,
        }
        register_response, success, _status_code = client.post_data_asset_ingest(
            request
        )
    elif source_type == SourceType.PYTHON.value:
        # Click options should enforce these being required, but to make pyright happy check anyways
        if (
            not project_root
            or not emitter_function
            or not emitter_payload_parameter
            or not emitter_file_path
            or not event_name_key
        ):
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Missing required options for Python project registration. You can use the --debug or --trace flags for more details."
            )
        source_names, schema_contents = gather_python_asset_data(
            get_abs_project_root_path(project_root),
            emitter_file_path,
            emitter_function,
            emitter_payload_parameter,
            event_name_key,
            exclude,
            ctx.obj.client,
        )
        if is_empty_schema_contents(source_type, schema_contents):
            raise click.ClickException(
                f"{EMOJI.RED_X.value} No data assets found to register! You can use the --debug or --trace flags for more details.",
            )
        if dry_run:
            logger.info("Dry run mode. Data asset registration not performed.")
        request = {
            "sourceType": source_type,
            "sourceNames": source_names,
            "databaseSchema": database_schema,
            "schema": schema_contents,
            "dryRun": dry_run,
        }
        register_response, success, _status_code = client.post_data_asset_ingest(
            request
        )
    elif source_type == SourceType.PYSPARK.value:
        if not project_root or not (connection_string or csv_schema_file):
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Missing required options for Spark project registration. You can use the --debug or --trace flags for more details."
            )
        if not spark_job_entrypoint:
            if not config_file or not config_entrypoint_path:
                raise click.ClickException(
                    f"{EMOJI.RED_X.value} Missing required options for Spark project registration: --config-entrypoint-path is required when using --config-file."
                )
            spark_job_entrypoint = read_config_file(
                config_file, config_entrypoint_path, config_args_path
            )

        response_pydantic, success, _status_code = register_pyspark_data_assets(
            ctx,
            spark_job_entrypoint,
            project_root,
            connection_string,
            csv_schema_file,
            dry_run,
        )
        register_response = (
            response_pydantic.dict()
        )  # shim so we can use the same response handling below
    elif source_type == SourceType.TYPESCRIPT.value:
        if not library and not emitter_function:
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Missing required options for Typescript project registration. Either --library or --emitter-function must be specified. You can use the --help option for more details."
            )
        if library and emitter_function:
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Only one of --library or --emitter-function may be specified. You can use the --help option for more details."
            )
        if emitter_function and (
            not emitter_payload_parameter
            or not emitter_file_path
            or (not event_name_key and not emitter_name_parameter)
        ):
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Missing required options for Typescript project registration when using --emitter-function. Options --emitter-payload-parameter, --emitter-file-path, and either --event-name-key or --event-name-parameter are required. You can use the --help option for more details."
            )
        if not project_root:
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Missing required option --project-root for Typescript project registration. You can use the --debug or --trace flags for more details."
            )
        response_pydantic, success, _status_code = register_typescript_data_assets(
            ctx,
            library,
            project_root,
            emitter_file_path,
            emitter_function,
            emitter_payload_parameter,
            emitter_name_parameter,
            event_name_key,
            dry_run,
        )
        register_response = (
            response_pydantic.dict()
        )  # shim so we can use the same response handling below
    elif source_type == SourceType.S3.value:
        from gable.helpers.data_asset_s3 import (
            detect_s3_data_assets_history,
            register_and_check_s3_data_assets,
            validate_input,
        )

        validate_input(
            "register", bucket, lookback_days, include_prefix, exclude_prefix, history
        )

        if history:
            detect_s3_data_assets_history(
                bucket,  # type: ignore (input validation ensures bucket is not None, this quashes linter)
                include,  # type: ignore (input validation ensures include is not None or empty, this quashes linter)
            )
            return

        # We want to both register and check S3 data assets since customers will be using the register command
        # in live change detection.
        register_response_pydantic, check_response_pydantic = (
            register_and_check_s3_data_assets(
                ctx,
                bucket,  # type: ignore (input validation ensures bucket is not None, this quashes linter)
                lookback_days,
                row_sample_count,
                include_prefix,
                exclude_prefix,
                dry_run,
                skip_profiling,
            )
        )
        register_response = register_response_pydantic[
            0
        ].dict()  # shim so we can use the same response handling below
        success = register_response_pydantic[1]
    else:
        raise NotImplementedError(f"Unknown source type: {source_type}")

    if not success:
        raise click.ClickException(
            f"{EMOJI.RED_X.value} Registration failed for some data assets: {str(register_response)}"
        )
    registered_assets = register_response["registered"]
    registered_output = ", ".join(
        shell_linkify_if_not_in_ci(
            f"{client.ui_endpoint}/assets/{quote(asset, safe='')}",
            asset,
        )
        for asset in registered_assets
    )
    logger.info(
        f"{EMOJI.GREEN_CHECK.value} Registration successful:\n{registered_output}"
    )
    if not dry_run:
        logger.info(register_response["message"])
    else:
        logger.info("Dry run mode. Data asset registration not performed.")

    # Only for S3 data asset registration
    if check_response_pydantic is not None:
        format_compliance_check_response_for_cli(check_response_pydantic, "text")


@data_asset.command(
    # Disable help, we re-add it in global_options()
    add_help_option=False,
    name="check",
    epilog="""Example:

gable data-asset check --source-type protobuf --files ./**/*.proto""",
)
@click.option(
    "--source-type",
    required=True,
    type=click.Choice(ALL_SOURCE_TYPE_VALUES, case_sensitive=True),
    help="""The type of data asset.
    
    For databases (postgres, mysql, mssql) the check will be performed for all tables within the database.

    For protobuf/avro/json_schema the check will be performed for all file(s)
    """,
)
@click.option(
    "-o",
    "--output",
    type=click.Choice(["text", "json", "markdown"]),
    default="text",
    help="Format of the output. Options are: text (default), json, or markdown which is intended to be used as a PR comment",
)
@proxy_database_options(
    option_group_help_text="""Options for checking contract compliance for tables in a relational database. The check will be performed
    for any tables that have a contract associated with them.
    
    Gable relies on having a proxy database that mirrors your production database, and will connect to the proxy database
    to perform the check in order to perform the check as part of the CI/CD process before potential changes in the PR are
    merged.
    """,
    action="check",
)
@file_source_type_options(
    option_group_help_text="""Options for checking Protobuf message(s), Avro record(s), or JSON schema object(s) for contract violations.""",
    action="check",
)
@python_project_options(
    option_group_help_text="""
    Options for checking contract compliance for assets emitted in Python project code. This set of options mirrors the registration options, and will
    perform a check for any assets that have a contract associated with them.
    """,
    action="check",
)
@typescript_project_options(
    option_group_help_text="""
    Options for verifying contract compliance for assets emitted from TypeScript project code. 
    These options reflect those available during asset registration and will perform validation 
    checks for any assets linked to an existing contract.
    """,
    action="check",
)
@pyspark_project_options(
    option_group_help_text="""
    Options for checking contract compliance of data assets from Pyspark tables. 

    When checking a Pyspark table, it's important to specify the project root and the entrypoint of the job. This allows Gable to correctly
    identify the project for analysis.

    The Pyspark project options include:
    - Specifying the project's entrypoint along with necessary arguments.
    - Identifying the path to the Python executable to be able to run the Pyspark script.
    """,
    action="check",
)
@s3_project_options(
    option_group_help_text="""
    Options for checking S3 contract compliance of s3 files from a bucket.

    When registering S3 files, it's important to specify the AWS bucket containing the files that are intended to be registered as data assets.
    Other options are:
    - S3 bucket name
    - The number of days to look back to expand the history depth of files to check (default is 0)
    - The list of prefixes to include in the check (default None to include everything)
    """,
    action="check",
)
@global_options()
@click.pass_context
def check_data_asset(
    ctx: ClickContext,
    source_type: str,
    output: str,
    host: str,
    port: int,
    db: str,
    schema: str,
    table: str,
    proxy_host: str,
    proxy_port: int,
    proxy_db: str,
    proxy_schema: str,
    proxy_user: str,
    proxy_password: str,
    files: tuple,
    project_root: str,
    emitter_function: str,
    emitter_payload_parameter: str,
    emitter_name_parameter: str,
    event_name_key: str,
    emitter_file_path: str,
    library: Optional[str],
    spark_job_entrypoint: Optional[str],
    connection_string: Optional[str],
    csv_schema_file: Optional[str],
    exclude: Optional[str],
    bucket: Optional[str],
    include_prefix: Optional[tuple[str, ...]],
    exclude_prefix: Optional[tuple[str, ...]],
    lookback_days: int,
    history: Optional[bool],
    skip_profiling: bool,
    row_sample_count: Optional[int],
    config_file: Optional[click.File],
    config_entrypoint_path: Optional[str],
    config_args_path: Optional[str],
) -> None:
    """Checks data asset(s) against a contract"""
    # Standardize the source type
    tables: Union[list[str], None] = (
        [t.strip() for t in table.split(",")] if table else None
    )
    response_type: ResponseType = (
        ResponseType.COMMENT_MARKDOWN if output == "markdown" else ResponseType.DETAILED
    )

    schema_contents = []
    source_names = []
    if source_type == SourceType.PYTHON.value:
        # Click options should enforce these being required, but to make pyright happy check anyways
        if (
            not project_root
            or not emitter_function
            or not emitter_payload_parameter
            or not emitter_file_path
            or not event_name_key
        ):
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Missing required options for Python project registration. You can use the --debug or --trace flags for more details."
            )
        source_names, schema_contents = gather_python_asset_data(
            project_root,
            emitter_file_path,
            emitter_function,
            emitter_payload_parameter,
            event_name_key,
            exclude,
            ctx.obj.client,
        )
        if is_empty_schema_contents(source_type, schema_contents):
            raise click.ClickException(
                f"{EMOJI.RED_X.value} No data assets found to check! You can use the --debug or --trace flags for more details."
            )
        results = post_data_assets_check_requests(
            ctx.obj.client,
            response_type,
            source_type,
            source_names,
            db,
            schema,
            schema_contents,
        )
    elif (
        source_type in SCHEMA_SOURCE_TYPE_VALUES
        or source_type in FILE_SOURCE_TYPE_VALUES
    ):
        schema_contents = get_schema_contents(
            source_type=source_type,
            dbuser=proxy_user,
            dbpassword=proxy_password,
            db=proxy_db or db,
            dbhost=proxy_host,
            dbport=proxy_port,
            schema=proxy_schema or schema,
            tables=tables,
            files=[] if files is None else list(files),
        )
        source_names = get_source_names(
            ctx=ctx,
            source_type=source_type,
            dbhost=host,
            dbport=port,
            files=[] if files is None else list(files),
        )
        if is_empty_schema_contents(source_type, schema_contents):
            raise click.ClickException(
                f"{EMOJI.RED_X.value} No data assets found to check! You can use the --debug or --trace flags for more details."
            )
        results = post_data_assets_check_requests(
            ctx.obj.client,
            response_type,
            source_type,
            source_names,
            db,
            schema,
            schema_contents,
        )
    elif source_type == SourceType.TYPESCRIPT.value:
        if not library and (
            not emitter_function
            or not emitter_payload_parameter
            or not emitter_file_path
            or (not event_name_key and not emitter_name_parameter)
        ):
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Missing required options for Typescript project registration. You can use the --help option for more details."
            )
        if not project_root:
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Missing required option '--project-root' for Typescript project registration. You can use the --debug or --trace flags for more details."
            )
        results = check_compliance_typescript_data_asset(
            ctx,
            library,
            project_root,
            emitter_file_path,
            emitter_function,
            emitter_payload_parameter,
            emitter_name_parameter,
            event_name_key,
            response_type,
        )
    elif source_type == SourceType.PYSPARK.value:
        if not project_root or not (connection_string or csv_schema_file):
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Missing required options for Spark project registration. You can use the --debug or --trace flags for more details."
            )
        if not spark_job_entrypoint:
            if not config_file or not config_entrypoint_path:
                raise click.ClickException(
                    f"{EMOJI.RED_X.value} Missing required options for Spark project registration: --config-entrypoint-path is required when using --config-file."
                )
            spark_job_entrypoint = read_config_file(
                config_file, config_entrypoint_path, config_args_path
            )
        results = check_compliance_pyspark_data_asset(
            ctx,
            spark_job_entrypoint,
            project_root,
            connection_string,
            csv_schema_file,
            response_type,  # type: ignore
        )
    elif source_type == SourceType.S3.value:
        from gable.helpers.data_asset_s3 import check_compliance_s3_data_assets
        from gable.helpers.data_asset_s3 import validate_input as validate_s3_input

        validate_s3_input(
            "check", bucket, lookback_days, include_prefix, exclude_prefix, history
        )

        results = check_compliance_s3_data_assets(
            ctx,
            response_type,  # type: ignore
            bucket,  # type: ignore (input validation ensures bucket is not None, this quashes linter)
            lookback_days,
            include_prefix,
            exclude_prefix,
            skip_profiling,
            row_sample_count,
        )
    else:
        raise click.ClickException(
            f"{EMOJI.RED_X.value} Source type {source_type} is not supported."
        )

    format_compliance_check_response_for_cli(results, output)


def format_compliance_check_response_for_cli(results, output: str) -> None:
    if isinstance(results, ErrorResponse):
        raise click.ClickException(
            f"Error checking data asset(s): {results.title} ({results.id})\n\t{results.message}"
        )
    # If the output was text, or json
    if output == "text" or output == "json":
        # Cast to list of detailed responses
        results = cast(
            list[
                Union[
                    CheckDataAssetDetailedResponse,
                    CheckDataAssetErrorResponse,
                    CheckDataAssetNoContractResponse,
                    CheckDataAssetMissingAssetResponse,
                ]
            ],
            results,
        )
        # Determine if we should block (non-zero exit code) or not
        should_block = determine_should_block(results)
        if output == "text":
            # Format the results
            output_string = format_check_data_assets_text_output(results)
        else:
            output_string = format_check_data_assets_json_output(results)

        if should_block:
            logger.info(output_string)
            raise click.ClickException("Contract violation(s) found")
        else:
            logger.info(output_string)
    else:
        # If the output was markdown
        results = cast(CheckDataAssetCommentMarkdownResponse, results)
        # Only print the markdown if it's not None or empty, otherwise the stdout will contain a newline. Print markdown
        # to stdout, so we can read it separately from the error output to determine if we should comment on a PR
        if results.markdown and results.markdown != "":
            logger.info(results.markdown)
        # Decide if we should comment on or block the PR based on whether or not there were any contract violations, and the
        # enforcement level of the contacts that had the violations. In either case, write something to stderr so there's
        # a record logged in the CI/CD output
        if results.shouldBlock:
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Contract violations found, maximum enforcement level was 'BLOCK'"
            )
        elif results.shouldAlert:
            logger.error(
                f"{EMOJI.YELLOW_WARNING.value} Contract violations found, maximum enforcement level was 'ALERT'"
            )
        # If there were errors
        if results.errors:
            errors_string = "\n".join([error.json() for error in results.errors])
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Contract checking failed for some data assets:\n{errors_string}"
            )


@data_asset.command(
    name="create-contract",
    epilog="""Example:
                    
gable data-asset create-contract --data-asset-id postgres://sample.host:5432:db.public.table --output-dir contracts""",
)
@click.pass_context
@click.argument(
    "data_asset_ids",
    nargs=-1,
)
@click.option(
    "--output-dir",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    help="Directory to output contracts. This directory must exist",
)
def create_data_asset_contracts(
    ctx: ClickContext, data_asset_ids: List[str], output_dir: Optional[str]
) -> None:
    """Creates the YAML contract specification for a list of data assets

    The specification that is produced is based off the registered data asset but the
    user will need to fill in places marked with 'PLACEHOLDER:' such as field
    descriptions and ownership information.
    """
    for data_asset_id in data_asset_ids:
        logger.debug(f"Creating contract for data asset: {data_asset_id}")

        # Base64 encode the data asset ID
        encoded_resource_name = base64.b64encode(data_asset_id.encode("utf-8")).decode(
            "utf-8"
        )

        # Get the inferred contract for the data asset
        (
            response,
            success,
            status_code,
        ) = ctx.obj.client.get_data_asset_infer_contract(encoded_resource_name)
        if not success:
            raise click.ClickException(
                f"{EMOJI.RED_X.value} Failed to generate contract for data asset: {data_asset_id} ({status_code}))"
            )

        # Get the raw contract spec and convert to yaml
        contract_spec_dict = json.loads(response["contractSpecRaw"])
        contract_spec_yaml = yaml.dump(
            contract_spec_dict, default_flow_style=False, sort_keys=False
        )

        # Print out the data asset
        logger.info(contract_spec_yaml)

        if output_dir:
            # Get the contract name for the filename
            name = response["contractSpec"]["name"].lower().replace(".", "_")
            filepath = os.path.join(output_dir, f"{name}.yaml")

            # Write the contract spec to a file
            with open(filepath, "w") as f:
                f.write(contract_spec_yaml)
