import json
from typing import List

import click
from click.core import Context as ClickContext
from gable.cli.helpers.contract import (
    contract_files_to_contract_inputs,
    contract_files_to_post_contract_request,
)
from gable.cli.helpers.emoji import EMOJI
from gable.cli.helpers.shell_output import shell_linkify_if_not_in_ci
from gable.cli.options import global_options
from gable.sdk.models import ContractPublishResponse
from loguru import logger


@click.group()
def contract():
    """Validate/publish contracts and check data asset compliance"""


@contract.command(
    # Disable help, we re-add it in global_options()
    add_help_option=False,
    epilog="""Examples:

    gable contract publish contract1.yaml

    gable contract publish **/*.yaml""",
)
@click.argument(
    "contract_files",
    type=click.File(),
    nargs=-1,
)
@global_options()
@click.pass_context
def publish(ctx: ClickContext, contract_files: List[click.File]):
    """Publishes data contracts to Gable"""
    request = contract_files_to_contract_inputs(contract_files)
    response: List[ContractPublishResponse] = ctx.obj.client.contracts.publish(request)
    published_contracts = [r for r in response if r.success]
    unpublished_contracts = [r for r in response if not r.success]
    if len(unpublished_contracts) > 0:
        raise click.ClickException(
            f"Publish failed: {json.dumps([r.message for r in unpublished_contracts])}"
        )
    updated_contracts = ", ".join(
        shell_linkify_if_not_in_ci(
            f"{ctx.obj.client.ui_endpoint}/contracts/{cid}",
            str(cid),
        )
        for cid in published_contracts
    )

    logger.info(f"\u2705 {len(published_contracts)} contract(s) published")
    logger.info(f"\t{updated_contracts}")


@contract.command(
    # Disable help, we re-add it in global_options()
    add_help_option=False,
    epilog="""Examples:\n
\b
  gable contract validate contract1.yaml
  gable contract validate **/*.yaml""",
)
@click.argument("contract_files", type=click.File(), nargs=-1)
@global_options()
@click.pass_context
def validate(ctx: ClickContext, contract_files: List[click.File]):
    """Validates the configuration of the data contract files"""
    request = contract_files_to_post_contract_request(contract_files)
    response, success, _status_code = ctx.obj.client.post_contract_validate(request)
    # For each input file, zip up the emoji, file name, and result message into a tuple
    zipped_results = zip(
        [
            # Compute emoji based on whether the contract is valid
            EMOJI.GREEN_CHECK.value if m.strip() == "VALID" else EMOJI.RED_X.value
            for m in response["message"]
        ],
        contract_files,
        [m.replace("\n", "\n\t") for m in response["message"]],
    )
    string_results = "\n".join(
        [
            # For valid contracts, just print the check mark and name
            (
                f"{x[0]} {x[1].name}"
                if x[2].strip() == "VALID"
                # For invalid contracts, print the check mark, name, and error message
                else f"{x[0]} {x[1].name}:\n\t{x[2]}"
            )
            for x in zipped_results
        ]
    )
    if not success:
        raise click.ClickException(f"\n{string_results}\nInvalid contract(s)")
    logger.info(string_results)
    logger.info("All contracts are valid")
