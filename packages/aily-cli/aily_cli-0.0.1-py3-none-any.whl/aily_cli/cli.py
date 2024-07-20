import click


@click.group()
def cli():
    pass


@cli.command()
@click.option("--name", prompt="Project name")
def new(name):
    click.echo(f"Creating new project: {name}")


@cli.command()
@click.option("--model", prompt="Model name", default="")
@click.option("--key", prompt="Api key", default="")
def run(model, key):
    click.echo(f"Running model: {model} with key: {key}")


if __name__ == "__main__":
    cli()
