import click


def header(txt: str) -> None:
    click.echo(click.style(f"\n{txt}", fg="magenta", underline=True, bold=True))


def info(txt: str) -> None:
    click.echo(click.style(txt))


def debug(txt: str, verbose=False) -> None:
    if verbose:
        click.echo(click.style(txt))


def step(txt: str) -> None:
    click.echo(click.style(f"\n* {txt}", fg="magenta"))


def warn(txt: str) -> None:
    click.echo(click.style(f"WARNING: {txt}", fg="yellow"))


def cmd(txt: str) -> None:
    click.echo(click.style(f"CMD: {txt}", fg="cyan"))


def error(txt: str) -> None:
    click.echo(click.style(f"\nERROR: {txt}", fg="red"))


def success(txt: str) -> None:
    click.echo(click.style(f"\n{txt}", fg="green"))


def exception(txt: str) -> None:
    error(txt)
    exit(1)
