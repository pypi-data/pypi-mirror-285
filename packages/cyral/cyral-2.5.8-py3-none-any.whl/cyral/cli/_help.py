"""Helpers for generating documentation"""

from click import HelpFormatter


class MDHelpFormatter(HelpFormatter):
    """MDHelpFormatter is a specialed HelpFormatter that outputs documentation
    in the markdown syntax.
    """

    def __init__(self, **kwargs):
        """
        Construct an MDHelpFormatter. The arguments are the same as for
        click.HelpFormatter.
        """
        super().__init__(**kwargs)

    def write_usage(self, prog, args="", prefix="Usage"):
        """Writes a usage line into the buffer.

        :param prog: the program name.
        :param args: whitespace separated list of arguments.
        :param prefix: the prefix for the first line.
        """
        self.write(f"## {prefix}\n")
        self.write(f"```\n{prog} {args}\n```\n")

    def write_dl(self, rows, col_max=30, col_spacing=2):
        """Writes a definition list into the buffer.  This is how options
        and commands are usually formatted.

        :param rows: a list of two item tuples for the terms and values.
        :param col_max: the maximum width of the first column.
        :param col_spacing: the number of spaces between the first and
                            second column.
        """
        rows = list(rows)
        self.write("|Name|Description|\n|---|---|\n")
        for row in rows:
            name, desc = tuple(row)
            name = _escape(name)
            desc = _escape(desc)
            self.write(f"|`{name}`|{desc}|\n")

    def write_heading(self, heading):
        """Writes a heading into the buffer."""
        self.write(f"### {heading}\n")


def _escape(txt: str) -> str:
    """markdown escape a string, currently limited to |."""
    return txt.replace("|", " \\| ")
