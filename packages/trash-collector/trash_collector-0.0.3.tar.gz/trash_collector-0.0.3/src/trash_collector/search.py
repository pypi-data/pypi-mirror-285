import os
import pathlib
import sys
import time

from .db import DB, File, Folder
from rich import console, print, table
from .utils import depth_from_folder_path, text_from_filesize

console = console.Console()


def start_search(start_dir, max_depth, should_save: bool):
    with console.status("[bold green]Working on tasks...\n") as status:
        console.log("Initializing DB")
        time.sleep(1)
        db = DB()
        root = start_dir
        depth = depth_from_folder_path(start_dir)
        if max_depth == -1:
            max_depth = sys.maxsize
        else:
            console.log(
                "[bold red] Warning! [/bold red][white]Max depth only hides the results, the files are still checked! :boom:"
            )
        db.add_folder(start_dir)
        console.log("starting :sparkles: :cake: :sparkles:")
        while True:  # depth < max_depth
            result = db.get_folder()
            if not result:
                break

            root = result.path
            depth = result.depth
            # print(result)
            # print("depth is", depth)

            for item in os.listdir(root):
                path = os.path.join(root, item)
                if os.path.isfile(path):
                    db.add_file(path, item)
                if os.path.isdir(path):
                    db.add_folder(path)
        console.log("Database is processing...")
        db.folder_size_count()

        console.log("Ordering results...")
        results: list[Folder] = db.sort_by_type(Folder)
        folder_table = table.Table()
        folder_table.add_column("Path", justify="left", style="cyan")
        folder_table.add_column("Num Of Children", justify="center", style="green")
        folder_table.add_column("Size", justify="right", style="red")
        for f in results:
            folder_table.add_row(
                f.path, str(f.num_of_children), text_from_filesize(f.size)
            )

        results: list[File] = db.sort_by_type(File)
        file_table = table.Table()
        file_table.add_column("Path", justify="left", style="cyan")
        file_table.add_column("Size", justify="right", style="red")

        for f in results:
            file_table.add_row(f.path, text_from_filesize(f.size))
        console.print(f"Here are the File results! :cake:")
        console.print(file_table)

        console.print(f"Here are the Folder results! :sparkles:")
        console.print(folder_table)

        if should_save:
            db.save_to_json()
            console.print("Saved results to JSON!")
