"""
Cyral CLI
"""
from .commands import cli


def main():
    """entrypoint for the Cyral CLI"""
    # pylint: disable=no-value-for-parameter
    cli(obj={}, auto_envvar_prefix="CYRAL")


if __name__ == "__main__":
    main()
