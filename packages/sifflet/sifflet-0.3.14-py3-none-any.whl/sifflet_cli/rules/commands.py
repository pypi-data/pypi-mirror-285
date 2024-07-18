from typing import List

import click
from click_aliases import ClickAliasedGroup
from sifflet_sdk.constants import (
    DEFAULT_PAGE_NUM,
    DEFAULT_PAGE_SIZE,
    OutputType,
    SIFFLET_CONFIG_CTX,
)
from sifflet_sdk.rules.service import RulesService

from sifflet_cli.rules.displayrules import DisplayRules


@click.group(cls=ClickAliasedGroup)
def rules():
    """List and control rules"""


@rules.command(name="list", aliases=["ls"])
@click.option("--name", "-n", type=str, required=False, help="Search rules by name")
@click.option(
    "--output",
    "-o",
    type=click.Choice(OutputType.list(), case_sensitive=False),
    required=False,
    help="Display the result either as a Table or raw Json",
    default="table",
    show_default=True,
)
@click.option(
    "--page-size",
    "page_size",
    type=int,
    required=False,
    help="Page size of the server side pagination",
    default=DEFAULT_PAGE_SIZE,
    show_default=True,
)
@click.option(
    "--page-num",
    "page_num",
    type=int,
    required=False,
    help="Page number of the server side pagination",
    default=DEFAULT_PAGE_NUM,
    show_default=True,
)
@click.pass_context
def list_rules(
    ctx,
    name: str,
    output: str = "table",
    page_size: int = DEFAULT_PAGE_SIZE,
    page_num: int = DEFAULT_PAGE_NUM,
):
    """Display all rules created"""
    sifflet_config = ctx.obj[SIFFLET_CONFIG_CTX]
    service = RulesService(sifflet_config, page_size=page_size, page_num=page_num)
    response_rules, response_total_count = service.fetch_rules(filter_name=name)
    utils = DisplayRules(output_type=output, page_num=page_num)
    utils.show_rules(rules=response_rules, total_count=response_total_count, filter_name=name)


@rules.command()
@click.option("--id", "ids", multiple=True, required=True, help="The rule id to trigger")
@click.pass_context
def run(ctx, ids: List[str]):
    """Run one or several rules - requires rule id(s)"""
    sifflet_config = ctx.obj[SIFFLET_CONFIG_CTX]
    service = RulesService(sifflet_config)
    rule_runs = service.run_rules(ids)
    service.wait_rule_runs(rule_runs)


@rules.command("run-history")
@click.option("--id", "rule_id", required=True, help="id of the rules id to fetch")
@click.option(
    "--output",
    "-o",
    type=click.Choice(OutputType.list(), case_sensitive=False),
    default="table",
    required=False,
    help="Display the result either as a Table or raw Json",
)
@click.option(
    "--page-size",
    "page_size",
    type=int,
    required=False,
    help="Page size of the server side pagination",
    default=DEFAULT_PAGE_SIZE,
    show_default=True,
)
@click.option(
    "--page-num",
    "page_num",
    type=int,
    required=False,
    help="Page number of the server side pagination",
    default=DEFAULT_PAGE_NUM,
    show_default=True,
)
@click.pass_context
def run_history(
    ctx,
    rule_id: str,
    output: str = "table",
    page_size: int = DEFAULT_PAGE_SIZE,
    page_num: int = DEFAULT_PAGE_NUM,
):
    """Display all rule runs for a given rule id"""
    sifflet_config = ctx.obj[SIFFLET_CONFIG_CTX]
    service = RulesService(sifflet_config, page_size=page_size, page_num=page_num)
    rule_info, rule_runs, total_count = service.fetch_run_history(rule_id=rule_id)
    utils = DisplayRules(output_type=output)
    utils.show_run_history(rule_info, rule_runs, total_count)
