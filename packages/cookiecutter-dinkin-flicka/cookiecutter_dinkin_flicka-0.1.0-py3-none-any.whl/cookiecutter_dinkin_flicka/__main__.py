"""Command-line interface."""
import click


@click.group()
@click.version_option()
def main() -> None:
    """Dinkin Flicka."""

@main.command()
def hello() -> None:
    click.echo(f"Hello")


if __name__ == "__main__":
    main(prog_name="cookiecutter-dinkin-flicka")  # pragma: no cover
