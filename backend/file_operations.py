"""Filesystem operations for the file manager (no GUI or terminal interaction)."""

from pathlib import Path
import os
import shutil
from send2trash import send2trash


def item_exists(path: Path) -> bool:
    """Check whether an entry exists, including dangling symbolic links."""
    try:
        path.lstat()
        return True
    except FileNotFoundError:
        return False


def validate_filename(name: str) -> str:
    name = name.strip()
    if not name:
        raise ValueError("Name cannot be empty!")
    if name in (".", "..") or "/" in name or "\\" in name:
        raise ValueError("Enter a single filename, not a path!")
    if os.name == "nt" and os.path.isreserved(name):
        raise ValueError(f"Invalid Windows filename: {name}")
    return name


def _reject_link(path: Path) -> None:
    """Conservative policy: do not perform write operations on links/junctions."""
    if path.is_symlink() or path.is_junction():
        raise ValueError(f"Symbolic links and junctions are not supported for this operation: {path}")


def get_item_info(item: Path) -> dict:
    if item.is_symlink():
        item_type = "symlink"
    elif item.is_junction():
        item_type = "junction"
    elif item.is_dir():
        item_type = "folder"
    elif item.is_file():
        item_type = "file"
    else:
        item_type = "unknown"

    # Metadata failures should propagate to the GUI, not silently hide errors.
    return {
        "name": item.name,
        "type": item_type,
        "path": item,
        "extension": item.suffix,
        "size": item.stat().st_size if item_type == "file" else None,
    }


def list_items(path: Path) -> list[dict]:
    return [get_item_info(item) for item in path.iterdir()]


def find_files(path: Path, searched_term: str, type_search: str) -> list[dict]:
    searched_term = searched_term.strip().casefold()
    if not searched_term:
        raise ValueError("Search term cannot be empty!")
    mode = type_search.strip().upper()
    if mode == "Q":
        candidates = path.iterdir()
    elif mode == "D":
        # Do not follow symlink/junction directories during traversal.
        candidates = (
            entry
            for folder, dirs, files in os.walk(path, followlinks=False)
            for entry in _walk_entries(folder, dirs, files)
        )
    else:
        raise ValueError("Invalid search mode! Use D or Q.")
    return [get_item_info(item) for item in candidates if searched_term in item.name.casefold()]


def _walk_entries(folder: str, dirs: list[str], files: list[str]):
    """Yield entries, pruning junctions and symlinked directories from traversal."""
    base = Path(folder)
    for name in list(dirs):
        item = base / name
        if item.is_junction() or item.is_symlink():
            dirs.remove(name)
        yield item
    for name in files:
        yield base / name


def select_file(path: Path, desired_item: str) -> Path:
    new_path = path / desired_item
    if not new_path.is_dir():
        raise NotADirectoryError(f"Not a valid directory: {new_path}")
    return new_path


def go_back(path: Path) -> Path:
    """Go up one directory, not browser-style navigation history."""
    return path.parent


def make_file_or_directory(path: Path, create_file_or_directory: str, name: str) -> Path:
    name = validate_filename(name)
    new_path = path / name
    kind = create_file_or_directory.strip().upper()
    if kind == "D":
        new_path.mkdir()
    elif kind == "F":
        new_path.touch(exist_ok=False)
    else:
        raise ValueError("Invalid creation type! Use D or F.")
    return new_path


def rename_file_or_directory(old_path: Path, new_name: str) -> Path:
    new_name = validate_filename(new_name)
    if not item_exists(old_path):
        raise FileNotFoundError(f"Item not found: {old_path}")
    _reject_link(old_path)
    new_path = old_path.parent / new_name
    if new_path == old_path:
        return old_path
    if item_exists(new_path):
        raise FileExistsError(f"Item already exists: {new_path}")
    old_path.rename(new_path)
    return new_path


def move_file_or_directory(old_path: Path, destination_directory: Path) -> Path:
    if not item_exists(old_path):
        raise FileNotFoundError(f"Source doesn't exist: {old_path}")
    _reject_link(old_path)
    if not destination_directory.is_dir():
        raise NotADirectoryError(f"Destination isn't a directory: {destination_directory}")
    if old_path.is_dir() and destination_directory.resolve().is_relative_to(old_path.resolve()):
        raise ValueError("Cannot move a directory into itself!")
    new_path = destination_directory / old_path.name
    if new_path == old_path:
        return old_path
    if item_exists(new_path):
        raise FileExistsError(f"An item with that name already exists: {new_path}")
    shutil.move(old_path, new_path)
    return new_path


def copy_file_or_directory(source_path: Path, destination_directory: Path) -> Path:
    if not item_exists(source_path):
        raise FileNotFoundError(f"Source doesn't exist: {source_path}")
    _reject_link(source_path)
    if not destination_directory.is_dir():
        raise NotADirectoryError(f"Destination isn't a directory: {destination_directory}")
    if source_path.is_dir() and destination_directory.resolve().is_relative_to(source_path.resolve()):
        raise ValueError("Cannot copy a directory into itself!")
    new_path = destination_directory / source_path.name
    if item_exists(new_path):
        raise FileExistsError(f"An item with that name already exists: {new_path}")
    if source_path.is_file():
        # 'xb' creates only if no file already exists; helps avoid overwrites for files.
        with source_path.open("rb") as src, new_path.open("xb") as dst:
            shutil.copyfileobj(src, dst)
        shutil.copystat(source_path, new_path)
    elif source_path.is_dir():
        # Never follow directory symlinks inside a copied tree.
        shutil.copytree(source_path, new_path, symlinks=True)
    else:
        raise ValueError("Source is not a regular file or directory!")
    return new_path


def delete_file_or_directory(target_path: Path) -> bool:
    if not item_exists(target_path):
        raise FileNotFoundError(f"Item doesn't exist: {target_path}")
    _reject_link(target_path)
    send2trash(target_path)
    return True
