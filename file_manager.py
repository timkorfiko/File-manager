from pathlib import Path
import shutil
from send2trash import send2trash
import os

def list_items(path):
    list_of_items = []

    for item in path.iterdir():
        if item.is_junction():
            continue

        list_of_items.append(get_item_info(item))

    return list_of_items

def find_files(path, searched_term, type_search):
    search_result = []
    searched_term = searched_term.strip().casefold()

    if not searched_term:
        raise ValueError("Search term cannot be empty!")

    if type_search == "D":
        result = path.rglob("*")

    elif type_search == "Q":
        result = path.glob("*")

    else:
        raise ValueError("Invalid search mode! Use D or Q.")

    for item in result:
        if item.is_junction():
            continue

        if searched_term in item.name.casefold():
            search_result.append(get_item_info(item))

    return search_result

def select_file(path, desired_item):
    new_path = path / desired_item

    if not new_path.is_dir():
        raise NotADirectoryError(f"Not a valid directory: {new_path}")

    return new_path

def go_back(path):
    return path.parent
def make_file_or_directory(path, create_file_or_directory, name):
    name = validate_filename(name)

    new_path = path / name

    if create_file_or_directory == "D":
        new_path.mkdir()

    elif create_file_or_directory == "F":
        new_path.touch(exist_ok=False)

    else:
        raise ValueError("Invalid creation type!")

    return new_path

def rename_file_or_directory(old_path, new_name):
    new_name = validate_filename(new_name.strip())

    if not new_name:
        raise ValueError("Name cannot be empty!")

    if new_name in (".", "..") or "/" in new_name or "\\" in new_name:
        raise ValueError("Enter a name, not a path!")

    if not item_exists(old_path):
        raise FileNotFoundError(f"Item not found: {old_path}")

    new_path = old_path.parent / new_name

    if new_path == old_path:
        return old_path

    if item_exists(new_path):
        raise FileExistsError(f"Item already exists: {new_path}")

    old_path.rename(new_path)

    return new_path

def move_file_or_directory(old_path, destination_directory):
    if not item_exists(old_path):
        raise FileNotFoundError("Source doesn't exist!")

    if not destination_directory.is_dir():
        raise NotADirectoryError("Destination directory doesn't exist!")

    if (
        old_path.is_dir()
        and destination_directory.resolve().is_relative_to(old_path.resolve())
    ):
        raise ValueError("Cannot move a directory into itself!")

    new_path = destination_directory / old_path.name

    if new_path == old_path:
        return old_path

    if item_exists(new_path):
        raise FileExistsError("An item with that name already exists!")

    shutil.move(old_path, new_path)
    return new_path

def copy_file_or_directory(source_path, destination_directory):
    if not item_exists(source_path):
        raise FileNotFoundError("Source file or directory doesn't exist!")

    if not destination_directory.is_dir():
        raise NotADirectoryError("Destination is not a valid directory!")

    new_destination_path = destination_directory / source_path.name

    if item_exists(new_destination_path):
        raise FileExistsError("An item with that name already exists!")

    if (
        source_path.is_dir()
        and destination_directory.resolve().is_relative_to(source_path.resolve())
    ):
        raise ValueError("Cannot copy a directory into itself!")

    if source_path.is_file():
        shutil.copy2(source_path, new_destination_path)

    elif source_path.is_dir():
        shutil.copytree(source_path, new_destination_path)

    else:
        raise ValueError("Source is not a regular file or directory!")

    return new_destination_path

def delete_file_or_directory(target_path):
    if not item_exists(target_path):
        raise FileNotFoundError("File or directory doesn't exist!")

    send2trash(target_path)

    return True

def handle_errors(error, operation):
    prefix = f"Error while {operation}: "

    if isinstance(error, FileNotFoundError):
        return prefix + "File or directory not found!"

    elif isinstance(error, PermissionError):
        return prefix + "Permission denied! Access to this item is restricted."

    elif isinstance(error, FileExistsError):
        return prefix + "A file or directory with this name already exists!"

    elif isinstance(error, IsADirectoryError):
        return prefix + "Expected a file, but found a directory!"

    elif isinstance(error, NotADirectoryError):
        return prefix + "Expected a directory, but found a file!"

    elif isinstance(error, ValueError):
        return prefix + str(error)

    elif isinstance(error, OSError):
        return prefix + f"Operating system error: {error}"

    else:
        return prefix + f"Unexpected error: {error}"

def get_item_info(item):
    if item.is_dir():
        item_type = "folder"
    elif item.is_file():
        item_type = "file"
    else:
        item_type = "unknown"

    return {
        "name": item.name,
        "type": item_type,
        "path": item,
        "extension": item.suffix,
        "size": item.stat().st_size if item_type == "file" else None
    }

def validate_filename(name):
    name = name.strip()

    if not name:
        raise ValueError("Name cannot be empty!")

    if name in (".", "..") or "/" in name or "\\" in name:
        raise ValueError("Enter a filename, not a path!")

    if os.name == "nt" and os.path.isreserved(name):
        raise ValueError(f"Invalid Windows filename: {name}")

    return name

def item_exists(path):
    try:
        path.lstat()
        return True

    except FileNotFoundError:
        return False

def main():
    current_path = Path.cwd()

    while True:
        print(f"\nCurrent directory: {current_path}")

        command = input(
            "\nLIST ITEMS  [1]\n"
            "FIND FILES  [2]\n"
            "FILE INFO   [3]\n"
            "SELECT FILE [4]\n"
            "GO BACK     [5]\n"
            "MAKE FILE/DIRECTORY [6]\n"
            "RENAME FILE/DIRECTORY [7]\n"
            "MOVE FILE/DIRECTORY [8]\n"
            "COPY FILE/DIRECTORY [9]\n"
            "DELETE FILE/DIRECTORY [10]\n"
            "EXIT        [Q]\n"
            "Select: "
        ).strip().upper()

        if command == "Q":
            print("executing: QUIT...")
            break

        elif command == "1":
            list_items(current_path)

        elif command == "2":
            find_files(current_path)

        elif command == "4":
            current_path = select_file(current_path)

        elif command == "5":
            current_path = go_back(current_path)

        elif command == "6":
            make_file_or_directory(current_path)

        elif command == "7":
            file_name = input("Enter the file or directory to rename: ").strip()

            selected_path = current_path / file_name

            rename_file_or_directory(selected_path)

        elif command == "8":
            source_name = input("File or directory to move: ").strip()
            destination_input = input("Destination directory: ").strip()

            old_path = current_path / source_name
            destination_directory = (current_path / destination_input).resolve()

            move_file_or_directory(old_path, destination_directory)

        elif command == "9":
            source_name = input("File or directory to copy: ").strip()
            destination_input = input("Destination folder: ").strip()

            source_path = current_path / source_name
            destination_directory = Path(destination_input)

            copy_file_or_directory(source_path, destination_directory)

        elif command == "10":
            target_name = input("File or directory to delete: ").strip()
            target_path = current_path / target_name

            result = delete_file_or_directory(target_path)
            print(result)

        else:
            print("Invalid command")

main()
print("EXITED")
