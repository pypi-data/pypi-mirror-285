import json
import os

import click

from xml_report.link_prediction_example import json_data

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@click.command("get-links-between-items-of-type")
@click.argument("resource-types", nargs=+1)
@click.argument("output", type=click.Path(file_okay=True, dir_okay=False))
@click.pass_context
def get_link_mapping(ctx: click.Context, resource_types: tuple, output: str) -> None:
    """
    Retrieving from TraceLynx API the link mapping from Test Cases and Test Functions
    :param ctx:
    :param resource_types:
    :param output:
    :return:
    """

    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))

    # json_data2 = get_predicted_link(
    #     ctx=ctx,
    #     traceability_id=3,
    # )

    with open(f"{output}", 'w') as file:
        json.dump(json_data, file)
