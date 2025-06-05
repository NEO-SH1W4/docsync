import logging
from rich.logging import RichHandler


def setup_logger(name: str) -> logging.Logger:
    """Create a Rich-configured logger."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler()]
    )
    return logging.getLogger(name)
