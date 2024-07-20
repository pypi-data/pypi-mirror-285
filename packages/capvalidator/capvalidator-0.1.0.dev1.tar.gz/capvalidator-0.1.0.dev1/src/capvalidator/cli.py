import click
from capvalidator import __version__, validate_cap, check_schema, check_signature  # noqa


@click.group()
@click.version_option(version=__version__)
def cli():
    """capvalidator"""

    pass


@click.command()
@click.pass_context
@click.option('--type', 'validation_type',
              type=click.Choice(['total', 'schema', 'signature']),
              required=False, default='total')
@click.argument('cap_xml', type=click.File(mode="rb", errors="ignore"))
def validate(ctx, cap_xml, validation_type) -> None:
    """Validate a CAP alert"""

    cap = cap_xml.read()

    if validation_type == "total":
        result = validate_cap(cap)
    elif validation_type == "schema":
        result = check_schema(cap)
    elif validation_type == "signature":
        result = check_signature(cap)

    click.echo(f"{result.passed}: {result.message}")


cli.add_command(validate)
