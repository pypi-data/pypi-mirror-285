import os

def read_file(filename: str) -> str:
    """Read the contents of a file."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} does not exist.")
    return open(filename).read()

def read_files(files: list[str]) -> list[str]:
    """Read the contents of a list of files."""
    return {f: read_file(f) for f in files}

def list_files(path: str) -> list[str]:
    """List the files and directory in a directory."""
    return [f for f in os.listdir(path) if not f.startswith(".")]

def tree(path: str, depth: int=3) -> str:
    """Get a tree representation of the files and directories in a directory."""
    def _tree(path: str, depth: int, prefix: str = "") -> str:
        if depth < 0:
            return ""
        if not os.path.exists(path):
            return f"{prefix} [Error: Path does not exist]"
        if os.path.isfile(path):
            return f"{prefix} {os.path.basename(path)}"
        try:
            files = sorted([f for f in os.listdir(path) if not f.startswith(".")])
        except PermissionError:
            return f"{prefix} [Error: Permission denied]"
        result = f"{prefix} {os.path.basename(path)}/" if prefix else ""
        for i, f in enumerate(files):
            is_last = (i == len(files) - 1)
            new_prefix = f"{prefix} {'└──' if is_last else '├──'}"
            result += _tree(os.path.join(path, f), depth - 1, new_prefix)
        return result

    if os.path.isfile(path):
        return os.path.basename(path)
    return _tree(path, depth).rstrip()
