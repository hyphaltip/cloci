import logging

# lib/__init__ runs before the other cloci modules call basicConfig, so this
# format applies to every cloci logger (the first basicConfig call wins).
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)
