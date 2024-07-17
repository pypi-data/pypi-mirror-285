from typing import List

import click
from click.core import Context as ClickContext
from gable.helpers.contract import contract_files_to_post_contract_request
from gable.helpers.emoji import EMOJI
from gable.helpers.shell_output import shell_linkify_if_not_in_ci
from gable.options import global_options
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
    request = contract_files_to_post_contract_request(contract_files)
    response, success, status_code = ctx.obj.client.post_contract(request)
    if not success:
        raise click.ClickException(f"Publish failed: {response['message']}")
    updated_contracts = ", ".join(
        shell_linkify_if_not_in_ci(
            f"{ctx.obj.client.ui_endpoint}/contracts/{cid}",
            cid,
        )
        for cid in response["contractIds"]
    )
    if len(response["contractIds"]) == 0:
        logger.info("\u2705 No contracts published")
    else:
        logger.info(f"\u2705 {len(response['contractIds'])} contract(s) published")
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
