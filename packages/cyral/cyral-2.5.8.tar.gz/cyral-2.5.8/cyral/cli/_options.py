"""
Provides click options to add to commands.
"""
from typing import List

import click


# _command_help is a callback function to print the help for the current
# function and exit. We explicitly add a --help option to all groups and
# commands with this callback to avoid having the command handler
# execute when --help is specified.
def _command_help(ctx: click.Context, _, value):
    if value:
        print(ctx.command.get_help(ctx))
        ctx.exit()


# custom decorator to add a custom help option to commands.
def command_help_option():
    """
    decorator to add --help flag to command
    """
    return click.option(
        "--help",
        "-h",
        is_flag=True,
        show_default=False,
        help="Show help message and exit.",
        callback=_command_help,
        expose_value=False,
        is_eager=True,
    )


def output_format_option(formats: List[str], default_format: str):
    """
    decorator to add --output-format flag to command
    """
    return click.option(
        "--output-format",
        "-f",
        help="Output format",
        show_default=True,
        type=click.Choice(formats),
        show_choices=True,
        default=default_format,
    )


def token_cache_option():
    """
    decorator to add --use-token-cache flag to command
    """
    return click.option(
        "--use-token-cache/--no-use-token-cache",
        help="Whether to use local token cache.",
        type=click.BOOL,
        default=True,
        show_default=True,
    )


def token_option():
    """
    decorator to add --token flag to command
    """
    return click.option(
        "--token",
        help="Access token value to use (optional)",
        type=click.STRING,
        default="",
    )


def auto_token_option():
    """
    decorator to add --auto-token flag to command
    """
    return click.option(
        "--auto-generate-token/--no-auto-generate-token",
        "auto_token",
        type=click.BOOL,
        default=True,
        help="Generate a token automatically if needed",
        show_default=True,
    )


def token_id_option(required: bool = True):
    """
    decorator to add --token-id flag to command
    """

    def callback(_, param: click.Option, value: str):
        if required and not value:
            raise click.BadParameter(f"{param.name} must not be empty")
        return value

    return click.option(
        "--token-id",
        help="ID of the token on which the action will be performed",
        type=click.STRING,
        default="",
        callback=callback,
    )
