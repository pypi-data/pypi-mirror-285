import logging

from rich.logging import RichHandler

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s: %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.DEBUG,
    handlers=[RichHandler(show_time=False)],
)
