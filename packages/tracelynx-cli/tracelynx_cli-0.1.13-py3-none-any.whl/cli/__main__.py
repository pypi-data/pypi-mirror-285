import click

from cli.links import get_link_mapping
from cli.prediction import predict
from cli.tlcli import authenticate, process_xml, config


@click.group()
@click.version_option()
@click.pass_context
@click.argument("domain")
@click.argument("username")
@click.argument("password")
def main(
    ctx: click.Context,
    domain: str,
    username: str,
    password: str,
) -> None:
    """
    TraceLynx CLI tool for performing interaction tasks from cross-domain applications.
    """
    ctx.obj = {}
    config(ctx, domain=domain)
    authenticate(ctx=ctx, username=username, password=password)


main.add_command(process_xml)
main.add_command(predict)
main.add_command(get_link_mapping)


if __name__ == "__main__":
    main()
