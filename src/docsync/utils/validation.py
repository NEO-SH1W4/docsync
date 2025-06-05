from pathlib import Path


def validate_path(path: Path, create: bool = False) -> Path:
    """Ensure a directory path exists, optionally creating it."""
    p = Path(path)
    if p.exists():
        if not p.is_dir():
            raise ValueError(f"Not a directory: {p}")
    else:
        if create:
            p.mkdir(parents=True, exist_ok=True)
        else:
            raise FileNotFoundError(f"Path does not exist: {p}")
    return p

__all__ = ["validate_path"]
