__version__ = "0.1.0"

import typing

import click


@click.command()
def main():
    print("lol {}".format(name))


main(auto_envvar_prefix="PINQUE")
