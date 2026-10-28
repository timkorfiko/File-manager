"""Friendly, GUI-displayable exception messages."""

def handle_errors(error: Exception, operation: str) -> str:
    prefix = f"Error while {operation}: "
    if isinstance(error, FileNotFoundError):
        return prefix + f"File or directory not found! {error}"
    if isinstance(error, PermissionError):
        return prefix + f"Permission denied! {error}"
    if isinstance(error, FileExistsError):
        return prefix + f"An item with that name already exists! {error}"
    if isinstance(error, IsADirectoryError):
        return prefix + f"Expected a file, but found a directory! {error}"
    if isinstance(error, NotADirectoryError):
        return prefix + f"Expected a directory, but found a file or invalid path! {error}"
    if isinstance(error, ValueError):
        return prefix + str(error)
    if isinstance(error, OSError):
        return prefix + f"Operating system error: {error}"
    return prefix + f"Unexpected error: {error}"
