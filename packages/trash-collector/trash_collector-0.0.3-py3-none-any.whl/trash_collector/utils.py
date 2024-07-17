from pathlib import Path


def text_from_filesize(size: int):
    KB = 1_024
    MB = KB**2
    GB = KB**3
    TB = KB**4
    if size < KB:
        return f"{size} bytes"
    elif size < MB:
        return f"{size / KB:.3f} Kb"
    elif size < GB:
        return f"{size / MB:.3f} Mb"
    elif size < TB:
        return f"{size / GB:.3f} Gb"
    else:
        return f"{size / TB:.3f} Tb"


def depth_from_folder_path(path: str):
    return len(Path(path).parents)


def depth_from_file_path(path: str):
    return len(Path(path).parents) - 1
