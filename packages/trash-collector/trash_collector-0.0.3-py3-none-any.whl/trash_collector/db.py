import os
import typing
from pathlib import Path

import json

import typing_extensions
from .utils import depth_from_file_path, depth_from_folder_path


class BaseItem:
    def __init__(self, path: str, depth: int) -> None:
        self.path = path
        self.depth = depth
        self.size = self._get_size(path)

    def _get_size(self, path):
        return os.stat(path).st_size

    def __repr__(self) -> str:
        return f"< {self.path} >"

    def __lt__(self, other):
        return self.size < other.size


class File(BaseItem):
    def __init__(self, path: str, depth: int, file_name: str) -> None:
        super().__init__(path, depth)
        self.file_name = file_name

    def to_json(self):
        _dict = {
            "path": self.path,
            "depth": self.depth,
            "size": self.size,
            "file_name": self.file_name,
        }
        return _dict

    def __repr__(self) -> str:
        return f"<File {self.path} {self.size} >"


class Folder(BaseItem):
    def __init__(self, path, depth) -> None:
        super().__init__(path, depth)
        self.searched = False
        self.num_of_children = 0

    def to_json(self):
        _dict = {
            "path": self.path,
            "depth": self.depth,
            "size": self.size,
            "searched": self.searched,
            "num_of_children": self.num_of_children,
        }
        return _dict

    def __repr__(self) -> str:
        return f"<Folder {self.path} {self.size} >"


class DB:
    def __init__(self) -> None:
        self.data: dict[int, list[BaseItem]] = {}

    def save_to_json(self, path: str = "trash-collector.json"):
        with open(path, "w") as f:
            _dict = {"file": [], "folder": []}
            for _l in self.data.values():
                for _v in _l:
                    if type(_v) == File:
                        _dict["file"].append(_v.to_json())
                    if type(_v) == Folder:
                        _dict["folder"].append(_v.to_json())
            json.dump(_dict, f)

    def folder_size_count(self):
        folders: list[Folder] = self.sort_by_type(Folder)
        files: list[File] = self.sort_by_type(File)
        for folder in folders:
            for file in files:
                file_parents = list(Path(file.path).parents)
                if Path(folder.path) in file_parents:
                    folder.size += file.size
                    folder.num_of_children += 1

    def sort_by_type(self, _type: BaseItem):
        _list: list[BaseItem] = []
        for _item_list in self.data.values():
            for value in _item_list:
                if type(value) == _type:
                    _list.append(value)
        return sorted(_list)

    def add_file(self, path, file_name):
        depth = depth_from_file_path(path)
        try:
            self.data[depth]
        except:
            self.data[depth] = []
        self.data[depth].append(File(path, depth, file_name))

    def add_folder(self, path):
        depth = depth_from_folder_path(path)
        try:
            self.data[depth]
        except:
            self.data[depth] = []
        self.data[depth].append(Folder(path, depth))

    def get_folder(self):
        # I could just use self.data.values ??? why is this code like this
        for i in self.data.keys():
            for value in self.data[i]:
                if type(value) == Folder and not value.searched:
                    value.searched = True
                    return value
        return None
