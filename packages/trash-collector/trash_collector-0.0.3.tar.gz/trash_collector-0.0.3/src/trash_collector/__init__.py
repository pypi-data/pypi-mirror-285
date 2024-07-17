from rich import color, emoji, live, print, progress_bar, spinner, status, tree
from rich.console import Console
from rich.table import Table

console = Console()

from typing import Optional

import typer
from typing_extensions import Annotated

from .search import start_search

# cli arg = req.
# cli options = not req.


def main(
    search: Annotated[
        Optional[bool],
        typer.Option(
            "--search",
            "-s",
            case_sensitive=False,
            help="Determines if it should search.",
        ),
    ] = None,
    start_dir: Annotated[
        Optional[str],
        typer.Option(
            "--start-dir", "-d", help="Defines the Directory for starting search"
        ),
    ] = ".",
    max_depth: Annotated[
        Optional[int],
        typer.Option("--max-depth", "-md", help="Max depth for search"),
    ] = -1,
    save_results: Annotated[
        Optional[bool], typer.Option("--save", "-sv", help="Saves results in a JSON.")
    ] = False,
):
    if search in [None, "--search", "-s"]:
        search = True
    if search:
        start_search(start_dir, max_depth, save_results)


if __name__ == "__main__":
    typer.run(main)
