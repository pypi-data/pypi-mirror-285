import click
import httpx

from auth.BearerAuth import BearerAuth


@click.command("predict-links")
@click.argument('traceability_matrix_id', type=int)
@click.pass_context
def predict(ctx: click.Context, traceability_matrix_id: int) -> None:
    """
    Requests the execution of the AI prediction for the given traceability matrix.
    :param ctx:
    :param traceability_matrix_id:
    :return:
    """
    click.secho(f'Requesting prediction for Traceability Matrix: {traceability_matrix_id}', fg='yellow')

    api_url = ctx.obj['api_url']
    organization_id = ctx.obj['organization_id']
    auth = BearerAuth(ctx.obj["auth"]["access_token"])
    url: str = f"{api_url}/{organization_id}/traceability/{traceability_matrix_id}/run"

    response = httpx.post(url, auth=auth)
    if response.status_code != 200:
        raise click.ClickException("Request failed")

    click.secho(f"Request of AI Prediction for Traceability Matrix: {traceability_matrix_id}, allocated", fg='green')
